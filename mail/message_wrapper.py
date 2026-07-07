from email.message import EmailMessage
from email.parser import BytesHeaderParser
from email.policy import default
from email.utils import parseaddr
import re

class MessageWrapper:
    
    def __init__(self, msg: EmailMessage, size: int, uid: bytes, uid_validity: int, flags: list[str]):
        self.msg = msg
        self.sender = msg['From']
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
        envelope_str = ""
        raw_bytes = b""        
        
        # Safely locate the header data without strict unpacking
        for item in response_data:
            if isinstance(item, tuple):
                # Safe way to handle tuples of any length (2, 3, or more items)
                if len(item) >= 2:
                    # The first item is almost always the metadata string
                    envelope_str = item[0].decode('utf-8', errors='ignore') if isinstance(item[0], bytes) else str(item[0])
                    # The second item contains the actual email text/headers
                    raw_bytes = item[1]
                    break
                    
        # If we didn't extract any bytes, look for single-item byte buffers
        if not raw_bytes:
            for item in response_data:
                if isinstance(item, bytes) and b"HEADER" in item:
                    raw_bytes = item
                    break

        size_match = re.search(r'RFC822\.SIZE\s+(\d+)', envelope_str)
        email_size = int(size_match.group(1)) if size_match else 0   
        
        msg: EmailMessage = BytesHeaderParser(policy=default).parsebytes(raw_bytes if raw_bytes else b"") 
        
        flags_match = re.search(r'FLAGS\s+\(([^)]*)\)', envelope_str)
        # This creates a list of strings, e.g., ['\\Seen', '\\Flagged']
        email_flags: list[str] = flags_match.group(1).split() if flags_match else []
                    
        return cls(
            msg=msg,
            size=email_size, 
            uid=uid,                 
            uid_validity=uid_validity,
            flags=email_flags
        )