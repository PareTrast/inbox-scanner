import os
import base64
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from schemas import EmailMessage

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service(credentials_path="credentials.json", token_path="token.json"):
    """Authenticates the user via OAuth2 and returns a Gmail service client."""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def _extract_body_and_links(payload: dict) -> tuple[str, list[str]]:
    """Extracts plain text and all href URLs from email MIME parts."""
    text_content = ""
    links = []

    def parse_part(part):
        nonlocal text_content
        mime = part.get("mimeType", "")
        body_data = part.get("body", {}).get("data")

        if body_data:
            decoded = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
            if mime == "text/html":
                soup = BeautifulSoup(decoded, "html.parser")
                links.extend([a["href"] for a in soup.find_all("a", href=True)])
                text_content = soup.get_text(separator=" ", strip=True)
            elif mime == "text/plain" and not text_content:
                text_content = decoded

        for sub_part in part.get("parts", []):
            parse_part(sub_part)

    parse_part(payload)
    unique_links = list(dict.fromkeys(links))[:15]
    return text_content, unique_links

def fetch_recent_emails(service, max_results: int = 50) -> list[EmailMessage]:
    """Fetches the most recent messages and normalizes them into EmailMessage objects."""
    results = service.users().messages().list(userId="me", maxResults=max_results).execute()
    messages = results.get("messages", [])
    email_list = []

    for msg in messages:
        full_msg = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        payload = full_msg.get("payload", {})
        header_map = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
        body, links = _extract_body_and_links(payload)

        email_list.append(
            EmailMessage(
                id=msg["id"],
                subject=header_map.get("subject", "(No Subject)"),
                sender=header_map.get("from", "Unknown"),
                reply_to=header_map.get("reply-to", "None"),
                auth_results=header_map.get("authentication-results", "None"),
                links=links,
                body=body[:2500],
            )
        )

    return email_list