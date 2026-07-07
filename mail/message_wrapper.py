from email.parser import BytesHeaderParser
from email.utils import parseaddr
import re

class MessageWrapper:
    
    def __init__(self, msg, size, uid, uid_validity):
        self.msg = msg
        self.sender, = msg['From']
        self.subject = msg['Subject']
        self.date = msg['Date']   
        self.size = size
        self.uid = uid
        self.uid_validity = uid_validity
        
    def print(self):
        print(f"{self.date[:31]:<31} | {self.size:<10} | {self.sender[:30]:<30} | {self.subject[:40]}")
            
    
    @classmethod                
    def print_heading(cls, count):
        print(f"Found {count} emails in Inbox.\n")        
        print(f"{'Date':<31} | {'Size (KB)':<10} | {'From':<30} | {'Subject'}")
        print("-" * 110)          
        
    @classmethod
    def from_response_data(cls, uid, uid_validity, response_data):
        envelope, raw_bytes = response_data[0]      
        
        size_match = re.search(r'RFC822\.SIZE\s+(\d+)', envelope.decode('utf-8', errors='ignore'))
        email_size = int(size_match.group(1)) if size_match else 0   
                                      
        msg = BytesHeaderParser().parsebytes(raw_bytes) 
        
        return cls(
            msg=msg,
            size=email_size, 
            uid=uid,                 
            uid_validity=uid_validity
        )
     