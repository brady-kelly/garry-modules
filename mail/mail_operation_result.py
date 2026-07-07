from message_wrapper import MessageWrapper

class MailOperationResult:
    
    def __init__(self, success: bool, message: str, result_list: list[MessageWrapper] = [], error_list: list[str] = []) -> None:
        self.success = success
        self.message = message
        self.result_list: list[MessageWrapper]  = result_list
        self.error_list: list[str] = error_list
        
