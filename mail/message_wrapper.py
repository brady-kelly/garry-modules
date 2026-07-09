from email.message import EmailMessage
from email.parser import BytesHeaderParser
from email.policy import default
from email.utils import parseaddr
import imaplib
import re
import time

class MessageWrapper:
    
    def __init__(self, msg: EmailMessage, size: int, uid: bytes, uid_validity: int, flags: list[str], internal_date: str | None):
        self.msg = msg
        self.sender = msg['From']
        self.subject = msg['Subject']
        self.date = msg['Date']   
        self.size = size
        self.uid = uid
        self.uid_validity = uid_validity
        self.internal_date = internal_date
        
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
        
        # === NEW INTERNALDATE PARSING LOGIC ===
        # 1. Extract the raw date string from the envelope metadata
        # Looks for: INTERNALDATE "dd-Mmm-yyyy hh:mm:ss +zzzz"
        date_match = re.search(r'INTERNALDATE\s+"([^"]+)"', envelope_str)
        
        # 2. Convert it directly into an IMAP append-compatible formatted string
        # If no internal date is found, default to None (server uses current time)
        internal_date = None
        if date_match:
            try:
                # Convert IMAP timestamp string into a time struct
                time_struct = time.strptime(date_match.group(1), "%d-%b-%Y %H:%M:%S %z")
                # Format time struct directly into the format required by the append command
                internal_date = imaplib.Time2Internaldate(time_struct)
            except Exception:
                # Fallback handler in case of unexpected locale or timezone string layout issues
                internal_date = None        
                    
        return cls(
            msg=msg,
            size=email_size, 
            uid=uid,                 
            uid_validity=uid_validity,
            flags=email_flags,
            internal_date=internal_date
        )