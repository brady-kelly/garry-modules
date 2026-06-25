import imaplib


url_map = {
    "gmail": "://gmail.com",
    "hotmail": "//office365.com"
}

class MailClient:
    
    def __init__(self, account):
        self.account = account
        
    def get_metadata(self):
        url = url_map.get(self.account.type)
        mail = imaplib.IMAP4_SSL("://gmail.com", 993)
        mail.login(self.account.username, self.account.password)