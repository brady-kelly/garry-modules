from mail_info import MailInfo
from mail_account import MailAccount
from mail_client import MailClient

box = "Gmail"
account = MailAccount(box)

client = MailClient(account)

infos = client.fetch_headers()
MailInfo.print_heading(len(infos or []))
print(f"{len(infos or [])} headers found")

for info in infos:
    info.print()