import imaplib
import time

# --- CONFIGURATION ---
GMAIL_USER = "your_gmail_username@gmail.com"
GMAIL_APP_PASS = "xxxx xxxx xxxx xxxx"       # Your 16-character Gmail App Password

HOTMAIL_USER = "your_hotmail_username@hotmail.com"
HOTMAIL_APP_PASS = "your_hotmail_app_password"  # Your Hotmail App Password
HOTMAIL_TARGET_FOLDER = "Inbox"                # Target folder in Hotmail

def transfer_emails():
    # 1. Connect to Gmail (Source)
    print("Connecting to Gmail...")
    gmail = imaplib.IMAP4_SSL("://gmail.com", 993)
    gmail.login(GMAIL_USER, GMAIL_APP_PASS)
    
    # Select the folder you want to copy from
    gmail.select("inbox", readonly=True)
    
    # Search for all email IDs (or use criteria like 'SINCE "01-Jan-2026"')
    status, data = gmail.search(None, "ALL")
    email_ids = data[0].split()
    print(f"Found {len(email_ids)} emails to transfer.")

    # 2. Connect to Hotmail (Destination)
    print("Connecting to Hotmail...")
    hotmail = imaplib.IMAP4_SSL("://office365.com", 993)
    hotmail.login(HOTMAIL_USER, HOTMAIL_APP_PASS)

    # 3. Fetch from Gmail and Append to Hotmail
    for idx, e_id in enumerate(email_ids, 1):
        try:
            # Fetch the raw RFC822 email data from Gmail
            res, msg_data = gmail.fetch(e_id, "(RFC822)")
            if res != "OK":
                continue
                
            raw_email = msg_data[0][1]
            
            # Append the raw email data directly to the Hotmail folder
            # We use None for flags and internal date to let Hotmail auto-assign them
            append_res, _ = hotmail.append(HOTMAIL_TARGET_FOLDER, None, None, raw_email)
            
            if append_res == "OK":
                print(f"[{idx}/{len(email_ids)}] Successfully transferred email ID {e_id.decode()}.")
            else:
                print(f"[{idx}/{len(email_ids)}] Failed to append email ID {e_id.decode()}.")
                
            # Anti-throttling delay
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error transferring email ID {e_id.decode()}: {e}")

    # 4. Clean up connections
    print("Transfer complete. Closing connections.")
    gmail.close()
    gmail.logout()
    hotmail.logout()

if __name__ == "__main__":
    transfer_emails()
