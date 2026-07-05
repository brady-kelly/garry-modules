import imaplib
from email.parser import BytesHeaderParser
from email.utils import parseaddr
from mail_info import MailInfo

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
                
    def fetch_headers(self):
        self.connect()
        if not isinstance(self.mail, imaplib.IMAP4_SSL):
            print(f"Couldn't connect to {self.url}")
            return []
        
        status, select_data = self.mail.select("inbox", readonly=True)    
        if status != "OK":
            print("Failed to select inbox.")
            return []
        
        # Extract the integer UIDVALIDITY value
        import re
        uid_validity = None
        for item in select_data:
            # Ensure item is a valid bytes object before checking contents
            if isinstance(item, bytes) and b'UIDVALIDITY' in item:
                match = re.search(r'\d+', item.decode('utf-8'))
                if match:
                    uid_validity = int(match.group())
                    break          
        
        status, search_data = self.mail.uid("search", "ALL")
        if status != "OK":
                print("Failed to search emails.")
                return []
    
        uid_bytes_list = search_data[0].split()
        metadatas = []
        for e_id in uid_bytes_list:
            try:
            
                status, response_data = self.mail.fetch(
                    e_id, "(BODY.PEEK[HEADER.FIELDS (DATE FROM SUBJECT)] RFC822.SIZE)"
                )                
                if status != "OK":
                    continue  
        
                info = MailInfo.from_response_data(e_id, uid_validity, response_data)
                metadatas.append(info)
                
            except Exception as e:
                print(f"CRASH DETECTED. e_id is actually: {repr(e_id)}")
                print(f"The original error that triggered the except block was: {e}")
                
                print(f"Error fetching metadata for email ID {e_id.decode()}: {e}")                
        
        return metadatas
                        

        self.connect()
        if not self.mail:
            print(f"Could not connect to: {self.url}")
            return
        # Open the Inbox in Read-Only mode to protect read/unread status
        self.mail.select("inbox", readonly=True)
        
        # 2. Search for all emails
        status, data = self.mail.search(None, "ALL")
        if status != "OK":
            print("Failed to search emails.")
            return
            
        email_ids = data[0].split()
        print(f"Found {len(email_ids)} emails in Inbox.\n")
        self.print_meta_heading()
        
            # 3. Fetch header fields and size for each email
        for e_id in email_ids:
            try:
                # We explicitly request only the target headers and the message file size
                status, response_data = self.mail.fetch(
                    e_id, "(BODY.PEEK[HEADER.FIELDS (DATE FROM SUBJECT)] RFC822.SIZE)"
                )
                
                if status != "OK":
                    continue

                raw_headers = b""
                size_bytes = 0            
                
            except Exception as e:
                pass