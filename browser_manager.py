from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import os
from datetime import datetime
import subprocess
import re
import logging

class BrowserManager:
    def __init__(self, browser_type="chrome", headless=False):
        """
        Initialize browser manager with specified browser type and mode
        :param browser_type: chrome, firefox, or edge
        :param headless: boolean to run browser in headless mode
        """
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.driver = None
        self.screenshot_dir = "screenshots"
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_chrome_version(self):
        """Get the version of Chrome browser installed on the system"""
        try:
            # Try Windows registry first
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return version
            except:
                pass

            # Try checking common Chrome installation paths
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\Application\chrome.exe"
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    # Get file version info using wmic
                    try:
                        result = subprocess.check_output(
                            f'wmic datafile where name="{path.replace(os.sep, os.sep+os.sep)}" get Version /value',
                            shell=True
                        ).decode()
                        version_match = re.search(r"Version=(.+)", result)
                        if version_match:
                            return version_match.group(1)
                    except:
                        continue

            # If all else fails, use a default version
            self.logger.warning("Could not detect Chrome version, using default version 120.0.0")
            return "120.0.0"

        except Exception as e:
            self.logger.error(f"Error detecting Chrome version: {str(e)}")
            return "120.0.0"

    def init_browser(self):
        """Initialize the browser with appropriate options"""
        try:
            if self.browser_type == "chrome":
                options = ChromeOptions()
                if self.headless:
                    options.add_argument("--headless=new")  # Updated headless mode syntax
                options.add_argument("--start-maximized")
                options.add_argument("--disable-notifications")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_experimental_option("excludeSwitches", ["enable-logging"])
                
                # Set Chrome version for ChromeDriverManager
                chrome_version = self.get_chrome_version()
                self.logger.info(f"Detected Chrome version: {chrome_version}")
                
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager(version=chrome_version).install()),
                    options=options
                )
                
            elif self.browser_type == "firefox":
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                self.driver = webdriver.Firefox(
                    service=Service(GeckoDriverManager().install()),
                    options=options
                )
                
            elif self.browser_type == "edge":
                options = EdgeOptions()
                if self.headless:
                    options.add_argument("--headless")
                self.driver = webdriver.Edge(
                    service=Service(EdgeChromiumDriverManager().install()),
                    options=options
                )
                
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")

            return self.driver

        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    def take_screenshot(self, name=None):
        """
        Take a screenshot of the current page
        :param name: Optional name for the screenshot
        :return: Path to the saved screenshot
        """
        if not self.driver:
            raise Exception("Browser not initialized")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png" if name else f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        self.driver.save_screenshot(filepath)
        return filepath

    def quit(self):
        """Close the browser and cleanup"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        """Context manager entry"""
        self.init_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.quit() 