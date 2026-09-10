from email.message import EmailMessage

from message_wrapper import MessageWrapper
from task_result import TaskResult
from mail_client import MailClient
from mail_account import MailAccount


class MailMover:
    
    def print_errors(self, result: TaskResult, desc: str | None = None):
        if desc is None or len(desc) == 0:
            print(f"{result.message}")
        else:
            print(f"{desc}: {result.message}")
        for err in result.error_list:
            print(f"\t{err}")
    
    def print_headers(self, account_name: str, limit: int = 50):
        account = MailAccount(account_name)
        client = MailClient(account)
        
        headers_result = client.fetch_headers(limit=limit)
        if not headers_result.success:
            self.print_errors(headers_result, f"Errors fetching headers for account {account.username}")
            
        print(f"{len(headers_result.result_list)} headers found")
        MessageWrapper.print_heading(len(headers_result.result_list))
        for wrapper in headers_result.result_list:
            wrapper.print()
            
    def move_messages(self, from_account_name: str, to_account_name: str, limit: int=50, delete_after: bool = False):
        from_account = MailAccount(from_account_name)
        to_account= MailAccount(to_account_name)

        from_client = MailClient(from_account)
        to_client = MailClient(to_account)
        
        headers_result = from_client.fetch_headers(limit=limit)
        if not headers_result.success:
            self.print_errors(headers_result, f"Errors fetching headers for account {from_account.username}")                   
            return
        
        to_client.connect()
        print(f"Moving {len(headers_result.result_list)} messages:")
        MessageWrapper.print_heading(len(headers_result.result_list))
        
        moved: list[int] = []
        for wrapper in headers_result.result_list:
            fetch_result = from_client.fetch_message(wrapper)
            if fetch_result.success and len(fetch_result.result_list) > 0:
                msg: EmailMessage = fetch_result.result_list[0].msg
            else:
                self.print_errors(fetch_result, f"Error getting message for id {wrapper.uid}")
                
            append_result = to_client.append_message("Inbox", wrapper)
            if append_result.success:
                wrapper.print()
                moved.append(wrapper.uid)
            else:
                self.print_errors(append_result, f"Error appending message for id {wrapper.uid}")                