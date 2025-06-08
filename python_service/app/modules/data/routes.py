from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..data.data_processor import DataProcessor
import logging

bp = Blueprint('data', __name__)
logger = logging.getLogger(__name__)
data_processor = DataProcessor()

@bp.route('/process', methods=['POST'])
@jwt_required()
def process_data():
    """Process and validate form data."""
    try:
        data = request.get_json()
        form_schema = data.get('form_schema')
        user_data = data.get('user_data')
        
        if not form_schema or not user_data:
            return jsonify({
                'success': False,
                'error': 'Form schema and user data are required'
            }), 400

        result = data_processor.process_form_data(form_schema, user_data)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Data processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/match-fields', methods=['POST'])
@jwt_required()
def match_fields():
    """Match user data fields to form fields."""
    try:
        data = request.get_json()
        form_fields = data.get('form_fields')
        user_data = data.get('user_data')
        
        if not form_fields or not user_data:
            return jsonify({
                'success': False,
                'error': 'Form fields and user data are required'
            }), 400

        matches = data_processor.match_fields(form_fields, user_data)
        return jsonify({
            'success': True,
            'matches': matches
        })

    except Exception as e:
        logger.error(f"Field matching error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_data():
    """Validate specific field data."""
    try:
        data = request.get_json()
        field_type = data.get('field_type')
        value = data.get('value')
        
        if not field_type or value is None:
            return jsonify({
                'success': False,
                'error': 'Field type and value are required'
            }), 400

        validator = data_processor.field_validators.get(field_type)
        if not validator:
            return jsonify({
                'success': False,
                'error': f'No validator found for field type: {field_type}'
            }), 400

        result = validator(value)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Data validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 