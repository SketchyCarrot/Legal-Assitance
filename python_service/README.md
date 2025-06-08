# Legal-Saathi Python Service

This service provides form automation and data processing capabilities for the Legal-Saathi project.

## Features

- Browser Automation
  - Headless browser management
  - Concurrent request handling
  - Screenshot capabilities
  - Session management

- Form Recognition
  - Web page analysis
  - Form field detection
  - Form type classification
  - Schema extraction
  - Field mapping

- Data Processing
  - Input validation
  - Field matching
  - Data transformation
  - Fuzzy matching
  - Indian legal document validation

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
FLASK_APP=app
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-key
```

4. Run the development server:
```bash
flask run
```

## API Endpoints

### Browser Module

- `POST /api/browser/navigate`
  - Navigate to a URL and get page information
  - Requires: `url` in request body
  - Returns: page title, URL, and screenshot

- `GET /api/browser/status`
  - Get browser pool status
  - Returns: available and active browser counts

- `POST /api/browser/cleanup`
  - Clean up browser resources

### Form Module

- `POST /api/form/analyze`
  - Analyze forms on a webpage
  - Requires: `url` in request body
  - Returns: detailed form analysis

- `POST /api/form/detect-type`
  - Detect form types on a webpage
  - Requires: `url` in request body
  - Returns: list of form types

- `POST /api/form/extract-schema`
  - Extract form schema
  - Requires: `url` and optional `form_index` in request body
  - Returns: detailed form schema

### Data Module

- `POST /api/data/process`
  - Process and validate form data
  - Requires: `form_schema` and `user_data` in request body
  - Returns: processed and validated data

- `POST /api/data/match-fields`
  - Match user data fields to form fields
  - Requires: `form_fields` and `user_data` in request body
  - Returns: field matches

- `POST /api/data/validate`
  - Validate specific field data
  - Requires: `field_type` and `value` in request body
  - Returns: validation result

## Authentication

All endpoints require JWT authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your-token>
```

## Error Handling

All endpoints return standardized error responses:
```json
{
    "success": false,
    "error": "Error message"
}
```

## Logging

Logs are stored in the `logs` directory with automatic rotation:
- Maximum log file size: 10KB
- Maximum number of backup files: 10

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Check code style:
```bash
flake8
```

## Production Deployment

1. Set environment variables:
```bash
export FLASK_ENV=production
export JWT_SECRET_KEY=your-secure-key
```

2. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
``` 