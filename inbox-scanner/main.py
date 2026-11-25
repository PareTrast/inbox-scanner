from model_manager import resolve_model_interactive
from gmail_client import get_gmail_service, fetch_recent_emails
from scanner import LocalEmailScanner

def run():
    # 1. Select or download the .litertlm model
    model_path = resolve_model_interactive()

    # 2. Connect to Gmail and pull recent messages
    count_input = input("\nHow many recent emails to scan? [default: 50]: ").strip()
    max_emails = int(count_input) if count_input.isdigit() else 50

    print("\nConnecting to Gmail...")
    service = get_gmail_service()
    emails = fetch_recent_emails(service, max_results=max_emails)
    print(f"Fetched {len(emails)} emails.\n")

    # 3. Load the local model once and scan each email
    with LocalEmailScanner(model_path=model_path, use_gpu=True) as scanner:
        for idx, email in enumerate(emails, 1):
            report = scanner.scan_email(email)
            status = "SAFE" if report.is_safe else f"WARNING ({report.risk_level} - {report.threat_type})"
            print(f"[{idx}/{len(emails)}] {status} | From: {email.sender} | Subject: {email.subject}")

            if not report.is_safe:
                print(f"   Red Flags: {', '.join(report.red_flags)}")
                print(f"   Summary:   {report.summary}\n")

if __name__ == "__main__":
    run()