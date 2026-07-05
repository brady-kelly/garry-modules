from mail_account import MailAccount
from mail_client import MailClient

box = "Gmail"
account = MailAccount(box)

client = MailClient(account)

meta = client.fetch_headers()
print(f"{len(meta or [])} headers found")