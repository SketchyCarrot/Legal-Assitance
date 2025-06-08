from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import json
import logging
from config.security_config import SECURITY_CONFIG
from services.encryption_service import EncryptionService

class ComplianceService:
    def __init__(self):
        """Initialize compliance service"""
        self.encryption_service = EncryptionService()
        self._user_consents = {}
        self._data_processing_records = {}
        self._privacy_notices = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def record_consent(self, user_id: str, purpose: str, data_categories: List[str]) -> Dict:
        """
        Record user consent for data processing
        :param user_id: User ID
        :param purpose: Purpose of data processing
        :param data_categories: Categories of data being processed
        :return: Consent record
        """
        consent_record = {
            'user_id': user_id,
            'purpose': purpose,
            'data_categories': data_categories,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'valid_until': (
                datetime.now(timezone.utc) + 
                SECURITY_CONFIG['COMPLIANCE']['CONSENT_EXPIRY']
            ).isoformat(),
            'privacy_policy_version': SECURITY_CONFIG['COMPLIANCE']['PRIVACY_POLICY_VERSION'],
            'tos_version': SECURITY_CONFIG['COMPLIANCE']['TOS_VERSION']
        }
        
        if user_id not in self._user_consents:
            self._user_consents[user_id] = []
        
        self._user_consents[user_id].append(consent_record)
        self.logger.info(f"Recorded consent for user {user_id} for purpose: {purpose}")
        
        return consent_record

    def verify_consent(self, user_id: str, purpose: str) -> bool:
        """
        Verify if user has given consent for specific purpose
        :param user_id: User ID
        :param purpose: Purpose to check consent for
        :return: True if valid consent exists, False otherwise
        """
        if user_id not in self._user_consents:
            return False
            
        current_time = datetime.now(timezone.utc)
        
        # Check for valid consent
        for consent in self._user_consents[user_id]:
            if (consent['purpose'] == purpose and
                datetime.fromisoformat(consent['valid_until']) > current_time):
                return True
                
        return False

    def withdraw_consent(self, user_id: str, purpose: Optional[str] = None):
        """
        Withdraw user consent
        :param user_id: User ID
        :param purpose: Optional specific purpose to withdraw consent for
        """
        if user_id not in self._user_consents:
            return
            
        if purpose:
            # Withdraw consent for specific purpose
            self._user_consents[user_id] = [
                consent for consent in self._user_consents[user_id]
                if consent['purpose'] != purpose
            ]
            self.logger.info(f"Withdrawn consent for user {user_id} for purpose: {purpose}")
        else:
            # Withdraw all consents
            self._user_consents[user_id] = []
            self.logger.info(f"Withdrawn all consents for user {user_id}")

    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize sensitive data fields
        :param data: Data to anonymize
        :return: Anonymized data
        """
        anonymized_data = data.copy()
        
        for field in SECURITY_CONFIG['DATA_PROTECTION']['ANONYMIZATION_FIELDS']:
            if field in anonymized_data:
                if isinstance(anonymized_data[field], str):
                    # Replace with anonymized version
                    anonymized_data[field] = self._generate_anonymous_value(field)
                elif isinstance(anonymized_data[field], dict):
                    # Recursively anonymize nested data
                    anonymized_data[field] = self.anonymize_data(anonymized_data[field])
                    
        return anonymized_data

    def _generate_anonymous_value(self, field_type: str) -> str:
        """
        Generate anonymous value for a field
        :param field_type: Type of field to generate value for
        :return: Anonymous value
        """
        if field_type == 'email':
            return 'anonymous@example.com'
        elif field_type in ['name', 'address']:
            return 'REDACTED'
        elif field_type == 'phone':
            return '+00000000000'
        elif field_type == 'ip_address':
            return '0.0.0.0'
        else:
            return 'ANONYMIZED'

    def record_processing_activity(self, activity_type: str, data_categories: List[str],
                                 purpose: str, user_id: Optional[str] = None):
        """
        Record data processing activity for GDPR compliance
        :param activity_type: Type of processing activity
        :param data_categories: Categories of data being processed
        :param purpose: Purpose of processing
        :param user_id: Optional user ID
        """
        record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'activity_type': activity_type,
            'data_categories': data_categories,
            'purpose': purpose,
            'user_id': user_id,
            'processor': 'Legal Assistant System',
            'legal_basis': self._determine_legal_basis(purpose)
        }
        
        activity_id = f"{activity_type}_{datetime.now(timezone.utc).timestamp()}"
        self._data_processing_records[activity_id] = record
        
        self.logger.info(f"Recorded processing activity: {activity_type} for purpose: {purpose}")

    def _determine_legal_basis(self, purpose: str) -> str:
        """
        Determine legal basis for data processing
        :param purpose: Purpose of processing
        :return: Legal basis
        """
        # Map common purposes to legal bases
        purpose_mapping = {
            'user_registration': 'contract',
            'legal_consultation': 'contract',
            'marketing': 'consent',
            'compliance': 'legal_obligation',
            'security': 'legitimate_interests'
        }
        
        return purpose_mapping.get(purpose, 'consent')

    def handle_data_request(self, user_id: str, request_type: str) -> Dict:
        """
        Handle data subject request (GDPR)
        :param user_id: User ID
        :param request_type: Type of request (access, deletion, portability)
        :return: Response data
        """
        if request_type == 'access':
            # Collect all user data
            user_data = self._collect_user_data(user_id)
            return {
                'status': 'success',
                'data': user_data
            }
            
        elif request_type == 'deletion':
            # Handle data deletion
            self._delete_user_data(user_id)
            return {
                'status': 'success',
                'message': 'User data has been deleted'
            }
            
        elif request_type == 'portability':
            # Export user data in portable format
            user_data = self._collect_user_data(user_id)
            return {
                'status': 'success',
                'data': user_data,
                'format': 'json'
            }
            
        else:
            raise ValueError(f"Unsupported request type: {request_type}")

    def _collect_user_data(self, user_id: str) -> Dict:
        """
        Collect all data associated with a user
        :param user_id: User ID
        :return: Collected user data
        """
        user_data = {
            'consents': self._user_consents.get(user_id, []),
            'processing_activities': [
                record for record in self._data_processing_records.values()
                if record.get('user_id') == user_id
            ]
        }
        
        return user_data

    def _delete_user_data(self, user_id: str):
        """
        Delete all data associated with a user
        :param user_id: User ID
        """
        # Remove consents
        self._user_consents.pop(user_id, None)
        
        # Remove processing records
        self._data_processing_records = {
            k: v for k, v in self._data_processing_records.items()
            if v.get('user_id') != user_id
        }
        
        self.logger.info(f"Deleted all data for user {user_id}")

    def update_privacy_notice(self, version: str, content: str):
        """
        Update privacy notice
        :param version: Version of the privacy notice
        :param content: Content of the privacy notice
        """
        self._privacy_notices[version] = {
            'content': content,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.info(f"Updated privacy notice to version {version}")

    def get_privacy_notice(self, version: Optional[str] = None) -> Dict:
        """
        Get privacy notice
        :param version: Optional specific version to retrieve
        :return: Privacy notice content
        """
        if version:
            return self._privacy_notices.get(version, {})
        else:
            # Get latest version
            latest_version = SECURITY_CONFIG['COMPLIANCE']['PRIVACY_POLICY_VERSION']
            return self._privacy_notices.get(latest_version, {}) 