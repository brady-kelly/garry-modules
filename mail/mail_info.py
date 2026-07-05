from email.parser import BytesHeaderParser
from email.utils import parseaddr


class MailInfo:
    
    def __init__(self, date, subject, sender, size, uid, uid_validity):
        self.date = date
        self.subject = subject
        self.sender = sender
        self.size = size
        self.uid = uid
        self.uid_validity = uid_validity
        
    def print(self):
        # Truncate values to keep the terminal layout clean
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
        
        # Parse the mixed response tuple data from the server
        for part in response_data:
            if isinstance(part, tuple):
                # Ensure we safely read byte fields for the header marker
                if b"HEADER" in part[0]:
                    raw_headers = part[1]
                
                # Check the fetch metadata string to extract the exact file size
                meta_str = part[0].decode(errors='ignore')
                if "SIZE" in meta_str:
                    # Look explicitly for the number that immediately follows "SIZE"
                    import re
                    # Matches 'RFC822.SIZE 12345' and extracts the digits group
                    size_match = re.search(r'SIZE\s+(\d+)', meta_str)
                    if size_match:
                        size_bytes = int(size_match.group(1))
                            
        # Format and clean up the parsed information
        headers = BytesHeaderParser().parsebytes(raw_headers)
        
        # Clean up headers (handles empty entries smoothly)
        date_val = headers.get("Date", "N/A").strip()
        subject_val = headers.get("Subject", "(No Subject)").strip()
        
        # Parse the sender address to isolate the raw email string
        from_raw = headers.get("From", "N/A")
        _, from_email = parseaddr(from_raw)
        
        size_kb = round(size_bytes / 1024, 2)
        
        # Safe decode for tracking labels
        msg_id = uid.decode(errors='ignore')      
        
        # Pass all 7 required arguments to your updated __init__ structure
        return cls(
            date=date_val, 
            subject=subject_val, 
            sender=from_email, 
            size=size_kb, 
            uid=uid,                 # Passes the raw UID bytes
            uid_validity=uid_validity # Passes the folder validity token
        )
     