import jwt
import bcrypt
import secrets
from datetime import datetime, timezone
from typing import Dict, Optional, List
import logging
from config.security_config import SECURITY_CONFIG, RBAC_CONFIG
from services.encryption_service import EncryptionService

class AuthService:
    def __init__(self):
        """Initialize authentication service"""
        self.encryption_service = EncryptionService()
        self._jwt_secret = secrets.token_hex(32)
        self._refresh_tokens = {}
        self._failed_attempts = {}
        self._user_sessions = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt
        :param password: Plain text password
        :return: Hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        :param password: Plain text password to verify
        :param hashed_password: Hashed password to check against
        :return: True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    def validate_password_strength(self, password: str) -> List[str]:
        """
        Validate password strength against security requirements
        :param password: Password to validate
        :return: List of validation errors (empty if password is valid)
        """
        errors = []
        
        if len(password) < SECURITY_CONFIG['AUTH']['PASSWORD_MIN_LENGTH']:
            errors.append(f"Password must be at least {SECURITY_CONFIG['AUTH']['PASSWORD_MIN_LENGTH']} characters long")
            
        if SECURITY_CONFIG['AUTH']['REQUIRE_SPECIAL_CHARS'] and not any(c in "!@#$%^&*(),.?\":{}|<>" for c in password):
            errors.append("Password must contain at least one special character")
            
        if SECURITY_CONFIG['AUTH']['REQUIRE_NUMBERS'] and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
            
        if SECURITY_CONFIG['AUTH']['REQUIRE_UPPERCASE'] and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
            
        if SECURITY_CONFIG['AUTH']['REQUIRE_LOWERCASE'] and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
            
        return errors

    def generate_tokens(self, user_id: str, roles: List[str]) -> Dict[str, str]:
        """
        Generate access and refresh tokens
        :param user_id: User ID
        :param roles: List of user roles
        :return: Dictionary containing access and refresh tokens
        """
        # Generate access token
        access_token = jwt.encode(
            {
                'user_id': user_id,
                'roles': roles,
                'exp': datetime.now(timezone.utc) + SECURITY_CONFIG['AUTH']['TOKEN_EXPIRY']
            },
            self._jwt_secret,
            algorithm='HS256'
        )
        
        # Generate refresh token
        refresh_token = secrets.token_hex(32)
        self._refresh_tokens[refresh_token] = {
            'user_id': user_id,
            'roles': roles,
            'exp': datetime.now(timezone.utc) + SECURITY_CONFIG['AUTH']['REFRESH_TOKEN_EXPIRY']
        }
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode a JWT token
        :param token: JWT token to verify
        :return: Decoded token payload or None if invalid
        """
        try:
            return jwt.decode(token, self._jwt_secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {str(e)}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate new access token using refresh token
        :param refresh_token: Refresh token
        :return: New access token or None if refresh token is invalid
        """
        token_data = self._refresh_tokens.get(refresh_token)
        if not token_data:
            return None
            
        # Check if refresh token has expired
        if datetime.now(timezone.utc) > token_data['exp']:
            del self._refresh_tokens[refresh_token]
            return None
            
        # Generate new access token
        return jwt.encode(
            {
                'user_id': token_data['user_id'],
                'roles': token_data['roles'],
                'exp': datetime.now(timezone.utc) + SECURITY_CONFIG['AUTH']['TOKEN_EXPIRY']
            },
            self._jwt_secret,
            algorithm='HS256'
        )

    def check_permission(self, user_roles: List[str], required_permission: str, resource: str) -> bool:
        """
        Check if user has required permission for a resource
        :param user_roles: List of user roles
        :param required_permission: Required permission
        :param resource: Resource to check permission for
        :return: True if user has permission, False otherwise
        """
        for role in user_roles:
            role_config = RBAC_CONFIG['roles'].get(role)
            if role_config and required_permission in role_config['permissions']:
                if resource in RBAC_CONFIG['resources']:
                    return required_permission in RBAC_CONFIG['resources'][resource]
        return False

    def track_login_attempt(self, user_id: str, success: bool):
        """
        Track login attempts and handle account lockout
        :param user_id: User ID
        :param success: Whether the login attempt was successful
        """
        current_time = datetime.now(timezone.utc)
        
        if success:
            # Reset failed attempts on successful login
            self._failed_attempts.pop(user_id, None)
            return
            
        # Track failed attempt
        if user_id not in self._failed_attempts:
            self._failed_attempts[user_id] = {
                'count': 1,
                'first_attempt': current_time
            }
        else:
            self._failed_attempts[user_id]['count'] += 1
            
        # Check if account should be locked
        if self._failed_attempts[user_id]['count'] >= SECURITY_CONFIG['AUTH']['MAX_LOGIN_ATTEMPTS']:
            self.logger.warning(f"Account locked for user {user_id} due to too many failed attempts")
            # You might want to implement additional logic here (e.g., notify user, admin)

    def is_account_locked(self, user_id: str) -> bool:
        """
        Check if an account is locked due to too many failed attempts
        :param user_id: User ID
        :return: True if account is locked, False otherwise
        """
        if user_id not in self._failed_attempts:
            return False
            
        attempts = self._failed_attempts[user_id]
        current_time = datetime.now(timezone.utc)
        
        # Check if lockout period has expired
        if attempts['count'] >= SECURITY_CONFIG['AUTH']['MAX_LOGIN_ATTEMPTS']:
            lockout_end = attempts['first_attempt'] + SECURITY_CONFIG['AUTH']['LOCKOUT_DURATION']
            if current_time > lockout_end:
                # Reset failed attempts after lockout period
                del self._failed_attempts[user_id]
                return False
            return True
            
        return False

    def create_session(self, user_id: str, user_agent: str, ip_address: str) -> str:
        """
        Create a new session for a user
        :param user_id: User ID
        :param user_agent: User agent string
        :param ip_address: IP address
        :return: Session ID
        """
        session_id = secrets.token_urlsafe(32)
        self._user_sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(timezone.utc),
            'last_activity': datetime.now(timezone.utc),
            'user_agent': user_agent,
            'ip_address': ip_address
        }
        return session_id

    def validate_session(self, session_id: str) -> bool:
        """
        Validate a session and update last activity
        :param session_id: Session ID to validate
        :return: True if session is valid, False otherwise
        """
        session = self._user_sessions.get(session_id)
        if not session:
            return False
            
        current_time = datetime.now(timezone.utc)
        
        # Check session timeout
        if current_time - session['last_activity'] > SECURITY_CONFIG['SESSION']['SESSION_TIMEOUT']:
            del self._user_sessions[session_id]
            return False
            
        # Update last activity
        session['last_activity'] = current_time
        return True

    def end_session(self, session_id: str):
        """
        End a user session
        :param session_id: Session ID to end
        """
        self._user_sessions.pop(session_id, None)

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now(timezone.utc)
        expired_sessions = [
            session_id for session_id, session in self._user_sessions.items()
            if current_time - session['last_activity'] > SECURITY_CONFIG['SESSION']['SESSION_TIMEOUT']
        ]
        
        for session_id in expired_sessions:
            del self._user_sessions[session_id] 