from email.parser import BytesHeaderParser
from email.utils import parseaddr
import re

class MailInfo:
    
    def __init__(self, date, subject, sender, size, uid, uid_validity, flags):
        self.date = date
        self.subject = subject
        self.sender = sender
        self.size = size
        self.uid = uid
        self.uid_validity = uid_validity
        self.flags = flags
        
    def print(self):
        print(f"{self.date[:31]:<31} | {self.size:<10} | {self.sender[:30]:<30} | {self.subject[:40]}")
            
    
    @classmethod                
    def print_heading(cls, count):
        print(f"Found {count} emails in Inbox.\n")        
        print(f"{'Date':<31} | {'Size (KB)':<10} | {'From':<30} | {'Subject'}")
        print("-" * 110)          
        
    @classmethod
    def from_response_data(cls, uid, uid_validity, response_data):
        raw_headers = b""
        size_bytes = 0        
        
        for part in response_data:
            if isinstance(part, tuple):
                if b"HEADER" in part[0]:
                    raw_headers = part[1]
                
                meta_str = part[0].decode(errors='ignore')
                if "SIZE" in meta_str:
                    # Matches 'RFC822.SIZE 12345' and extracts the digits group
                    size_match = re.search(r'SIZE\s+(\d+)', meta_str)
                    if size_match:
                        size_bytes = int(size_match.group(1))
                        
                # EXTRACT FLAGS: Capture text inside FLAGS (...)
                if "FLAGS" in meta_str:
                    # Captures flags like '\Seen \Flagged' inside parentheses
                    flags_match = re.search(r'FLAGS\s+\(([^)]*)\)', meta_str)
                    if flags_match:
                        flags_str = flags_match.group(1).strip()                        
                            
        headers = BytesHeaderParser().parsebytes(raw_headers)
        
        date_val = headers.get("Date", "N/A").strip()
        subject_val = headers.get("Subject", "(No Subject)").strip()
        
        from_raw = headers.get("From", "N/A")
        _, from_email = parseaddr(from_raw)
        
        size_kb = round(size_bytes / 1024, 2)
        
        msg_id = uid.decode(errors='ignore')      
        
        return cls(
            date=date_val, 
            subject=subject_val, 
            sender=from_email, 
            size=size_kb, 
            uid=uid,                 
            uid_validity=uid_validity,
            flags=flags_str
        )
     