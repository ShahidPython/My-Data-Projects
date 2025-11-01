"""Email Slicer - Extract and analyze email address components."""

__version__ = "1.0.0"

from .core import parse_email, ParsedEmail, EmailSliceError, batch_parse_emails
from .validators import suggest_domain, validate_email_format, get_email_provider_type

__all__ = [
    "__version__", 
    "parse_email", 
    "ParsedEmail", 
    "EmailSliceError",
    "batch_parse_emails",
    "suggest_domain",
    "validate_email_format",
    "get_email_provider_type"
]