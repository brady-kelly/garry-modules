import imaplib
from email.parser import BytesHeaderParser
from email.utils import parseaddr

# --- CONFIGURATION ---
GMAIL_USER = "your_username@gmail.com"
GMAIL_APP_PASS = "xxxx xxxx xxxx xxxx"  # Your 16-character Gmail App Password

def read_email_metadata():
    # 1. Connect to Gmail
    print("Connecting to Gmail IMAP server...")
    mail = imaplib.IMAP4_SSL("://gmail.com", 993)
    mail.login(GMAIL_USER, GMAIL_APP_PASS)
    
    # Open the Inbox in Read-Only mode to protect read/unread status
    mail.select("inbox", readonly=True)
    
    # 2. Search for all emails
    status, data = mail.search(None, "ALL")
    if status != "OK":
        print("Failed to search emails.")
        return
        
    email_ids = data[0].split()
    print(f"Found {len(email_ids)} emails in Inbox.\n")
    print(f"{'ID':<6} | {'Date':<31} | {'Size (KB)':<10} | {'From':<30} | {'Subject'}")
    print("-" * 110)

    # 3. Fetch header fields and size for each email
    for e_id in email_ids:
        try:
            # We explicitly request only the target headers and the message file size
            status, response_data = mail.fetch(
                e_id, "(BODY.PEEK[HEADER.FIELDS (DATE FROM SUBJECT)] RFC822.SIZE)"
            )
            
            if status != "OK":
                continue

            raw_headers = b""
            size_bytes = 0

            # Parse the mixed response tuple data from the server
            for part in response_data:
                if isinstance(part, tuple):
                    # Part 0 contains the header content string
                    if b"HEADER" in part[0]:
                        raw_headers = part[1]
                    # Check the fetch string metadata to extract the exact byte size
                    meta_str = part[0].decode()
                    if "SIZE" in meta_str:
                        # Extract size integer from string like '1 (RFC822.SIZE 2345 BODY[HEADER...)'
                        for piece in meta_str.split():
                            if piece.isdigit():
                                size_bytes = int(piece)

            # 4. Format and clean up the parsed information
            headers = BytesHeaderParser().parsebytes(raw_headers)
            
            # Clean up headers (handles empty entries smoothly)
            date_val = headers.get("Date", "N/A").strip()
            subject_val = headers.get("Subject", "(No Subject)").strip()
            
            # Parse the sender address to isolate the raw email string
            from_raw = headers.get("From", "N/A")
            _, from_email = parseaddr(from_raw)
            
            size_kb = round(size_bytes / 1024, 2)
            msg_id = e_id.decode()

            # Truncate values to keep the terminal layout clean
            print(f"{msg_id:<6} | {date_val[:31]:<31} | {size_kb:<10} | {from_email[:30]:<30} | {subject_val[:40]}")

        except Exception as e:
            print(f"Error parsing metadata for email ID {e_id.decode()}: {e}")

    # 5. Logout safely
    mail.logout()

if __name__ == "__main__":
    read_email_metadata()
