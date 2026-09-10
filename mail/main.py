from mail_mover import MailMover


def main():
    util = MailMover()
    # util.move_messages("Outlook", "GMail", limit=20)
    util.print_headers("Outlook")
    
    
main()