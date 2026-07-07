from email.message import EmailMessage

from message_wrapper import MessageWrapper
from mail_account import MailAccount
from mail_client import MailClient

box = "Gmail"
account = MailAccount(box)

client = MailClient(account)

headers_result = client.fetch_headers()
if not headers_result.success:
    print(headers_result.message)
    if len(headers_result.error_list) > 0:
        for err in headers_result.error_list:
            print(err)
else:
    MessageWrapper.print_heading(len(headers_result.result_list))
    print(f"{len(headers_result.result_list)} headers found")

    for info in headers_result.result_list:
        info.print()
            
    msg_result = client.fetch_message(headers_result.result_list[0])
    if headers_result.success and len(headers_result.result_list) > 0:
        msg: EmailMessage = headers_result.result_list[0].msg
        print(f"Something: {msg["Subject"]}")
    else:
        print(f"Error getting message for id {headers_result.result_list[0].uid}: {msg_result.error_list[0]}")