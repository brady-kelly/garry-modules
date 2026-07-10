import datetime
from email.message import EmailMessage
from email.parser import BytesHeaderParser
from email.policy import default
from email.utils import parseaddr
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
        return cls(
            msg=msg,
            size=size,                  
            uid=uid,                 
            uid_validity=uid_validity,
            flags=flags,                
            internal_date=internal_date,
            raw_content=b""             
        )