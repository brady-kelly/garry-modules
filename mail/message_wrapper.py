from email.message import EmailMessage
from email.parser import BytesHeaderParser
from email.policy import default
from email.utils import parseaddr
import imaplib
import re
import time

class MessageWrapper:
    
    def __init__(self, msg: EmailMessage, size: int, uid: bytes, uid_validity: int, flags: list[str], internal_date: str | None, raw_content: bytes):
        self.msg = msg
        self.sender = msg['From']
        self.subject = msg['Subject']
        self.date = msg['Date']   
        self.size = size
        self.uid = uid
        self.uid_validity = uid_validity
        self.flags = flags
        self.internal_date = internal_date,
        self.raw_content = raw_content=raw_content
        
    def print(self):
        print(f"{self.date[:31]:<31} | {self.size:<10} | {self.sender[:40]:<40} | {self.subject[:40]}")
            
    
    @classmethod                
    def print_heading(cls, count):
        print(f"Found {count} emails in Inbox.\n")        
        print(f"{'Date':<31} | {'Size (KB)':<10} | {'From':<40} | {'Subject'}")
        print("-" * 130)          

    @classmethod
    def from_response_data(cls, uid, uid_validity, response_data):
        envelope_str = ""
        raw_bytes = b""        
        
        for item in response_data:
            if isinstance(item, tuple) and len(item) >= 2:
                # item[0] holds the metadata (e.g., b'1 (RFC822.SIZE 4500 FLAGS (...) INTERNALDATE "...")')
                if isinstance(item[0], bytes):
                    envelope_str = item[0].decode('utf-8', errors='ignore')
                else:
                    envelope_str = str(item[0])
                
                # item[1] holds the raw RFC822 body bytes
                if isinstance(item[1], bytes):
                    raw_bytes = item[1]
                    break
                    
        if not raw_bytes:
            for item in response_data:
                if isinstance(item, bytes):
                    raw_bytes = item
                    break

        # Clean and direct: No more hassle guessing bracket sizes
        size_match = re.search(r'RFC822\.SIZE\s+(\d+)', envelope_str)
        email_size = int(size_match.group(1)) if size_match else 0
        
        msg: EmailMessage = BytesHeaderParser(policy=default).parsebytes(raw_bytes if raw_bytes else b"") 
        
        flags_match = re.search(r'FLAGS\s+\(([^)]*)\)', envelope_str)
        email_flags: list[str] = flags_match.group(1).split() if flags_match else []
        
        date_match = re.search(r'INTERNALDATE\s+"([^"]+)"', envelope_str)
        internal_date = date_match.group(1) if date_match else None
                    
        return cls(
            msg=msg,
            size=email_size, 
            uid=uid,                 
            uid_validity=uid_validity,
            flags=email_flags,
            internal_date=internal_date,
            raw_content=raw_bytes
        )
