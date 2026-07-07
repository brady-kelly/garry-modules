class MailResult:
    
    def __init__(self, success: bool, message: str, result_list = []) -> None:
        self.success = success
        self.message = message
        self.result_list = result_list
        self.error_list = []