BUSINESS RULES
RULE ID: BR-001

Field: transaction_id
Validation: Must be unique integer between 100000-999999
Action: Reject row if invalid
Error Code: PKV001
RULE ID: BR-002

Field: customer_id
Validation: Format "CUST-XXXXXX" where X is numeric
Action: Reject row if invalid
Error Code: CIF002
RULE ID: BR-003

Field: transaction_date
Validation: Must be between 2020-01-01 and current_date
Action: Set to null and flag
Error Code: DTV003
RULE ID: BR-004

Field: amount
Validation: Must be positive decimal with 2 decimal places
Action: Convert to absolute value and flag
Error Code: AMV004
RULE ID: BR-005

Field: email
Validation: RFC 5322 compliant format
Action: Standardize to lowercase, flag invalid
Error Code: EMV005
RULE ID: BR-006

Field: phone
Validation: Minimum 10 digits, E.164 preferred
Action: Format to +XXXXXXXXXXX, flag invalid
Error Code: PHV006
RULE ID: BR-007

Business Logic: Discount cannot exceed 50% of original price
Action: Cap discount at 50%, flag override
Error Code: BDL007
RULE ID: BR-008

Business Logic: Shipping date must be ≥ order date
Action: Set shipping_date = order_date + 1 day if violated
Error Code: BDL008
RULE ID: BR-009

Quality Threshold: Batch rejection if >5% rows fail critical rules
Action: Stop processing, require manual review
Error Code: QLT009