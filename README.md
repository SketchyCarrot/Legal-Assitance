# Legal-Saathi

A comprehensive legal assistance platform with multi-modal input handling, AI-powered legal reasoning, and automated form filling capabilities.

## Features

- Multi-modal input handling (voice, text, image)
- Azure OpenAI API integration for legal reasoning
- Bhashini API integration for translation
- Python-based AI agent for form automation
- Auto-fill functionality for legal forms
- Interactive data collection workflow

## Tech Stack

- Frontend: Next.js with TypeScript
- Styling: Tailwind CSS
- State Management: Zustand
- AI/ML: Azure OpenAI, Tesseract.js
- Form Automation: Python (Selenium)
- Translation: Bhashini API

## Setup Instructions

### Frontend Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env.local` file with required environment variables:
   ```
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_MODEL_NAME=your_model_name
   BHASHINI_API_KEY=your_api_key
   BHASHINI_API_ENDPOINT=your_endpoint
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

### Python Service Setup

1. Navigate to the python service directory:
   ```bash
   cd python_service
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask server:
   ```bash
   python app.py
   ```

## Project Structure

```
legal-saathi/
├── src/
│   ├── app/           # Next.js app router pages
│   ├── components/    # React components
│   ├── lib/          # Utility functions and API clients
│   ├── hooks/        # Custom React hooks
│   ├── types/        # TypeScript type definitions
│   └── styles/       # CSS/styling files
├── public/           # Static assets
├── python_service/   # Python backend service
│   ├── app.py
│   └── requirements.txt
└── package.json
```

## Contributing

Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License.

# Form Automation System

A robust and feature-rich form automation system built with Selenium WebDriver, designed to automate web form interactions with support for session management and various input types.

## Features

### Browser Automation
- Multi-browser support (Chrome, Firefox, Edge)
- Headless browser operation
- Screenshot capabilities
- Smart wait strategies for dynamic content
- Browser session management

### Form Handling
- Support for multiple input types:
  - Text fields
  - Dropdowns
  - Checkboxes
  - Radio buttons
  - File uploads
  - Date pickers
- Form validation
- CAPTCHA detection
- Customizable form submission workflows

### Session Management
- Login session handling
- Session persistence
- Session recovery
- Multi-tab/window management
- Session timeout handling

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd form-automation-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from browser_manager import BrowserManager
from form_automator import FormAutomator
from session_manager import SessionManager
from selenium.webdriver.common.by import By

# Initialize browser manager
with BrowserManager(browser_type="chrome", headless=True) as browser_manager:
    driver = browser_manager.driver
    form_automator = FormAutomator(driver)
    
    # Fill form fields
    form_automator.fill_text_field(By.NAME, "username", "john_doe")
    form_automator.click_checkbox(By.ID, "terms", check=True)
    form_automator.submit_form(By.ID, "submit-button")
```

### Session Management

```python
# Initialize session manager
session_manager = SessionManager(driver)

# Handle login and save session
login_successful = session_manager.handle_login(
    login_url="https://example.com/login",
    username_locator=(By.ID, "username"),
    password_locator=(By.ID, "password"),
    submit_locator=(By.ID, "login-button"),
    username="user",
    password="pass",
    success_indicator=(By.CLASS_NAME, "welcome-message")
)

# Save current session
session_manager.save_session("my_session")

