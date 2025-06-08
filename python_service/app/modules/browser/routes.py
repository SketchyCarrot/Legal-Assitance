from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..browser.browser_pool import BrowserPool
import logging

bp = Blueprint('browser', __name__)
logger = logging.getLogger(__name__)
browser_pool = BrowserPool()

@bp.route('/navigate', methods=['POST'])
@jwt_required()
def navigate():
    """Navigate to a URL and get page information."""
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
            screenshot = browser_pool.take_screenshot(browser, 'page.png')
            
            return jsonify({
                'success': True,
                'url': browser.current_url,
                'title': browser.title,
                'screenshot': screenshot
            })
        finally:
            browser_pool.release_browser(browser)

    except Exception as e:
        logger.error(f"Navigation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/status', methods=['GET'])
@jwt_required()
def status():
    """Get browser pool status."""
    try:
        return jsonify({
            'success': True,
            'available_browsers': browser_pool.available_browsers.qsize(),
            'active_browsers': len(browser_pool.active_browsers)
        })
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/cleanup', methods=['POST'])
@jwt_required()
def cleanup():
    """Clean up browser resources."""
    try:
        browser_pool.cleanup()
        return jsonify({
            'success': True,
            'message': 'Browser resources cleaned up'
        })
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 