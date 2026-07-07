import imaplib
from email.parser import BytesHeaderParser
from email.utils import parseaddr
from mail_result import MailResult
from mail_message import MailMessage
from message_wrapper import MessageWrapper

url_map = {
    "gmail": "imap.gmail.com",
    "hotmail": "//office365.com"
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
        self.mail = imaplib.IMAP4_SSL(self.url, 993)
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
            return MailResult(False, f"Couldn't connect to {self.url}")
        
        status, select_data = self.mail.select(folder, readonly=True)    
        if status != "OK":
            return MailResult(False, f"Failed to select folder {folder}.")         
        
        status, search_data = self.mail.uid("search", "ALL")
        if status != "OK":
            return MailResult(False, "Failed to search emails.")
        
        uid_validity = self.get_uid_validity(select_data)
    
        uid_bytes_list = search_data[0].split()
        wrappers = []
        errors = []
        print(f"Search found {len(uid_bytes_list)} Ids")
        for uid in uid_bytes_list:
            try:            
                status, response_data = self.mail.fetch(
                    uid, "(FLAGS BODY.PEEK[HEADER] RFC822.SIZE)"
                )                
                if status == 'OK' and response_data:
                    info = MessageWrapper.from_response_data(uid, uid_validity, response_data)
                    wrappers.append(info)
                else:
                    errors.append(f"Bad response for email ID {uid.decode()}: {status}")
                
            except Exception as e:                
                errors.append(f"Error fetching metadata for email ID {uid.decode()}: {e}")                
        
        return MailResult(True, f"Fetch headers for folder {folder}.", wrappers)  
                        
    # def fetch_message(self, info):
    #     self.connect()
    #     if not isinstance(self.mail, imaplib.IMAP4_SSL):
    #         print(f"Couldn't connect to {self.url}")
    #         return None
        
    #     res, msg_data = self.mail.uid("fetch", info.uid, "(RFC822)")
    #     if res != "OK":
    #         return None
        
    #     raw_email = b""
        
    #     # Safely find the tuple containing the email data bytes
    #     for part in msg_data:
    #         if isinstance(part, tuple):
    #             raw_email = part[1]
    #             break

    #     if not raw_email:
    #         print(f"Failed to extract raw email content for UID {info.uid}")
    #         return None

    #     # Return your MailMessage instance combining your metadata and the body bytes
    #     return MailMessage(info=info, raw_body=raw_email)        
    
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
    
    
