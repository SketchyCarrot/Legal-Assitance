from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
import logging
from typing import Dict, List, Optional, Tuple

class FormAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.common_field_patterns = {
            'name': r'name|full[_\s-]*name|first[_\s-]*name|last[_\s-]*name',
            'email': r'email|e-mail|mail',
            'phone': r'phone|mobile|contact|tel',
            'address': r'address|location|residence',
            'date': r'date|dob|birth|day|month|year',
            'id': r'id|identification|aadhar|pan|passport',
            'case': r'case|matter|petition|filing',
            'court': r'court|tribunal|forum|jurisdiction'
        }

    def analyze_page(self, browser) -> Dict:
        """Analyze the webpage and extract form information."""
        try:
            # Wait for form elements to be present
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )

            # Get page source and parse with BeautifulSoup
            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            forms = soup.find_all('form')
            return {
                'form_count': len(forms),
                'forms': [self._analyze_form(form) for form in forms]
            }
        except Exception as e:
            self.logger.error(f"Error analyzing page: {str(e)}")
            return {'error': str(e)}

    def _analyze_form(self, form) -> Dict:
        """Analyze a single form and its fields."""
        form_data = {
            'id': form.get('id', ''),
            'name': form.get('name', ''),
            'method': form.get('method', 'get'),
            'action': form.get('action', ''),
            'fields': [],
            'required_fields': [],
            'field_groups': [],
            'form_type': self._detect_form_type(form)
        }

        fields = self._extract_form_fields(form)
        form_data['fields'] = fields
        form_data['required_fields'] = [
            field for field in fields 
            if field.get('required', False)
        ]
        form_data['field_groups'] = self._group_related_fields(fields)

        return form_data

    def _extract_form_fields(self, form) -> List[Dict]:
        """Extract and analyze all form fields."""
        fields = []
        
        # Process input fields
        for input_field in form.find_all('input'):
            field_info = self._analyze_input_field(input_field)
            if field_info:
                fields.append(field_info)

        # Process select fields
        for select in form.find_all('select'):
            field_info = self._analyze_select_field(select)
            if field_info:
                fields.append(field_info)

        # Process textarea fields
        for textarea in form.find_all('textarea'):
            field_info = self._analyze_textarea_field(textarea)
            if field_info:
                fields.append(field_info)

        return fields

    def _analyze_input_field(self, input_field) -> Optional[Dict]:
        """Analyze an input field and its attributes."""
        try:
            field_type = input_field.get('type', 'text')
            if field_type in ['submit', 'button', 'reset', 'hidden']:
                return None

            field_info = {
                'type': field_type,
                'name': input_field.get('name', ''),
                'id': input_field.get('id', ''),
                'required': input_field.has_attr('required'),
                'placeholder': input_field.get('placeholder', ''),
                'value': input_field.get('value', ''),
                'pattern': input_field.get('pattern', ''),
                'field_category': self._categorize_field(input_field)
            }

            # Add validation rules
            validation = []
            if input_field.get('minlength'):
                validation.append(f"minlength={input_field['minlength']}")
            if input_field.get('maxlength'):
                validation.append(f"maxlength={input_field['maxlength']}")
            if input_field.get('pattern'):
                validation.append(f"pattern={input_field['pattern']}")
            
            field_info['validation'] = validation
            return field_info
        except Exception as e:
            self.logger.error(f"Error analyzing input field: {str(e)}")
            return None

    def _analyze_select_field(self, select) -> Optional[Dict]:
        """Analyze a select field and its options."""
        try:
            options = []
            for option in select.find_all('option'):
                options.append({
                    'value': option.get('value', ''),
                    'text': option.text.strip(),
                    'selected': option.has_attr('selected')
                })

            return {
                'type': 'select',
                'name': select.get('name', ''),
                'id': select.get('id', ''),
                'required': select.has_attr('required'),
                'options': options,
                'multiple': select.has_attr('multiple'),
                'field_category': self._categorize_field(select)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing select field: {str(e)}")
            return None

    def _analyze_textarea_field(self, textarea) -> Optional[Dict]:
        """Analyze a textarea field."""
        try:
            return {
                'type': 'textarea',
                'name': textarea.get('name', ''),
                'id': textarea.get('id', ''),
                'required': textarea.has_attr('required'),
                'placeholder': textarea.get('placeholder', ''),
                'rows': textarea.get('rows', ''),
                'cols': textarea.get('cols', ''),
                'field_category': self._categorize_field(textarea)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing textarea field: {str(e)}")
            return None

    def _detect_form_type(self, form) -> str:
        """Detect the type of form based on its fields and attributes."""
        form_text = form.get_text().lower()
        form_html = str(form).lower()
        
        if any(word in form_text for word in ['login', 'signin', 'sign in']):
            return 'login'
        elif any(word in form_text for word in ['register', 'signup', 'sign up']):
            return 'registration'
        elif any(word in form_text for word in ['petition', 'complaint', 'file']):
            return 'legal_filing'
        elif any(word in form_text for word in ['contact', 'enquiry', 'inquiry']):
            return 'contact'
        else:
            return 'unknown'

    def _categorize_field(self, field) -> str:
        """Categorize a field based on its attributes and common patterns."""
        field_attrs = ' '.join([
            str(field.get('name', '')),
            str(field.get('id', '')),
            str(field.get('placeholder', ''))
        ]).lower()

        for category, pattern in self.common_field_patterns.items():
            if re.search(pattern, field_attrs):
                return category

        return 'other'

    def _group_related_fields(self, fields: List[Dict]) -> List[Dict]:
        """Group related fields together based on their names and categories."""
        groups = []
        processed_fields = set()

        for field in fields:
            if field['name'] in processed_fields:
                continue

            related_fields = []
            base_name = field['name'].rstrip('0123456789')

            # Find related fields
            for other_field in fields:
                other_base_name = other_field['name'].rstrip('0123456789')
                if (base_name == other_base_name or 
                    self._are_fields_related(field, other_field)):
                    related_fields.append(other_field)
                    processed_fields.add(other_field['name'])

            if related_fields:
                groups.append({
                    'name': base_name,
                    'fields': related_fields,
                    'type': 'group'
                })

        return groups

    def _are_fields_related(self, field1: Dict, field2: Dict) -> bool:
        """Check if two fields are related based on their names and categories."""
        name1 = field1['name'].lower()
        name2 = field2['name'].lower()

        # Check for common prefixes/suffixes
        if (name1.startswith(name2) or name2.startswith(name1) or
            name1.endswith(name2) or name2.endswith(name1)):
            return True

        # Check if fields are part of the same category
        if (field1.get('field_category') == field2.get('field_category') and
            field1.get('field_category') != 'other'):
            return True

        return False 