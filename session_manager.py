import json
import os
import pickle
from datetime import datetime, timedelta
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class SessionManager:
    def __init__(self, driver, session_dir="sessions", timeout=30):
        """
        Initialize session manager
        :param driver: Selenium WebDriver instance
        :param session_dir: Directory to store session data
        :param timeout: Session timeout in minutes
        """
        self.driver = driver
        self.session_dir = session_dir
        self.timeout = timeout
        self.current_session = None
        
        # Create session directory if it doesn't exist
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
            
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def save_session(self, session_name):
        """
        Save current session data
        :param session_name: Name to identify the session
        """
        session_data = {
            'cookies': self.driver.get_cookies(),
            'current_url': self.driver.current_url,
            'timestamp': datetime.now().isoformat(),
            'window_handles': self.driver.window_handles,
            'current_window': self.driver.current_window_handle
        }
        
        # Save local storage if available
        try:
            local_storage = self.driver.execute_script(
                "return Object.assign({}, window.localStorage);"
            )
            session_data['local_storage'] = local_storage
        except Exception as e:
            self.logger.warning(f"Could not save local storage: {str(e)}")

        # Save session storage if available
        try:
            session_storage = self.driver.execute_script(
                "return Object.assign({}, window.sessionStorage);"
            )
            session_data['session_storage'] = session_storage
        except Exception as e:
            self.logger.warning(f"Could not save session storage: {str(e)}")

        session_file = os.path.join(self.session_dir, f"{session_name}.json")
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
            
        self.current_session = session_name
        self.logger.info(f"Session saved: {session_name}")

    def load_session(self, session_name):
        """
        Load saved session data
        :param session_name: Name of the session to load
        :return: Boolean indicating success
        """
        session_file = os.path.join(self.session_dir, f"{session_name}.json")
        
        if not os.path.exists(session_file):
            self.logger.error(f"Session file not found: {session_name}")
            return False
            
        with open(session_file, 'r') as f:
            session_data = json.load(f)
            
        # Check session timeout
        last_timestamp = datetime.fromisoformat(session_data['timestamp'])
        if datetime.now() - last_timestamp > timedelta(minutes=self.timeout):
            self.logger.warning(f"Session {session_name} has expired")
            return False

        # Navigate to the saved URL
        self.driver.get(session_data['current_url'])
        
        # Restore cookies
        for cookie in session_data['cookies']:
            self.driver.add_cookie(cookie)
            
        # Restore local storage if available
        if 'local_storage' in session_data:
            for key, value in session_data['local_storage'].items():
                self.driver.execute_script(
                    f"window.localStorage.setItem('{key}', '{value}');"
                )
                
        # Restore session storage if available
        if 'session_storage' in session_data:
            for key, value in session_data['session_storage'].items():
                self.driver.execute_script(
                    f"window.sessionStorage.setItem('{key}', '{value}');"
                )

        self.current_session = session_name
        self.logger.info(f"Session loaded: {session_name}")
        return True

    def handle_login(self, login_url, username_locator, password_locator, 
                    submit_locator, username, password, success_indicator):
        """
        Handle login process and session creation
        :param login_url: URL of the login page
        :param username_locator: Tuple of (By.TYPE, 'locator') for username field
        :param password_locator: Tuple of (By.TYPE, 'locator') for password field
        :param submit_locator: Tuple of (By.TYPE, 'locator') for submit button
        :param username: Username to login with
        :param password: Password to login with
        :param success_indicator: Tuple of (By.TYPE, 'locator') to verify successful login
        :return: Boolean indicating success
        """
        try:
            # Navigate to login page
            self.driver.get(login_url)
            
            # Wait for and fill username
            username_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(username_locator)
            )
            username_element.clear()
            username_element.send_keys(username)
            
            # Fill password
            password_element = self.driver.find_element(*password_locator)
            password_element.clear()
            password_element.send_keys(password)
            
            # Click submit
            submit_element = self.driver.find_element(*submit_locator)
            submit_element.click()
            
            # Wait for success indicator
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(success_indicator)
            )
            
            # Save session
            session_name = f"session_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.save_session(session_name)
            
            return True
            
        except TimeoutException:
            self.logger.error("Login failed: timeout waiting for elements")
            return False
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False

    def manage_windows(self):
        """
        Get information about all open windows/tabs
        :return: Dictionary of window handles and their details
        """
        windows_info = {}
        current_handle = self.driver.current_window_handle
        
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            windows_info[handle] = {
                'title': self.driver.title,
                'url': self.driver.current_url,
                'is_current': handle == current_handle
            }
            
        # Switch back to the original window
        self.driver.switch_to.window(current_handle)
        return windows_info

    def switch_to_window(self, window_handle):
        """
        Switch to specified window/tab
        :param window_handle: Handle of the window to switch to
        :return: Boolean indicating success
        """
        try:
            self.driver.switch_to.window(window_handle)
            return True
        except Exception as e:
            self.logger.error(f"Failed to switch window: {str(e)}")
            return False

    def close_window(self, window_handle=None):
        """
        Close specified window/tab or current window if not specified
        :param window_handle: Handle of the window to close
        """
        if window_handle:
            current_handle = self.driver.current_window_handle
            self.driver.switch_to.window(window_handle)
            self.driver.close()
            if window_handle != current_handle:
                self.driver.switch_to.window(current_handle)
        else:
            self.driver.close()

    def cleanup_expired_sessions(self):
        """
        Remove expired session files
        """
        for filename in os.listdir(self.session_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.session_dir, filename)
                with open(filepath, 'r') as f:
                    session_data = json.load(f)
                    last_timestamp = datetime.fromisoformat(session_data['timestamp'])
                    
                    if datetime.now() - last_timestamp > timedelta(minutes=self.timeout):
                        os.remove(filepath)
                        self.logger.info(f"Removed expired session: {filename}") 