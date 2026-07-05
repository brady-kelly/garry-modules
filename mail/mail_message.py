class MailMessage:
    
    def __init__(self, info, raw_body) -> None:
        self.info = info
        self.raw_body = raw_body