import imaplib
import os
import msal
from dotenv import load_dotenv

load_dotenv()

# 1. Personal Configuration
client_id = os.environ["CLIENT_ID"]
tenant_id = os.environ["TENANT_ID"]
OUTLOOK_USERNAME = os.environ["OUTLOOK_USERNAME"]
temp_folder = os.environ["TEMP_FOLDER"]

AUTHORITY = f"https://login.microsoftonline.com/{tenant_id}"
# Personal accounts use scopes explicitly prefixed by ://office.com
SCOPES = [
    "https://outlook.office.com/IMAP.AccessAsUser.All",
    "https://outlook.office.com/SMTP.Send"
]

app = msal.PublicClientApplication(client_id, authority=AUTHORITY)
flow = app.initiate_device_flow(scopes=SCOPES)
if "user_code" not in flow:
    raise Exception("Could not initiate authentication flow.")
print(flow["message"]) 
token_result = app.acquire_token_by_device_flow(flow)
if "access_token" not in token_result:
    raise Exception(f"Login failed: {token_result.get('error_description')}")
access_token = token_result["access_token"]
auth_string = f"user={OUTLOOK_USERNAME}\x01auth=Bearer {access_token}\x01\x01".encode('utf-8')

# 4. Connect to IMAP
try:
    mail = imaplib.IMAP4_SSL("outlook.office365.com")
    mail.authenticate("XOAUTH2", lambda x: auth_string)
    print("\nSuccessfully authenticated personal Outlook account!")

    mail.select(f'"{temp_folder}"')
    status, search_data = mail.uid("search", "ALL")
    mail_ids = search_data[0].split()
    print(f"Target folder accessed. Ready to parse {len(mail_ids)} messages.")
    
    mail.close()
    mail.logout()

except Exception as e:
    print(f"IMAP Connection Error: {e}")
