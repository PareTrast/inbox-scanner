from pydantic import BaseModel

class EmailMessage(BaseModel):
    id: str
    subject: str
    sender: str
    reply_to: str
    auth_results: str
    links: list[str]
    body: str
    
    
class EmailSafetyReport(BaseModel):
    is_safe: bool
    risk_level: str # "Low", "Medium", "High"
    threat_type: str # "None", "Phishing", "Spoofing", "Spam", "Malware Link"
    red_flags: list[str]
    summary: stry