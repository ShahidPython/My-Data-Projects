# Data Cleaning Pipeline API
Version: 2.0.0

## Base URL
https://api.datacleaner.production.company.com/v1

## Authentication
Bearer Token Required
Header: Authorization: Bearer ${API_KEY}

## Endpoints

### 1. Upload and Clean
POST /clean
Content-Type: multipart/form-data

Parameters:
- file: CSV file (max 1GB)
- config: JSON string (optional)
- callback_url: Webhook URL (optional)

Response:
{
  "job_id": "cln_7f83b1657ff1fc53",
  "status": "queued",
  "estimated_completion": "2024-01-15T14:30:00Z"
}

### 2. Check Status
GET /status/{job_id}

Response:
{
  "job_id": "cln_7f83b1657ff1fc53",
  "status": "completed",
  "download_url": "https://storage.company.com/results/cln_7f83b1657ff1fc53.parquet",
  "metrics": {
    "rows_processed": 15842,
    "rows_cleaned": 14258,
    "quality_score": 99.2
  }
}

### 3. Download Result
GET /download/{job_id}
Returns: Cleaned data file (Parquet format)

### 4. Get Rules
GET /rules
Returns: Active cleaning rules configuration

## Rate Limits
- 100 requests per hour per API key
- 10 concurrent jobs per account
- 1GB max file size

## Error Codes
- 400: Invalid input
- 401: Unauthorized
- 429: Rate limit exceeded
- 500: Internal server error

## Webhook Events
POST to callback_url with:
{
  "event": "job.completed",
  "job_id": "cln_7f83b1657ff1fc53",
  "timestamp": "2024-01-15T14:28:15Z"
}