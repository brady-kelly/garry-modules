from email.message import EmailMessage
from message_wrapper import MessageWrapper
from mail_account import MailAccount
from mail_client import MailClient

def run_ops():
    from_account = MailAccount("Outlook")
    to_account= MailAccount("GMail")

    from_client = MailClient(from_account)
    to_client = MailClient(to_account)

    headers_result = from_client.fetch_headers()
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
                
        wrapper = headers_result.result_list[0]
        fetch_result = from_client.fetch_message(wrapper)
        if fetch_result.success and len(fetch_result.result_list) > 0:
            msg: EmailMessage = fetch_result.result_list[0].msg
            print(f"Fetched message: {msg["Subject"]}")
        else:
            print(f"Error getting message for id {wrapper.uid}: {fetch_result.error_list[0]}")
            
        # append_result = to_client.append_message("Inbox", wrapper)
        # if append_result.success:
        #     print(f"Appended message: {msg["Subject"]}")
        # else:
        #     print(f"Error appending message for id {wrapper.uid}: {append_result.error_list[0]}")

run_ops()