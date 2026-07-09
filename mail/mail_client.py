import imaplib
from email.parser import BytesHeaderParser
from email.utils import parseaddr
import os

import msal
from mail_operation_result import MailOperationResult
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
        
    def connect(self):
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
            temp_folder = os.environ["TEMP_FOLDER"]

            AUTHORITY = f"https://login.microsoftonline.com/{tenant_id}"
            SCOPES = [
                "https://outlook.office.com/IMAP.AccessAsUser.All",
                "https://outlook.office.com/SMTP.Send"
            ]

            app = msal.PublicClientApplication(client_id, authority=AUTHORITY)
            
            # flow = app.initiate_device_flow(scopes=SCOPES)
            # if "user_code" not in flow:
            #     raise Exception("Could not initiate authentication flow.")
            # print(flow["message"]) 
            # token_result = app.acquire_token_by_device_flow(flow)
            # if "access_token" not in token_result:
            #     raise Exception(f"Login failed: {token_result.get('error_description')}")
            
            # This pops open a local browser tab pre-filled with your email address
            token_result = app.acquire_token_interactive(
                scopes=SCOPES,
                login_hint=self.account.username
            )
            
            access_token = token_result["access_token"]
            
            if "access_token" not in token_result:
                raise Exception(f"Login failed: {token_result.get('error_description')}")            
            
            auth_string = f"user={self.account.username}\x01auth=Bearer {access_token}\x01\x01".encode('utf-8')    
            self.mail.authenticate("XOAUTH2", lambda x: auth_string)
        else:
            self.mail.login(self.account.username, self.account.password)    
        
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
                                
    def fetch_headers(self, folder = "inbox"):
        self.connect()
        if not isinstance(self.mail, imaplib.IMAP4_SSL):
            return MailOperationResult(False, f"Couldn't connect to {self.url}")
        
        status, select_data = self.mail.select(folder, readonly=True)    
        if status != "OK":
            return MailOperationResult(False, f"Failed to select folder {folder}.")         
        
        status, search_data = self.mail.uid("search", "ALL")
        if status != "OK":
            return MailOperationResult(False, "Failed to search emails.")
        
        uid_validity = self.get_uid_validity(select_data) or 0
    
        uid_bytes_list = search_data[0].split()
        wrappers = []
        errors = []
        for uid in uid_bytes_list[:20]:
            try:            
                status, response_data = self.mail.uid("fetch", uid, "(FLAGS BODY.PEEK[HEADER] RFC822.SIZE INTERNALDATE)")                
                if status == 'OK' and response_data:
                    info = MessageWrapper.from_response_data(uid, uid_validity, response_data)
                    wrappers.append(info)
                else:
                    errors.append(f"Bad response for email ID {uid.decode()}: {status}")
                
            except Exception as e:                
                errors.append(f"Error fetching metadata for email ID {uid.decode()}: {e}")                
        
        if len(errors) > 0:
            return MailOperationResult(False, f"{len(errors)} errors fetching headers for folder {folder}: ", wrappers, errors)  
        else:
            return MailOperationResult(True, f"Fetch headers for folder {folder}.", wrappers)  
                        
    def fetch_message(self, wrapper: MessageWrapper) -> MailOperationResult:
        self.connect()
        if not isinstance(self.mail, imaplib.IMAP4_SSL):
            return MailOperationResult(False, f"Couldn't connect to {self.url}")
                
        try:            
            status, response_data = self.mail.uid("fetch", wrapper.uid.decode('utf-8') , "(RFC822 FLAGS INTERNALDATE)")                
            if status == 'OK' and response_data:
                wrapper = MessageWrapper.from_response_data(wrapper.uid, wrapper.uid_validity, response_data)
                return MailOperationResult(True, f"Fetched message for id {wrapper.uid}.", [wrapper])  
            else:
                return MailOperationResult(False, f"Failed to fetch message for id {wrapper.uid}.")  
            
        except Exception as e:   
            return MailOperationResult(False, f"Error fetching metadata for email ID {wrapper.uid}: {e}")             
        
    
    def append_message(self, folder, wrapper: MessageWrapper):
        self.connect()
        if not isinstance(self.mail, imaplib.IMAP4_SSL):
            return MailOperationResult(False, f"Couldn't connect to {self.url}")
        
        formatted_flags = " ".join(wrapper.flags) if wrapper.flags else None
        
        self.mail.append(
            f'"{folder}"', 
            " ".join(wrapper.flags),  # e.g., "\\Seen \\Flagged"
            str(wrapper.internal_date), 
            wrapper.raw_content
)                
    
    # def append_message(self, folder_name: str, message: MailMessage) -> bool:
    #     """
    #     Appends a MailMessage object directly to the specified folder.
    #     Returns True if successful, False otherwise.
    #     """
    #     self.connect()
    #     if not isinstance(self.mail, imaplib.IMAP4_SSL):
    #         print(f"Couldn't connect to {self.url} to append message.")
    #         return False

    #     try:
    #         # 1. Extract the raw bytes from your MailMessage container
    #         # Assuming your object maps raw bytes to message.raw_body
    #         raw_email = message.raw_body

    #         if not raw_email:
    #             print(f"Cannot append empty message data (UID: {message.info.uid.decode(errors='ignore')}).")
    #             return False

    #         # 2. Append the raw email data directly to the target folder
    #         # We use None for flags and internal date to let the server auto-assign them
    #         append_res, _ = self.mail.append(folder_name, "", "", raw_email)
    
# # Pass it directly to append by joining the list items with a space
# dest_mail.append(
#     f'"{DEST_FOLDER}"', 
#     " ".join(email_flags),  # e.g., "\\Seen \\Flagged"
#     internal_date, 
#     raw_email_bytes
# )    
    
    
            
    #         # 3. Handle and report tracking success
    #         uid_str = message.info.uid.decode(errors='ignore')
    #         if append_res == "OK":
    #             print(f"Successfully transferred email UID {uid_str} to folder '{folder_name}'.")
    #             return True
    #         else:
    #             print(f"Failed to append email UID {uid_str} to folder '{folder_name}'. Response: {append_res}")
    #             return False

    #     except Exception as e:
    #         uid_str = message.info.uid.decode(errors='ignore') if message and message.info else "Unknown"
    #         print(f"Exception raised while trying to append email UID {uid_str}: {e}")
    #         return False
