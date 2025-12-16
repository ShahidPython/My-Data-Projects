# Email Slicer Pro

A powerful Python tool for parsing, analyzing, and validating email addresses. Extract components like username, domain, TLD, and more with both CLI and GUI interfaces.

## Features

- **Email Parsing**: Extract local part, domain, subdomain, TLD, and more
- **+Tag Support**: Handle email addresses with tags (e.g., user+tag@domain.com)
- **Validation**: Validate email format and identify disposable email providers
- **Batch Processing**: Process multiple emails from files
- **Modern GUI**: User-friendly graphical interface with copy functionality
- **CLI Interface**: Command-line tool with rich output formatting
- **Provider Analysis**: Categorize email providers (personal, business, disposable)

## Installation

### From Source
```bash
git clone https://github.com/yourusername/email-slicer.git
cd email-slicer
pip install -e .
Using pip
bash
pip install email-slicer
Usage
Command Line Interface
Parse a single email:

bash
email-slicer slice user@example.com
Parse with all details:

bash
email-slicer slice user@example.com --all
Process a batch of emails:

bash
email-slicer batch emails.txt
Validate an email:

bash
email-slicer validate user@example.com --detailed
Graphical Interface
bash
email-slicer-gui
Or run directly:

bash
python -m email_slicer.gui
Examples
bash
# Basic parsing
$ email-slicer slice john.doe+newsletter@gmail.com

# Batch processing with JSON output
$ email-slicer batch emails.txt --json --output results.json

# Detailed validation
$ email-slicer validate test@mailinator.com --detailed
API Usage
python
from email_slicer import parse_email, validate_email_format

# Parse an email
parsed = parse_email("user+tag@sub.example.com")
print(parsed.domain)  # "sub.example.com"
print(parsed.tag)     # "tag"

# Validate format
is_valid = validate_email_format("invalid-email")
print(is_valid)  # False
Project Structure
text
email-slicer/
├── src/email_slicer/     # Source code
├── tests/               # Test cases
├── examples/            # Example files
└── docs/               # Documentation
Contributing
Fork the repository

Create a feature branch

Make your changes

Add tests for new functionality

Submit a pull request

License
MIT License - see LICENSE file for details.

Support
For bugs and feature requests, please create an issue on GitHub.