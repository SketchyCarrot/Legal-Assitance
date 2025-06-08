from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
from datetime import datetime
import os
import logging

class FormAutomator:
    def __init__(self, driver, timeout=10):
        """
        Initialize form automator with WebDriver instance
        :param driver: Selenium WebDriver instance
        :param timeout: Default timeout for element waits
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def wait_for_element(self, locator_type, locator_value, timeout=None):
        """
        Wait for element to be present and visible
        :param locator_type: By.ID, By.NAME, By.CLASS_NAME, etc.
        :param locator_value: Value of the locator
        :param timeout: Optional custom timeout
        :return: WebElement if found
        """
        timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((locator_type, locator_value))
            )
            return element
        except TimeoutException:
            self.logger.error(f"Element not found: {locator_type}={locator_value}")
            raise

    def fill_text_field(self, locator_type, locator_value, text):
        """
        Fill a text input field
        :param locator_type: By.ID, By.NAME, etc.
        :param locator_value: Value of the locator
        :param text: Text to enter
        """
        element = self.wait_for_element(locator_type, locator_value)
        element.clear()
        element.send_keys(text)

    def select_dropdown(self, locator_type, locator_value, value, by_value=True):
        """
        Select option from dropdown
        :param locator_type: By.ID, By.NAME, etc.
        :param locator_value: Value of the locator
        :param value: Value or visible text to select
        :param by_value: If True, select by value, else by visible text
        """
        element = self.wait_for_element(locator_type, locator_value)
        select = Select(element)
        if by_value:
            select.select_by_value(value)
        else:
            select.select_by_visible_text(value)

    def click_checkbox(self, locator_type, locator_value, check=True):
        """
        Check or uncheck a checkbox
        :param locator_type: By.ID, By.NAME, etc.
        :param locator_value: Value of the locator
        :param check: True to check, False to uncheck
        """
        element = self.wait_for_element(locator_type, locator_value)
        if element.is_selected() != check:
            element.click()

    def click_radio(self, locator_type, locator_value):
        """
        Click a radio button
        :param locator_type: By.ID, By.NAME, etc.
        :param locator_value: Value of the locator
        """
        element = self.wait_for_element(locator_type, locator_value)
        element.click()

    def upload_file(self, locator_type, locator_value, file_path):
        """
        Upload a file
        :param locator_type: By.ID, By.NAME, etc.
        :param locator_value: Value of the locator
        :param file_path: Path to the file to upload
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        element = self.wait_for_element(locator_type, locator_value)
        element.send_keys(os.path.abspath(file_path))

    def set_date(self, locator_type, locator_value, date_value):
        """
        Set date in a date picker
        :param locator_type: By.ID, By.NAME, etc.
        :param locator_value: Value of the locator
        :param date_value: Date string in YYYY-MM-DD format
        """
        try:
            # Try to set date using standard input
            element = self.wait_for_element(locator_type, locator_value)
            self.driver.execute_script(
                f"arguments[0].value = '{date_value}'", element
            )
        except Exception as e:
            self.logger.error(f"Failed to set date: {str(e)}")
            raise

    def submit_form(self, submit_button_locator_type, submit_button_locator_value):
        """
        Submit the form
        :param submit_button_locator_type: By.ID, By.NAME, etc.
        :param submit_button_locator_value: Value of the locator
        """
        submit_button = self.wait_for_element(
            submit_button_locator_type, 
            submit_button_locator_value
        )
        submit_button.click()

    def is_captcha_present(self):
        """
        Check if CAPTCHA is present on the page
        :return: Boolean indicating CAPTCHA presence
        """
        captcha_identifiers = [
            (By.ID, "recaptcha"),
            (By.CLASS_NAME, "g-recaptcha"),
            (By.TAG_NAME, "iframe[title*='reCAPTCHA']"),
        ]
        
        for locator_type, locator_value in captcha_identifiers:
            try:
                self.driver.find_element(locator_type, locator_value)
                return True
            except NoSuchElementException:
                continue
        return False

    def validate_form(self, validation_rules):
        """
        Validate form fields based on rules
        :param validation_rules: Dictionary of field locators and their validation rules
        :return: Dictionary of validation results
        """
        validation_results = {}
        
        for field, rules in validation_rules.items():
            locator_type, locator_value = field
            element = self.wait_for_element(locator_type, locator_value)
            
            value = element.get_attribute("value")
            field_name = element.get_attribute("name") or locator_value
            
            validation_results[field_name] = {
                "value": value,
                "errors": []
            }
            
            # Required field validation
            if rules.get("required", False) and not value:
                validation_results[field_name]["errors"].append("Field is required")
                
            # Length validation
            min_length = rules.get("min_length")
            max_length = rules.get("max_length")
            if min_length and len(value) < min_length:
                validation_results[field_name]["errors"].append(
                    f"Minimum length should be {min_length}"
                )
            if max_length and len(value) > max_length:
                validation_results[field_name]["errors"].append(
                    f"Maximum length should be {max_length}"
                )
                
            # Pattern validation
            pattern = rules.get("pattern")
            if pattern and not pattern.match(value):
                validation_results[field_name]["errors"].append(
                    "Value does not match required pattern"
                )
                
        return validation_results 