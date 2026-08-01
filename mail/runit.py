from email.message import EmailMessage
from task_result import TaskResult
from message_wrapper import MessageWrapper
from mail_account import MailAccount
from mail_client import MailClient

def print_errors(result: TaskResult, desc: str | None = None):
    if desc is None or len(desc) == 0:
        print(f"{result.message}")
    else:
        print(f"{desc}: {result.message}")
    for err in result.error_list:
        print(f"\t{err}")

def run_ops():
    from_account = MailAccount("Outlook")
    to_account= MailAccount("GMail")

    from_client = MailClient(from_account)
    to_client = MailClient(to_account)

    headers_result = from_client.fetch_headers(limit=50)
    if not headers_result.success:
        print_errors(headers_result)

    else:
        print(f"{len(headers_result.result_list)} headers found")
        MessageWrapper.print_heading(len(headers_result.result_list))

        for wrapper in headers_result.result_list:
               
            fetch_result = from_client.fetch_message(wrapper)
            if fetch_result.success and len(fetch_result.result_list) > 0:
                msg: EmailMessage = fetch_result.result_list[0].msg
            else:
                print_errors(fetch_result, f"Error getting message for id {wrapper.uid}")
                
            append_result = to_client.append_message("Inbox", wrapper)
            if append_result.success:
                wrapper.print()
            else:
                print_errors(append_result, f"Error appending message for id {wrapper.uid}")

run_ops()