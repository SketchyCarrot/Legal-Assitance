from browser_manager import BrowserManager
from form_automator import FormAutomator
from session_manager import SessionManager
from selenium.webdriver.common.by import By
import re
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def example_form_automation():
    """Example demonstrating form automation capabilities"""
    
    # Try Chrome first, fall back to Firefox if Chrome fails
    try:
        browser_type = "chrome"
        with BrowserManager(browser_type=browser_type, headless=True) as browser_manager:
            run_automation(browser_manager)
    except Exception as e:
        logger.warning(f"Chrome automation failed: {str(e)}")
        logger.info("Trying Firefox instead...")
        browser_type = "firefox"
        with BrowserManager(browser_type=browser_type, headless=True) as browser_manager:
            run_automation(browser_manager)

def run_automation(browser_manager):
    """Run the actual automation logic"""
    driver = browser_manager.driver
    
    # Initialize form automator and session manager
    form_automator = FormAutomator(driver)
    session_manager = SessionManager(driver)
    
    try:
        # Example login process
        login_successful = session_manager.handle_login(
            login_url="https://example.com/login",
            username_locator=(By.ID, "username"),
            password_locator=(By.ID, "password"),
            submit_locator=(By.ID, "login-button"),
            username="test_user",
            password="test_password",
            success_indicator=(By.CLASS_NAME, "welcome-message")
        )
        
        if not login_successful:
            logger.error("Login failed")
            return
            
        # Navigate to form page
        driver.get("https://example.com/form")
        
        # Fill text fields
        form_automator.fill_text_field(
            By.NAME, "first_name", "John"
        )
        form_automator.fill_text_field(
            By.NAME, "last_name", "Doe"
        )
        
        # Select from dropdown
        form_automator.select_dropdown(
            By.ID, "country", "United States", by_value=False
        )
        
        # Check checkboxes
        form_automator.click_checkbox(
            By.NAME, "terms", check=True
        )
        form_automator.click_checkbox(
            By.NAME, "newsletter", check=True
        )
        
        # Select radio button
        form_automator.click_radio(
            By.CSS_SELECTOR, "input[name='gender'][value='male']"
        )
        
        # Upload file
        form_automator.upload_file(
            By.ID, "document", "path/to/document.pdf"
        )
        
        # Set date
        form_automator.set_date(
            By.ID, "birth_date", "1990-01-01"
        )
        
        # Validate form before submission
        validation_rules = {
            (By.NAME, "first_name"): {
                "required": True,
                "min_length": 2,
                "max_length": 50
            },
            (By.NAME, "last_name"): {
                "required": True,
                "min_length": 2,
                "max_length": 50
            },
            (By.ID, "email"): {
                "required": True,
                "pattern": re.compile(r"[^@]+@[^@]+\.[^@]+")
            }
        }
        
        validation_results = form_automator.validate_form(validation_rules)
        has_errors = any(
            len(result["errors"]) > 0 
            for result in validation_results.values()
        )
        
        if has_errors:
            logger.error("Form validation failed:")
            for field, result in validation_results.items():
                if result["errors"]:
                    logger.error(f"{field}: {', '.join(result['errors'])}")
            return
        
        # Check for CAPTCHA
        if form_automator.is_captcha_present():
            logger.warning("CAPTCHA detected, manual intervention required")
            return
        
        # Submit form
        form_automator.submit_form(
            By.ID, "submit-button"
        )
        
        # Take screenshot for verification
        screenshot_path = browser_manager.take_screenshot("form_submission")
        logger.info(f"Screenshot saved: {screenshot_path}")
        
        # Save session for later use
        session_manager.save_session("completed_form")
        
    except Exception as e:
        logger.error(f"Error during form automation: {str(e)}")
        screenshot_path = browser_manager.take_screenshot("error_state")
        logger.error(f"Error screenshot saved: {screenshot_path}")

if __name__ == "__main__":
    example_form_automation() 