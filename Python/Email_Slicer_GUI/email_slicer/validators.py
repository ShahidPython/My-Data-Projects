"""Simple validators and helpers (typo suggestions)."""
from __future__ import annotations
from typing import Optional
import difflib
import re

# Import from the same package
from .core import DISPOSABLE_DOMAINS

# Curated common providers (you can extend this list)
_COMMON_DOMAINS = [
    "gmail.com", "googlemail.com", "hotmail.com", "outlook.com",
    "yahoo.com", "icloud.com", "protonmail.com", "aol.com",
    "zoho.com", "mail.com", "yandex.com", "gmx.com",
    "live.com", "msn.com", "icloud.com", "me.com"
]

def validate_email_format(email: str) -> bool:
    """
    Simple regex validation for email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email format is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def suggest_domain(domain: str, cutoff: float = 0.7) -> Optional[str]:
    """
    Return a suggested domain if domain looks like a typo, else None.
    
    Args:
        domain: The domain to check for suggestions
        cutoff: Similarity threshold for suggestions (0.0-1.0)
        
    Returns:
        Optional[str]: Suggested domain or None
    """
    domain = domain.lower().strip()
    matches = difflib.get_close_matches(domain, _COMMON_DOMAINS, n=1, cutoff=cutoff)
    return matches[0] if matches else None

def get_email_provider_type(domain: str) -> str:
    """
    Categorize email provider type.
    
    Args:
        domain: The domain to categorize
        
    Returns:
        str: Provider type ('personal', 'business', 'disposable', 'unknown')
    """
    domain_lower = domain.lower()
    
    # Major providers
    major_providers = {'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'aol.com', 'icloud.com'}
    if domain_lower in major_providers:
        return 'personal'
    
    # Business/enterprise (common patterns)
    if re.match(r'.*\.(edu|gov|org|mil)$', domain_lower):
        return 'business'
    
    # Disposable emails
    if domain_lower in DISPOSABLE_DOMAINS:
        return 'disposable'
    
    return 'unknown'