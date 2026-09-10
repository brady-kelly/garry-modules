from mail_mover import MailMover


def main():
    util = MailMover()
    util.move_messages("Outlook", "GMail")
    
    
main()