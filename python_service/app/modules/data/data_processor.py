from typing import Dict, List, Optional, Any
import re
from fuzzywuzzy import fuzz
import json
import logging
from datetime import datetime

class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.field_validators = {
            'name': self._validate_name,
            'email': self._validate_email,
            'phone': self._validate_phone,
            'date': self._validate_date,
            'id': self._validate_id
        }

    def process_form_data(self, form_schema: Dict, user_data: Dict) -> Dict:
        """Process and validate form data against the form schema."""
        try:
            processed_data = {}
            errors = []
            missing_fields = []

            # Process required fields first
            for field in form_schema.get('required_fields', []):
                field_name = field['name']
                if field_name not in user_data:
                    missing_fields.append(field_name)
                    continue

                result = self._process_field(field, user_data[field_name])
                if result['valid']:
                    processed_data[field_name] = result['value']
                else:
                    errors.append({
                        'field': field_name,
                        'error': result['error']
                    })

            # Process optional fields
            for field in form_schema.get('fields', []):
                if field['name'] in processed_data:
                    continue

                if field['name'] in user_data:
                    result = self._process_field(field, user_data[field['name']])
                    if result['valid']:
                        processed_data[field['name']] = result['value']
                    else:
                        errors.append({
                            'field': field['name'],
                            'error': result['error']
                        })

            return {
                'success': len(errors) == 0 and len(missing_fields) == 0,
                'processed_data': processed_data,
                'errors': errors,
                'missing_fields': missing_fields
            }

        except Exception as e:
            self.logger.error(f"Error processing form data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def match_fields(self, form_fields: List[Dict], user_data: Dict) -> Dict[str, str]:
        """Match user data fields to form fields using fuzzy matching."""
        matches = {}
        used_form_fields = set()
        
        # First pass: exact matches
        for user_field, value in user_data.items():
            user_field_lower = user_field.lower()
            for form_field in form_fields:
                if form_field['name'].lower() == user_field_lower:
                    matches[user_field] = form_field['name']
                    used_form_fields.add(form_field['name'])
                    break

        # Second pass: fuzzy matching for remaining fields
        for user_field, value in user_data.items():
            if user_field in matches:
                continue

            best_match = None
            best_score = 0
            
            for form_field in form_fields:
                if form_field['name'] in used_form_fields:
                    continue

                score = fuzz.ratio(user_field.lower(), form_field['name'].lower())
                if score > best_score and score > 80:  # 80% similarity threshold
                    best_score = score
                    best_match = form_field['name']

            if best_match:
                matches[user_field] = best_match
                used_form_fields.add(best_match)

        return matches

    def _process_field(self, field: Dict, value: Any) -> Dict:
        """Process and validate a single field."""
        try:
            # Get the appropriate validator based on field category
            validator = self.field_validators.get(
                field.get('field_category'),
                self._validate_generic
            )

            # Apply field-specific validation
            validation_result = validator(value)
            if not validation_result['valid']:
                return validation_result

            # Apply any additional validation rules from the field definition
            for rule in field.get('validation', []):
                if rule.startswith('minlength='):
                    min_length = int(rule.split('=')[1])
                    if len(str(value)) < min_length:
                        return {
                            'valid': False,
                            'error': f'Value must be at least {min_length} characters long'
                        }
                elif rule.startswith('maxlength='):
                    max_length = int(rule.split('=')[1])
                    if len(str(value)) > max_length:
                        return {
                            'valid': False,
                            'error': f'Value must be at most {max_length} characters long'
                        }
                elif rule.startswith('pattern='):
                    pattern = rule.split('=')[1]
                    if not re.match(pattern, str(value)):
                        return {
                            'valid': False,
                            'error': 'Value does not match required pattern'
                        }

            return {
                'valid': True,
                'value': validation_result['value']
            }

        except Exception as e:
            self.logger.error(f"Error processing field: {str(e)}")
            return {
                'valid': False,
                'error': str(e)
            }

    def _validate_generic(self, value: Any) -> Dict:
        """Generic validation for any field."""
        return {
            'valid': True,
            'value': str(value)
        }

    def _validate_name(self, value: str) -> Dict:
        """Validate name fields."""
        if not isinstance(value, str):
            return {
                'valid': False,
                'error': 'Name must be a string'
            }

        value = value.strip()
        if len(value) < 2:
            return {
                'valid': False,
                'error': 'Name must be at least 2 characters long'
            }

        if not re.match(r'^[A-Za-z\s\'-]+$', value):
            return {
                'valid': False,
                'error': 'Name contains invalid characters'
            }

        return {
            'valid': True,
            'value': value
        }

    def _validate_email(self, value: str) -> Dict:
        """Validate email fields."""
        if not isinstance(value, str):
            return {
                'valid': False,
                'error': 'Email must be a string'
            }

        value = value.strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            return {
                'valid': False,
                'error': 'Invalid email format'
            }

        return {
            'valid': True,
            'value': value.lower()
        }

    def _validate_phone(self, value: str) -> Dict:
        """Validate phone number fields."""
        if not isinstance(value, str):
            return {
                'valid': False,
                'error': 'Phone number must be a string'
            }

        # Remove all non-numeric characters
        value = re.sub(r'\D', '', value)

        # Check for valid length (assuming Indian phone numbers)
        if len(value) != 10:
            return {
                'valid': False,
                'error': 'Phone number must be 10 digits'
            }

        return {
            'valid': True,
            'value': value
        }

    def _validate_date(self, value: str) -> Dict:
        """Validate date fields."""
        try:
            # Try parsing the date in multiple formats
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    parsed_date = datetime.strptime(value, fmt)
                    return {
                        'valid': True,
                        'value': parsed_date.strftime('%Y-%m-%d')
                    }
                except ValueError:
                    continue

            return {
                'valid': False,
                'error': 'Invalid date format'
            }
        except Exception:
            return {
                'valid': False,
                'error': 'Invalid date'
            }

    def _validate_id(self, value: str) -> Dict:
        """Validate ID fields (Aadhar, PAN, etc.)."""
        if not isinstance(value, str):
            return {
                'valid': False,
                'error': 'ID must be a string'
            }

        value = value.strip().upper()

        # Validate PAN
        if re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', value):
            return {
                'valid': True,
                'value': value
            }

        # Validate Aadhar (12 digits)
        if re.match(r'^\d{12}$', value):
            return {
                'valid': True,
                'value': value
            }

        return {
            'valid': False,
            'error': 'Invalid ID format'
        } 