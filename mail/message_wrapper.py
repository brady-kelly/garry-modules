import datetime
from email.message import EmailMessage
from email.parser import BytesHeaderParser
from email.policy import default
from email.policy import SMTP
from email.utils import parseaddr, parsedate_to_datetime
import imaplib
import re
import time

class MessageWrapper:
    
    def __init__(self, msg: EmailMessage, size: int, uid: int, uid_validity: int, flags: list[str], internal_date: datetime.datetime | None, raw_content: bytes):
        self.msg = msg
        self.sender = msg['From']
        self.subject = msg['Subject']
        self.date = msg['Date']   
        self.size = size
        self.uid = uid
        self.uid_validity = uid_validity
        self.flags = flags
        if isinstance(internal_date, tuple):
            self.internal_date = datetime.datetime(*internal_date[:6])
        else:
            self.internal_date = internal_date
        self.raw_content = raw_content=raw_content
        
    def print(self):
        try:
            iso_date = parsedate_to_datetime(self.date).isoformat()
        except Exception:
            iso_date = str(self.date)  
        print(f"{iso_date[:20]:<20} | {self.size:<10} | {self.sender[:40]:<40} | {self.subject[:55]}")
            
    
    @classmethod                
    def print_heading(cls, count):
        print(f"{'Date':<20} | {'Size (KB)':<10} | {'From':<40} | {'Subject'}")
        print("-" * 135)          
                
    @classmethod
    def from_imap_client_data(
        cls, 
        uid: int, 
        uid_validity: int, 
        size: int, 
        flags: list[str], 
        internal_date: datetime.datetime | None, 
        raw_headers: bytes
    ):
        msg: EmailMessage = BytesHeaderParser(policy=default).parsebytes(raw_headers)      
        raw_content = msg.as_bytes(policy=SMTP)  
        return cls(
            msg=msg,
            size=size,                  
            uid=uid,                 
            uid_validity=uid_validity,
            flags=flags,                
            internal_date=internal_date,
            raw_content=raw_content         
        )