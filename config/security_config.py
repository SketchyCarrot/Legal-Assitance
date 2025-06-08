from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security Settings
SECURITY_CONFIG = {
    # Encryption Settings
    'ENCRYPTION': {
        'ALGORITHM': 'AES-256-GCM',
        'KEY_DERIVATION': 'PBKDF2',
        'ITERATIONS': 100000,
        'SALT_LENGTH': 32,
        'KEY_LENGTH': 32
    },

    # Authentication Settings
    'AUTH': {
        'TOKEN_EXPIRY': timedelta(hours=1),
        'REFRESH_TOKEN_EXPIRY': timedelta(days=30),
        'PASSWORD_MIN_LENGTH': 12,
        'REQUIRE_SPECIAL_CHARS': True,
        'REQUIRE_NUMBERS': True,
        'REQUIRE_UPPERCASE': True,
        'REQUIRE_LOWERCASE': True,
        'MAX_LOGIN_ATTEMPTS': 5,
        'LOCKOUT_DURATION': timedelta(minutes=15)
    },

    # Session Settings
    'SESSION': {
        'COOKIE_SECURE': True,
        'COOKIE_HTTPONLY': True,
        'COOKIE_SAMESITE': 'Strict',
        'SESSION_TIMEOUT': timedelta(minutes=30),
        'REQUIRE_2FA': True
    },

    # API Security
    'API': {
        'RATE_LIMIT': {
            'WINDOW': timedelta(minutes=1),
            'MAX_REQUESTS': 100
        },
        'REQUIRE_HTTPS': True,
        'ALLOWED_ORIGINS': ['https://legalassistant.com'],
        'API_KEY_EXPIRY': timedelta(days=90)
    },

    # Data Protection
    'DATA_PROTECTION': {
        'RETENTION_PERIOD': timedelta(days=365),
        'BACKUP_RETENTION': timedelta(days=90),
        'ANONYMIZATION_FIELDS': [
            'name', 'email', 'phone', 'address', 'ip_address'
        ],
        'SENSITIVE_FIELDS': [
            'ssn', 'passport_number', 'credit_card'
        ]
    },

    # Compliance
    'COMPLIANCE': {
        'GDPR_ENABLED': True,
        'CCPA_ENABLED': True,
        'REQUIRE_CONSENT': True,
        'CONSENT_EXPIRY': timedelta(days=365),
        'PRIVACY_POLICY_VERSION': '1.0.0',
        'TOS_VERSION': '1.0.0'
    },

    # Audit Logging
    'AUDIT': {
        'ENABLED': True,
        'LOG_LEVEL': 'INFO',
        'RETENTION_PERIOD': timedelta(days=90),
        'INCLUDE_USER_AGENT': True,
        'INCLUDE_IP_ADDRESS': True
    }
}

# Role-Based Access Control (RBAC) Configuration
RBAC_CONFIG = {
    'roles': {
        'admin': {
            'permissions': ['read', 'write', 'delete', 'manage_users', 'manage_roles'],
            'description': 'Full system access'
        },
        'legal_professional': {
            'permissions': ['read', 'write', 'manage_cases'],
            'description': 'Access to manage legal cases'
        },
        'user': {
            'permissions': ['read', 'write_own'],
            'description': 'Basic user access'
        },
        'guest': {
            'permissions': ['read'],
            'description': 'Read-only access'
        }
    },
    'resources': {
        'user_data': ['read', 'write', 'delete'],
        'case_data': ['read', 'write', 'delete', 'manage_cases'],
        'system_settings': ['read', 'write', 'manage_users', 'manage_roles']
    }
}

# Secure Headers Configuration
SECURE_HEADERS = {
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'X-Content-Type-Options': 'nosniff',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}

# Environment-specific settings
ENV = os.getenv('ENVIRONMENT', 'development')

if ENV == 'development':
    # Development-specific overrides
    SECURITY_CONFIG['API']['REQUIRE_HTTPS'] = False
    SECURITY_CONFIG['SESSION']['COOKIE_SECURE'] = False
    SECURITY_CONFIG['API']['ALLOWED_ORIGINS'].append('http://localhost:3000')
elif ENV == 'production':
    # Production-specific settings
    SECURITY_CONFIG['AUTH']['REQUIRE_2FA'] = True
    SECURITY_CONFIG['API']['RATE_LIMIT']['MAX_REQUESTS'] = 50 