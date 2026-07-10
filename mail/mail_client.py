import datetime
import imaplib
from email.parser import BytesHeaderParser
from email.utils import parseaddr
import os

import msal
from auth import get_msal_token_device_flow, get_msal_token_interactive
from task_result import TaskResult
from message_wrapper import MessageWrapper

url_map = {
    "gmail": "imap.gmail.com",
    "hotmail": "office365.com",
    "outlook": "outlook.office365.com"
}

class MailClient:
    
    def __init__(self, account):
        self.account = account    
        self.mail = None
        self._is_logged_in = False
        
    def connect(self):
        if self.mail and self._is_logged_in:
            try:
                status, _ = self.mail.noop()
                if status == 'OK':
                    return  
            except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError):
                self._is_logged_in = False
                try:
                    self.mail.logout()
                except Exception:
                    pass  # Ignore errors on an already dead connection       

        atkey = self.account.account_type.lower()
        if not atkey in url_map:
            print(f"No url defined for account type: {atkey}")
            return
        self.url = url_map[atkey]
        print(f"Connecting to host: {self.url}")
        self.mail = imaplib.IMAP4_SSL(self.url)
        if atkey == "outlook":
            client_id = os.environ["CLIENT_ID"]
            tenant_id = os.environ["TENANT_ID"]

            AUTHORITY = f"https://login.microsoftonline.com/{tenant_id}"
            SCOPES = [
                "https://outlook.office.com/IMAP.AccessAsUser.All",
                "https://outlook.office.com/SMTP.Send"
            ]

            app = msal.PublicClientApplication(client_id, authority=AUTHORITY)        

            #token_result = get_msal_token_device_flow(app, SCOPES)
            token_result = get_msal_token_interactive(app, SCOPES, self.account.username)            
            access_token = token_result["access_token"]
            
            if "access_token" not in token_result:
                raise Exception(f"Login failed: {token_result.get('error_description')}")            
            
            auth_string = f"user={self.account.username}\x01auth=Bearer {access_token}\x01\x01".encode('utf-8')    
            self.mail.authenticate("XOAUTH2", lambda x: auth_string)
        else:
            self.mail.login(self.account.username, self.account.password)  
            
        self._is_logged_in = True  
        
    def get_uid_validity(self, select_data):
        import re
        uid_validity = None
        for item in select_data:
            # Ensure item is a valid bytes object before checking contents
            if isinstance(item, bytes) and b'UIDVALIDITY' in item:
                match = re.search(r'\d+', item.decode('utf-8'))
                if match:
                    uid_validity = int(match.group())
                    break      
        return uid_validity      
                                
    def fetch_headers(self, folder = "Inbox", limit=20) -> TaskResult:    
        try:
            self.connect()
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError) as conn_err:
            self._is_logged_in = False
            return TaskResult(False, f"Failed to establish/verify connection: {str(conn_err)}")
                
        if not self.mail:
            return TaskResult(False, f"Not connected to {self.url}")        
        
        status, select_data = self.mail.select(folder, readonly=True)    
        if status != "OK":
            return TaskResult(False, f"Failed to select folder {folder}.")         
        
        status, search_data = self.mail.uid("search", "ALL")
        if status != "OK":
            return TaskResult(False, "Failed to search emails.")
        
        # FIX 1: Explicitly check for missing or empty search data arrays
        if not search_data or not search_data[0]:
            return TaskResult(True, "No messages found in folder.", [])        
        
        uid_validity = self.get_uid_validity(select_data) or 0
    
        uid_bytes_list = search_data[0].split()
        wrappers = []
        errors = []
        slice_limit = limit if limit is not None else len(uid_bytes_list)
        for uid in uid_bytes_list[:slice_limit]:
            
            uid_str = uid.decode('utf-8') if isinstance(uid, bytes) else str(uid)
            
            try:
                fetch_status, response_data = self.mail.uid("fetch", uid_str, "(RFC822.SIZE FLAGS INTERNALDATE BODY.PEEK[HEADER])")
            except (imaplib.IMAP4.abort, OSError) as net_err:
                self._is_logged_in = False  # Connection broke mid-loop, must flag it
                errors.append(f"Network dropped while fetching UID {uid_str}: {str(net_err)}")
                break  # Break out of the loop because the connection is dead
            except imaplib.IMAP4.error as cmd_err:
                errors.append(f"Server rejected fetch for UID {uid_str}: {str(cmd_err)}")
                continue  # Skip this specific message and try the next one
                                
            if fetch_status != 'OK' or not response_data:
                errors.append(f"Server returned status {fetch_status} for UID {uid_str}.")
                continue
            
            try:
                wrapper = MessageWrapper.from_response_data(
                    uid=uid, 
                    uid_validity=uid_validity, 
                    response_data=response_data
                )
                wrappers.append(wrapper)
            except Exception as parse_err:
                errors.append(f"Failed to parse data for UID {uid_str}: {str(parse_err)}")
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
            status, response_data = self.mail.uid("fetch", wrapper.uid.decode('utf-8') , "(RFC822.SIZE FLAGS INTERNALDATE RFC822)")                            
        except (imaplib.IMAP4.abort, OSError) as net_err:
            self._is_logged_in = False  # Connection broke mid-request
            return TaskResult(False, f"Network dropped during fetch: {str(net_err)}")
        except imaplib.IMAP4.error as cmd_err:
            # Severe protocol violation or server-side failure (e.g. UID does not exist anymore)
            return TaskResult(False, f"IMAP server rejected the fetch command: {str(cmd_err)}")
        
        if status == 'OK' and response_data:
            wrapper = MessageWrapper.from_response_data(wrapper.uid, wrapper.uid_validity, response_data)
            return TaskResult(True, f"Fetched message for id {wrapper.uid.decode('utf-8')}.", [wrapper])  
        
        return TaskResult(False, f"Server returned non-OK status ({status}) or empty data.")   

            
    def append_message(self, folder, wrapper: MessageWrapper):              
        try:
            self.connect()
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError) as conn_err:
            self._is_logged_in = False
            return TaskResult(False, f"Failed to establish/verify connection: {str(conn_err)}")
                
        if not self.mail:
            return TaskResult(False, f"Not connected to {self.url}")
        
        # FIXED: Safely format flags to be wrapped in parentheses as IMAP expects.
        # Example: ['\\Seen', '\\Flagged'] -> "(\\Seen \\Flagged)"
        formatted_flags = f"({' '.join(wrapper.flags)})" if wrapper.flags else "()"
        
        if wrapper.internal_date:
            formatted_date = f'"{wrapper.internal_date}"'
        else:
            # Fallback to the current system time formatted perfectly for IMAP
            now = datetime.datetime.now()
            formatted_date = now.strftime('"%d-%b-%Y %H:%M:%S +0000"')        
        
        try:            
            status, response = self.mail.append(
                f'"{folder}"', 
                formatted_flags, 
                formatted_date, 
                wrapper.raw_content
            )    
                            
        except (imaplib.IMAP4.abort, OSError) as net_err:
            self._is_logged_in = False  # Network drop, must log back in on next call
            return TaskResult(False, f"Network dropped during append: {str(net_err)}")
        except imaplib.IMAP4.error as cmd_err:
            # Catches critical issues like missing target folders or bad flag syntax
            return TaskResult(False, f"Server rejected append (possible missing folder): {str(cmd_err)}")

        if status == 'OK':
            return TaskResult(True, f"Successfully appended message to {folder}.")            
        return TaskResult(False, f"Server rejected append with status {status}: {str(response)}")
      

