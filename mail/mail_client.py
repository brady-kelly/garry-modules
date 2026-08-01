import datetime
import imaplib
from typing import Iterable, cast
from imapclient import IMAPClient
from email.parser import BytesHeaderParser
from email.utils import parseaddr
import os
import msal
from auth import get_msal_token_device_flow, get_msal_token_interactive
from mail_account import MailAccount
from task_result import TaskResult
from message_wrapper import MessageWrapper

url_map = {
    "gmail": "imap.gmail.com",
    "hotmail": "office365.com",
    "outlook": "outlook.office365.com"
}

class MailClient:
    
    def __init__(self, account):
        self.account: MailAccount = account    
        self.url: str | None = None
        self.mail: IMAPClient | None = None
        self._is_logged_in = False
        
    def connect(self):
        if self.mail and self._is_logged_in:
            try:
                self.mail.capabilities()
                return  
            except Exception:
                self._is_logged_in = False
                try:
                    self.mail.logout()
                except Exception:
                    pass   

        atkey = self.account.account_type.lower()
        if not atkey in url_map:
            print(f"No url defined for account type: {atkey}")
            return
        self.url = url_map[atkey]
        print(f"Connecting to host: {self.url}")
        self.mail = IMAPClient(self.url, ssl=True)

        if not self.account.username: #or not self.account.password:
            raise ValueError("Missing IMAP username or password configuration.")

        if atkey == "outlook":
            client_id = os.environ["CLIENT_ID"]
            tenant_id = os.environ["TENANT_ID"]

            AUTHORITY = f"https://login.microsoftonline.com/{tenant_id}"
            SCOPES = [
                "https://outlook.office.com/IMAP.AccessAsUser.All",
                "https://outlook.office.com/SMTP.Send"
            ]

            app = msal.PublicClientApplication(client_id, authority=AUTHORITY)        
            token_result = get_msal_token_interactive(app, SCOPES, self.account.username)            
            access_token = token_result["access_token"]
            
            if "access_token" not in token_result:
                raise Exception(f"Login failed: {token_result.get('error_description')}")       
            
            self.mail.oauth2_login(self.account.username, access_token)             
        else:
            if not self.account.username or not self.account.password:
                raise ValueError("Missing IMAP username or password configuration.")
            self.mail.login(self.account.username, self.account.password)  
            
        self._is_logged_in = True       
        
    def parse_info(self, data):
        # IMAPClient normalizes key responses to bytes keys
        size = cast(int, data.get(b"RFC822.SIZE", 0))
        
        # This natively returns a datetime.datetime object
        date = cast(datetime.datetime | None, data.get(b"INTERNALDATE"))
        
        raw_flags = data.get(b"FLAGS") or []                
        if not isinstance(raw_flags, Iterable) or isinstance(raw_flags, (bytes, str)):
            raw_flags = [raw_flags]      
                                                
        # IMAPClient returns flags as a tuple/list of strings or bytes depending on configuration
        flags = [
            f.decode("utf-8") if isinstance(f, bytes) else str(f) 
            for f in cast(Iterable, raw_flags)
        ]  
        
        return (size, date, flags)          
                                
    def fetch_headers(self, folder="Inbox", limit=20) -> TaskResult:    
        try:
            self.connect()
        # IMAPClient raises its own exceptions or standard wrapper errors
        except Exception as conn_err:
            self._is_logged_in = False
            return TaskResult(False, f"Failed to establish/verify connection: {str(conn_err)}")
                
        if not self.mail:
            return TaskResult(False, f"Not connected to {self.url}")        
        
        try:
            # IMAPClient returns a dictionary with string keys, not bytes
            select_data = self.mail.select_folder(folder, readonly=True)    
        except Exception as select_err:
            return TaskResult(False, f"Failed to select folder {folder}: {str(select_err)}.")         
                    
        try:
            uids = self.mail.search("ALL")
        except Exception as search_err:
            return TaskResult(False, f"Failed to search emails: {str(search_err)}.")
        
        if not uids:
            return TaskResult(True, "No messages found in folder.", [])           
                        
        # Look up using string key 'UIDVALIDITY' instead of byte key b'UIDVALIDITY'
        uid_validity = select_data.get('UIDVALIDITY', 0)

        wrappers = []
        errors = []
        slice_limit = limit if limit is not None else len(uids)
        batch_uids = uids[:slice_limit]
        
        try:
            # Note: Changed 'BODY.PEEK[HEADER]' to 'RFC822.HEADER' for clean mapping
            response_data = self.mail.fetch(batch_uids, ["RFC822.SIZE", "FLAGS", "INTERNALDATE", "RFC822.HEADER"])
        except Exception as net_err:
            self._is_logged_in = False  
            errors.append(f"Network drop or server failure during bulk fetch batch: {str(net_err)}")
            response_data = {}

        for uid in batch_uids:
            uid_str = str(uid)
            
            if uid not in response_data:
                errors.append(f"Server omitted or failed to return data for UID {uid_str}.")
                continue
                
            try:
                data = response_data[uid]
                
                email_size, internal_date, email_flags = self.parse_info(data)   
                
                # IMAPClient returns requested headers as bytes under the matching normalized key
                raw_header_bytes = cast(bytes, data.get(b"RFC822.HEADER", b""))
                
                wrapper = MessageWrapper.from_imap_client_data(
                    uid=uid, 
                    uid_validity=uid_validity, 
                    size=email_size,
                    flags=email_flags,
                    internal_date=internal_date,  # This will be a datetime object now
                    raw_headers=raw_header_bytes
                )
                wrappers.append(wrapper)
                
            except Exception as parse_err:
                errors.append(f"Failed to process/parse data details for UID {uid_str}: {str(parse_err)}")
                continue
            
        if wrappers:
            return TaskResult(True, f"Processed {len(wrappers)} headers with {len(errors)} errors.", wrappers)
            
        if errors:
            return TaskResult(False, f"Failed to get headers. Errors: {'; '.join(errors)}")
            
        return TaskResult(True, "No headers to process.", [])
  
    def fetch_message(self, wrapper: MessageWrapper) -> TaskResult:        
        try:
            self.connect()
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError) as conn_err:
            self._is_logged_in = False
            return TaskResult(False, f"Failed to establish/verify connection: {str(conn_err)}")
                
        if not self.mail:
            return TaskResult(False, f"Not connected to {self.url}")  
                
        try:
            response_data = self.mail.fetch([wrapper.uid], ["RFC822.SIZE", "FLAGS", "INTERNALDATE", "RFC822"])
        except Exception as net_err:
            self._is_logged_in = False  
            return TaskResult(False, f"Network dropped or command failed during fetch: {str(net_err)}")
                
        if response_data and wrapper.uid in response_data:
            try:
                data = response_data[wrapper.uid]
                email_size, internal_date, email_flags = self.parse_info(data)    
                raw_bytes = cast(bytes, data.get(b"RFC822", b""))
                
                wrapper = MessageWrapper.from_imap_client_data(
                    uid=wrapper.uid,
                    uid_validity=wrapper.uid_validity,
                    size=email_size,
                    flags=email_flags,
                    internal_date=internal_date,
                    raw_headers=raw_bytes 
                )
                wrapper.raw_content = raw_bytes
                
            except Exception as parse_err:
                return TaskResult(False, f"Failed to unpack message data details for UID {wrapper.uid}: {str(parse_err)}")
            
            return TaskResult(True, f"Fetched message for id {wrapper.uid}.", [wrapper])  
        
        return TaskResult(False, f"Server returned empty data payload for UID {wrapper.uid}.")
                
    def append_message(self, folder, wrapper: MessageWrapper):              
        try:
            self.connect()
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError) as conn_err:
            self._is_logged_in = False
            return TaskResult(False, f"Failed to establish/verify connection: {str(conn_err)}")
                
        if not self.mail:
            return TaskResult(False, f"Not connected to {self.url}")  
        
        msg_time = wrapper.internal_date if wrapper.internal_date else datetime.datetime.now()

        try:
            self.mail.append(
                folder=folder, 
                msg=wrapper.raw_content,   # Corrected keyword
                flags=wrapper.flags, 
                msg_time=msg_time
            )    
                            
        except Exception as err:
            if "abort" in str(err).lower() or "connection" in str(err).lower():
                self._is_logged_in = False  
                return TaskResult(False, f"Network dropped during append: {str(err)}")                
            return TaskResult(False, f"Server rejected append (possible missing folder): {str(err)}")

        return TaskResult(True, f"Successfully appended message to {folder}.")  
      

