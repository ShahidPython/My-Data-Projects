"""Core parsing and validation for Email Slicer."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import re

from email_validator import validate_email, EmailNotValidError
import tldextract

@dataclass
class ParsedEmail:
    """Dataclass representing a parsed email with all components."""
    original: str
    local_part: str
    base_username: str
    tag: Optional[str]
    domain: str
    subdomain: Optional[str]
    root_domain: Optional[str]
    tld: Optional[str]
    normalized: str
    is_disposable: bool = False

class EmailSliceError(ValueError):
    """Custom exception for email parsing errors."""
    pass

# Common disposable email domains
DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "guerrillamail.com", "10minutemail.com",
    "throwawaymail.com", "fakeinbox.com", "temp-mail.org", "yopmail.com",
    "dispostable.com", "maildrop.cc", "getairmail.com", "tmpmail.org"
}

def _split_local(local: str) -> tuple[str, Optional[str]]:
    """Split local part into base and optional +tag."""
    if "+" in local:
        base, tag = local.split("+", 1)
        return base, tag
    return local, None

def _is_disposable_domain(domain: str) -> bool:
    """Check if the domain is a known disposable email provider."""
    return domain.lower() in DISPOSABLE_DOMAINS

def parse_email(email: str, check_disposable: bool = False) -> ParsedEmail:
    """
    Validate and parse an email into components.
    
    Args:
        email: The email address to parse
        check_disposable: Whether to check for disposable email domains
        
    Returns:
        ParsedEmail: A dataclass with all email components
        
    Raises:
        EmailSliceError: For invalid input
    """
    email = email.strip()
    if not email:
        raise EmailSliceError("Empty email string")

    try:
        v = validate_email(email, check_deliverability=False)
    except EmailNotValidError as exc:
        raise EmailSliceError(str(exc)) from exc

    normalized = v.email
    local_part, domain = normalized.rsplit("@", 1)
    base_username, tag = _split_local(local_part)

    # Use tldextract for proper domain parsing
    tx = tldextract.extract(domain)
    subdomain = tx.subdomain if tx.subdomain else None
    root_domain = tx.domain if tx.domain else None
    tld_part = tx.suffix if tx.suffix else None
    
    # Check if domain is disposable
    is_disposable = _is_disposable_domain(domain) if check_disposable else False

    return ParsedEmail(
        original=email,
        local_part=local_part,
        base_username=base_username,
        tag=tag,
        domain=domain,
        subdomain=subdomain,
        root_domain=root_domain,
        tld=tld_part,
        normalized=normalized,
        is_disposable=is_disposable
    )

def batch_parse_emails(emails: list[str], check_disposable: bool = False) -> list[ParsedEmail]:
    """
    Parse multiple email addresses.
    
    Args:
        emails: List of email addresses to parse
        check_disposable: Whether to check for disposable email domains
        
    Returns:
        List of ParsedEmail objects
    """
    results = []
    for email in emails:
        try:
            parsed = parse_email(email, check_disposable)
            results.append(parsed)
        except EmailSliceError:
            continue  # Skip invalid emails
    return results