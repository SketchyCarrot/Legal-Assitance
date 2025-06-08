from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from queue import Queue
import threading
import logging
import os

class BrowserPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, pool_size=3):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(BrowserPool, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, pool_size=3):
        if self._initialized:
            return
            
        self.pool_size = pool_size
        self.available_browsers = Queue()
        self.active_browsers = {}
        self.logger = logging.getLogger(__name__)
        self._initialize_pool()
        self._initialized = True

    def _create_browser(self):
        try:
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            
            # Set up ChromeDriver using webdriver_manager
            driver_path = ChromeDriverManager().install()
            service = Service(executable_path=driver_path)
            
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to create browser: {str(e)}")
            return None

    def _initialize_pool(self):
        for _ in range(self.pool_size):
            browser = self._create_browser()
            if browser is not None:
                self.available_browsers.put(browser)
            else:
                self.logger.error("Failed to initialize browser instance")

    def acquire_browser(self):
        try:
            browser = self.available_browsers.get(timeout=30)
            if browser is None:
                browser = self._create_browser()
                if browser is None:
                    raise Exception("Failed to create new browser instance")
                    
            session_id = threading.get_ident()
            self.active_browsers[session_id] = browser
            return browser
        except Exception as e:
            self.logger.error(f"Failed to acquire browser: {str(e)}")
            raise

    def release_browser(self, browser=None):
        session_id = threading.get_ident()
        if browser is None and session_id in self.active_browsers:
            browser = self.active_browsers[session_id]
            del self.active_browsers[session_id]

        if browser:
            try:
                browser.delete_all_cookies()
                self.available_browsers.put(browser)
            except Exception as e:
                self.logger.error(f"Failed to release browser: {str(e)}")
                self._handle_failed_browser(browser)

    def _handle_failed_browser(self, browser):
        try:
            browser.quit()
        except:
            pass
        finally:
            new_browser = self._create_browser()
            if new_browser is not None:
                self.available_browsers.put(new_browser)

    def take_screenshot(self, browser, filename):
        try:
            return browser.get_screenshot_as_png()
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
            return None

    def cleanup(self):
        while not self.available_browsers.empty():
            browser = self.available_browsers.get()
            try:
                browser.quit()
            except:
                pass

        for browser in self.active_browsers.values():
            try:
                browser.quit()
            except:
                pass 