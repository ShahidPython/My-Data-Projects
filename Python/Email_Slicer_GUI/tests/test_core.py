"""Tests for email_slicer core functionality."""
import pytest
from email_slicer.core import parse_email, EmailSliceError, batch_parse_emails

def test_valid_simple():
    """Test parsing a simple valid email."""
    pe = parse_email("alice@example.com")
    assert pe.local_part == "alice"
    assert pe.domain == "example.com"
    assert pe.base_username == "alice"
    assert pe.tag is None

def test_plus_addressing():
    """Test parsing email with + addressing."""
    pe = parse_email("bob+tag@gmail.com")
    assert pe.base_username == "bob"
    assert pe.tag == "tag"
    assert pe.local_part == "bob+tag"

def test_invalid_email():
    """Test handling of invalid email."""
    with pytest.raises(EmailSliceError):
        parse_email("not-an-email")

def test_subdomain_and_tld():
    """Test parsing email with subdomain and complex TLD."""
    pe = parse_email("x@mail.google.co.uk")
    assert pe.root_domain == "google"
    assert pe.subdomain == "mail"
    assert pe.tld == "co.uk"

def test_empty_email():
    """Test handling of empty email string."""
    with pytest.raises(EmailSliceError):
        parse_email("")

def test_whitespace_email():
    """Test handling of whitespace-only email."""
    with pytest.raises(EmailSliceError):
        parse_email("   ")

def test_batch_parsing():
    """Test batch parsing of multiple emails."""
    emails = [
        "alice@example.com",
        "bob+tag@gmail.com",
        "invalid-email",  # This should be skipped
        "x@mail.google.co.uk"
    ]
    
    results = batch_parse_emails(emails)
    assert len(results) == 3  # One invalid email should be skipped
    assert all(hasattr(pe, 'domain') for pe in results)

def test_disposable_detection():
    """Test detection of disposable email domains."""
    pe = parse_email("test@mailinator.com", check_disposable=True)
    assert pe.is_disposable == True

def test_normal_email_not_disposable():
    """Test that normal emails are not flagged as disposable."""
    pe = parse_email("user@gmail.com", check_disposable=True)
    assert pe.is_disposable == False