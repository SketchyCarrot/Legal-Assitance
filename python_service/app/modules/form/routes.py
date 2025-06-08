from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..browser.browser_pool import BrowserPool
from ..form.form_analyzer import FormAnalyzer
import logging

bp = Blueprint('form', __name__)
logger = logging.getLogger(__name__)
browser_pool = BrowserPool()
form_analyzer = FormAnalyzer()

@bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_form():
    """Analyze a form on a webpage."""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400

        browser = browser_pool.acquire_browser()
        try:
            browser.get(url)
            analysis = form_analyzer.analyze_page(browser)
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
        finally:
            browser_pool.release_browser(browser)

    except Exception as e:
        logger.error(f"Form analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/detect-type', methods=['POST'])
@jwt_required()
def detect_form_type():
    """Detect the type of form on a webpage."""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400

        browser = browser_pool.acquire_browser()
        try:
            browser.get(url)
            analysis = form_analyzer.analyze_page(browser)
            
            form_types = [
                form.get('form_type', 'unknown')
                for form in analysis.get('forms', [])
            ]
            
            return jsonify({
                'success': True,
                'form_types': form_types
            })
        finally:
            browser_pool.release_browser(browser)

    except Exception as e:
        logger.error(f"Form type detection error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/extract-schema', methods=['POST'])
@jwt_required()
def extract_form_schema():
    """Extract the schema of a form on a webpage."""
    try:
        data = request.get_json()
        url = data.get('url')
        form_index = data.get('form_index', 0)
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400

        browser = browser_pool.acquire_browser()
        try:
            browser.get(url)
            analysis = form_analyzer.analyze_page(browser)
            
            if not analysis.get('forms'):
                return jsonify({
                    'success': False,
                    'error': 'No forms found on the page'
                }), 404

            if form_index >= len(analysis['forms']):
                return jsonify({
                    'success': False,
                    'error': 'Form index out of range'
                }), 400

            form_schema = analysis['forms'][form_index]
            return jsonify({
                'success': True,
                'schema': form_schema
            })
        finally:
            browser_pool.release_browser(browser)

    except Exception as e:
        logger.error(f"Schema extraction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 