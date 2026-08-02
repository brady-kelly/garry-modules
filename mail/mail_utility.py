from message_wrapper import MessageWrapper
from task_result import TaskResult
from mail_client import MailClient
from mail_account import MailAccount


class MailUtility:
    
    def print_errors(self, result: TaskResult, desc: str | None = None):
        if desc is None or len(desc) == 0:
            print(f"{result.message}")
        else:
            print(f"{desc}: {result.message}")
        for err in result.error_list:
            print(f"\t{err}")
    
    def print_headers(self, account_name: str):
        account = MailAccount(account_name)
        client = MailClient(account)
        
        headers_result = client.fetch_headers(limit=50)
        if not headers_result.success:
            self.print_errors(headers_result, f"Errors fetching headers for account {account.username}")
            
        MessageWrapper.print_heading(len(headers_result.result_list))