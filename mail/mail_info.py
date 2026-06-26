from email.parser import BytesHeaderParser
from email.utils import parseaddr


class MailInfo:
    
    def __init__(self, date, subject, sender, size, msg_id):
        self.date = date
        self.subject = subject
        self.sender = sender
        self.size = size
        self.msg_id = msg_id
        
    @classmethod        
    def from_response_data(cls, response_data):
        
        raw_headers = b""
        size_bytes = 0        
        
        # Parse the mixed response tuple data from the server
        for part in response_data:
            if isinstance(part, tuple):
                # Part 0 contains the header content string
                if b"HEADER" in part[0]:
                    raw_headers = part[1]
                # Check the fetch string metadata to extract the exact byte size
                meta_str = part[0].decode()
                if "SIZE" in meta_str:
                    # Extract size integer from string like '1 (RFC822.SIZE 2345 BODY[HEADER...)'
                    for piece in meta_str.split():
                        if piece.isdigit():
                            size_bytes = int(piece)   
                            
        # 4. Format and clean up the parsed information
        headers = BytesHeaderParser().parsebytes(raw_headers)
        
        # Clean up headers (handles empty entries smoothly)
        date_val = headers.get("Date", "N/A").strip()
        subject_val = headers.get("Subject", "(No Subject)").strip()
        
        # Parse the sender address to isolate the raw email string
        from_raw = headers.get("From", "N/A")
        _, from_email = parseaddr(from_raw)
        
        size_kb = round(size_bytes / 1024, 2)
        msg_id = id.decode()      
        
        return cls(date_val, subject_val, from_email, size_kb, msg_id)        