# Later, load the saved session
session_manager.load_session("my_session")
```

## Components

### BrowserManager

The `BrowserManager` class handles browser initialization and management:
- Browser type selection
- Headless mode configuration
- Screenshot capabilities
- Context management

### FormAutomator

The `FormAutomator` class provides form interaction capabilities:
- Field identification and interaction
- Input type handling
- Form validation
- CAPTCHA detection
- Submit handling

### SessionManager

The `SessionManager` class manages browser sessions:
- Session storage and retrieval
- Login handling
- Window/tab management
- Session timeout handling

## Best Practices

1. **Error Handling**
   - Always use try-except blocks for form interactions
   - Take screenshots on errors for debugging
   - Implement proper logging

2. **Session Management**
   - Regularly save sessions for long-running operations
   - Clean up expired sessions
   - Handle timeouts gracefully

3. **Form Validation**
   - Validate form fields before submission
   - Handle required fields appropriately
   - Check for CAPTCHA before submission

4. **Browser Management**
   - Use context managers for browser instances
   - Implement proper cleanup
   - Handle multiple windows carefully

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Legal Assistant System - Security & Compliance

## Overview
This document outlines the security and compliance features implemented in the Legal Assistant System, ensuring data protection, user privacy, and regulatory compliance.

## Security Features

### Data Protection
- **Encryption at Rest**: All sensitive data is encrypted using AES-256-GCM
- **Secure Communication**: HTTPS required for all API endpoints
- **Data Anonymization**: Automated anonymization of sensitive user data
- **Secure Data Deletion**: Secure file deletion with multiple overwrites

### Authentication & Authorization
- **User Authentication**: JWT-based authentication with refresh tokens
- **Role-Based Access Control (RBAC)**: Granular permission management
- **Session Management**: Secure session handling with timeout
- **Password Security**: Strong password requirements and hashing
- **Account Protection**: Login attempt tracking and account lockout

### API Security
- **Rate Limiting**: Prevents abuse through request rate limiting
- **API Key Management**: Secure API key generation and rotation
- **Input Validation**: Strict validation of all user inputs
- **Secure Headers**: Implementation of security headers

## Compliance Features

### GDPR Compliance
- **User Consent Management**: Explicit consent tracking
- **Data Subject Rights**: 
  - Right to Access
  - Right to be Forgotten
  - Data Portability
- **Processing Records**: Detailed activity logging
- **Privacy Notices**: Version-controlled privacy policies

### Data Protection
- **Data Minimization**: Collection of only necessary data
- **Retention Policies**: Automated data retention management
- **Processing Records**: GDPR Article 30 compliance
- **Data Breach Protocol**: Incident response procedures

## Setup & Configuration

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file with the following settings:
```env
ENVIRONMENT=development
ENCRYPTION_KEY=your_secure_key
JWT_SECRET=your_jwt_secret
API_KEY=your_api_key
```

### Security Configuration
The security settings can be configured in `config/security_config.py`:
- Encryption settings
- Authentication parameters
- Session timeouts
- API rate limits
- Compliance settings

## Usage Examples

### Authentication
```python
from services.auth_service import AuthService

auth_service = AuthService()

# User authentication
tokens = auth_service.generate_tokens(user_id, roles)
is_valid = auth_service.verify_token(token)
```

### Data Protection
```python
from services.encryption_service import EncryptionService

encryption_service = EncryptionService()

# Encrypt sensitive data
encrypted_data = encryption_service.encrypt_data(data, method='aes-gcm')
decrypted_data = encryption_service.decrypt_data(encrypted_data, method='aes-gcm')
```

### Compliance
```python
from services.compliance_service import ComplianceService

compliance_service = ComplianceService()

# Handle user consent
consent = compliance_service.record_consent(user_id, purpose, data_categories)
is_valid = compliance_service.verify_consent(user_id, purpose)

# Handle GDPR requests
data = compliance_service.handle_data_request(user_id, 'access')
```

## Best Practices

### Security
1. Regularly rotate encryption keys and API keys
2. Monitor failed login attempts
3. Keep dependencies updated
4. Regular security audits
5. Implement logging and monitoring

### Compliance
1. Regular privacy policy updates
2. Maintain processing records
3. Document consent management
4. Regular compliance audits
5. Staff training on data protection

## Contributing
Please follow security best practices when contributing:
1. No sensitive data in code or comments
2. Use secure coding practices
3. Document security implications
4. Include tests for security features

## License
[Your License Here] 