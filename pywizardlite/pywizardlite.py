"""
PyWizardLite is a python script that automates the process of downloading the suitable version of
chrome driver for the chrome version installed on the machine. It also has the functionality
to generate the xpath of an element on a webpage using the text of the element and the it
will wait for the element to be visible.

Information:
    Supports Windows OS Only

Source/Reference:
    URL: https://github.com/SergeyPirogov/webdriver_manager/
"""
import io
import os
import re
import subprocess
import sys
import time
from zipfile import ZipFile

try:
    from selenium.webdriver.common.by import By
except ImportError:
    raise ImportError("Please install selenium package")

try:
    import requests
except ImportError:
    raise ImportError("Please install requests package")

class ElementNotFound(Exception):
    """
    ElementNotFound is an exception when the element is not found
    """


class PyWizardLite:
    """
    PyWizardLite is a python script that automates the process of downloading the suitable version of
    chrome driver for the chrome version installed on the machine. It also has the functionality
    to generate the xpath of an element on a webpage using the text of the element and the it
    will wait for the element to be visible.
    """
    __COMMANDS = (
        r'(Get-Item -Path "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion',
        r'(Get-Item -Path "$env:PROGRAMFILES\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion',
        r'(Get-Item -Path "$env:PROGRAMFILES (x86)\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion',
        r'(Get-ItemProperty -Path Registry::"HKCU\SOFTWARE\Google\Chrome\BLBeacon").version',
        r'(Get-ItemProperty -Path Registry::"HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome").version'
    )

    def __init__(self):
        """
        Initialize the PyWizardLite class
        """
        self.__file_response = None
        self.__driver = "chromedriver.exe"

    def system_requirements(self) -> bool:
        """
        Check if the system meets the requirements to run this script

        Returns:
            bool: True if the system meets the requirements, False otherwise
        """
        # Check if the system is windows
        if sys.platform == "win32":
            return True
        return False

    def __construct_powershell_commands(self, *commands: tuple) -> str:
        """
        Construct a powershell command with No Profile and ErrorActionPreference set to
        silentlycontinue

        Args:
            *commands (tuple): The commands

        Returns:
            str: The constructed command
        """
        first_hit_template = """$tmp = {expression}; if ($tmp) {{echo $tmp; Exit;}};"""
        script = "$ErrorActionPreference='silentlycontinue'; " + \
            " ".join(first_hit_template.format(expression = e) for e in commands)

        return f'powershell -NoProfile "{script}"'

    def __get_chrome_version(self):
        """
        Get the chrome version

        Returns:
            str: The chrome version or None if not found
        """

        # Construct the powershell command
        script_command = self.__construct_powershell_commands(*self.__COMMANDS)

        with subprocess.Popen(
                script_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                shell=True,
        ) as stream:
            version = stream.communicate()[0].decode()

        return version.strip() if version else None

    def __set_proxy(self, proxy_url: str = None):
        """
        Set the proxy for the script
        """
        if proxy_url:
            return {
                "http": proxy_url,
                "https": proxy_url
            }
        return None

    def __get_request(self, url: str, proxy_url: str = None, _stream = None):
        """
        Get the request

        Args:
            url (str): The url to get the request from
            proxy_url (str, optional): The proxy url. Defaults to None.
            _stream (bool, optional): The stream. Defaults to None.

        Returns:
            requests.models.Response: The response
        """
        set_proxy = self.__set_proxy(proxy_url = proxy_url)
        try:
            response = requests.get(url, proxies = set_proxy, stream = _stream, timeout = 120)
            return response
        except requests.exceptions:
            return None

    def __is_driver_exists(self) -> bool:
        """
        Check if the driver exists
        # os.path.join(os.getcwd(), self.__driver)

        Returns:
            bool: True if the driver exists, False otherwise
        """
        # check driver exists in the current directory
        if os.path.exists(self.__driver):
            return True
        return False

    def __extract_zip(self):
        """
        Extract the zip file
        """
        with ZipFile(io.BytesIO(self.__file_response.content)) as zip_file:
            zip_file.extract(self.__driver)

    def __set_execusion_permission(self):
        """
        Set the execution permission for the extracted file
        """
        # Set execute permissions on the ChromeDriver binary
        os.chmod(self.__driver, 0o755)

    def driver_download_path(self) -> str:
        """
        Get the driver download path
        """
        self.download_path = str(os.path.join(os.getcwd(), self.__driver))
        return self.download_path

    def __download_chrome_web_driver(self, proxy_url: str = None):
        """
        Download the chrome web driver

        Args:
            proxy_url (str, optional): The proxy url. Defaults to None.
        """
        base_url = "https://chromedriver.storage.googleapis.com"

        # Get the chrome version
        machine_chrome_version = self.__get_chrome_version()

        # Get the major version of chrome
        major_version = re.search(r"^\d+", machine_chrome_version).group()

        # Get the latest version of ChromeDriver for the major version
        version_latest_release = f"{base_url}/LATEST_RELEASE_{major_version}"

        # Get the response - the latest release in the major version
        ver_lat_rel = self.__get_request(version_latest_release, proxy_url = proxy_url).text.strip()

        # Get the content response
        content_response = f"{base_url}/{ver_lat_rel}/chromedriver_win32.zip"

        # Get the response - the content response
        self.__file_response = self.__get_request(content_response,
                                                proxy_url = proxy_url, _stream = True)

        # Extract the zip file
        self.__extract_zip()

        # Set the execution permission
        self.__set_execusion_permission()

        # Get the download path
        self.driver_download_path()

    def setup_chrome_web_driver(self, proxy_url: str = None):
        """
        Setup the chrome web driver

        Args:
            proxy_url (str, optional): The proxy url. Defaults to None.
        """
        # Check if the system meets the requirements
        if self.system_requirements():
            if self.__is_driver_exists():
                return self.driver_download_path()
            # Download the chrome web driver
            self.__download_chrome_web_driver(proxy_url = proxy_url)
            path = str(self.download_path) if self.download_path else None
            return path
        else:
            print("System does not meet the requirements")
            sys.exit(0)

    def wait_until_element_is_visible(driver, element_by,
                                      element: str, default_time: int = None):
        """
        This function waits until the element is active and default time is 60 seconds

        Args:
            driver (WebDriver Object): The web driver object
            element_by (Web Element Object): Set of supported locator strategies
            Acceptable values are ClassName, CSSSelector, ID, LinkText, Name,
            PartialLinkText, TagName, XPath

            element (Web Element Object): The web element which need to be checked
            default_time (int, Optional): The max time to wait
        """
        element_dict = {
            "ClassName": By.CLASS_NAME,
            "CSSSelector": By.CSS_SELECTOR,
            "ID": By.ID,
            "LinkText": By.LINK_TEXT,
            "Name": By.NAME,
            "PartialLinkText": By.PARTIAL_LINK_TEXT,
            "TagName": By.TAG_NAME,
            "XPath": By.XPATH
        }

        if default_time is None:
            wait_time = 60
        else:
            wait_time = default_time

        found_wait_time = 1
        start_time = time.time()

        while True:
            end_time = time.time()
            total_time = int(end_time - start_time)
            if total_time >= wait_time:
                raise ElementNotFound(f'The element - {element} not found within the limited time!')

            try:
                is_web_element_found = driver.find_element(element_dict[element_by], element)
                if is_web_element_found is not None:
                    is_element_found = True
            except ElementNotFound:
                is_element_found = False

            if is_element_found:
                time.sleep(found_wait_time)
                break
            time.sleep(1)

    def wait_until_css_condition(driver, element_by,
                                 element: str, css_prop: str, css_value: str, default_time: int = None):
        """
        This function waits until the css condition met and default time is 60 seconds

        Args:
            element_by (Web Element Object): Set of supported locator strategies
            Acceptable values are ClassName, CSSSelector, ID, LinkText, Name,
            PartialLinkText, TagName, XPath

            css_prop (str): The CSS property of the element
            css_value (str): The CSS value of that property

            element (Web Element Object): The web element which need to be checked
            default_time (int, Optional): The max time to wait
        """
        element_dict = {
            "ClassName": By.CLASS_NAME,
            "CSSSelector": By.CSS_SELECTOR,
            "ID": By.ID,
            "LinkText": By.LINK_TEXT,
            "Name": By.NAME,
            "PartialLinkText": By.PARTIAL_LINK_TEXT,
            "TagName": By.TAG_NAME,
            "XPath": By.XPATH
        }

        if default_time is None:
            wait_time = 60
        else:
            wait_time = default_time

        found_wait_time = 1
        start_time = time.time()

        while True:
            condition = False
            end_time = time.time()
            total_time = int(end_time - start_time)
            if total_time >= wait_time:
                raise Exception(f'The element - {element} not found within the limited time!')

            try:
                is_web_element_found = driver.find_element(element_dict[element_by], element)
                if is_web_element_found is not None:
                    # Now fetch the inline style of the element
                    inline_style = is_web_element_found.get_attribute('style')
                    # Store the css property and value in a dictionary
                    style_dict = {}
                    for each_style in inline_style.split(';'):
                        if each_style != '':
                            prop, value = each_style.split(':')
                            style_dict[prop.strip()] = value.strip()
                    # Check the condition
                    if style_dict[css_prop] == css_value:
                        condition = True
                    is_element_found = True
            except Exception:
                is_element_found = False
                condition = False

            if is_element_found and condition:
                time.sleep(found_wait_time)
                break
            time.sleep(1)

    def generate_string_xpath(driver, text: str):
        """
        Generate the xpath of the string

        Args:
            driver (selenium.webdriver.chrome.webdriver.WebDriver): The driver
            text (str): The text to generate the xpath for

        Returns:
            str: The xpath of the string or None if not found
        """

        __js_code_1 = f'''
        const searchText = "{text}".trim();
        '''
        __js_code_2 = '''
        const xpathExpr = `//*[contains(text(), '${searchText}')]`;

        const xpathResult = document.evaluate(
        xpathExpr,
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
        );

        const node = xpathResult.singleNodeValue;

        if (node !== null) {
        const element = node.closest('[name],[id]');
        if (element !== null) {
            const name = element.getAttribute('name');
            const id = element.getAttribute('id');
        }
        const xpath = getXPath(node);
        return xpath;
        } else {
        // `No element with text "${searchText}" found in document`
        return;
        }

        function getXPath(node) {
        if (node.nodeType === Node.DOCUMENT_NODE) {
            return "/";
        }

        const element = node instanceof Element ? node : node.parentNode;
        const tagName = element.tagName.toLowerCase();
        const parent = element.parentNode;

        if (!parent) {
            return `/${tagName}`;
        }

        const siblings = Array.from(parent.childNodes).filter(
            (node) =>
            node.nodeType === Node.ELEMENT_NODE &&
            node.tagName.toLowerCase() === tagName
        );
        const index = siblings.indexOf(element) + 1;

        return `${getXPath(parent)}/${tagName}[${index}]`;
        }
        '''
        __js_code = __js_code_1 + __js_code_2
        __xpath = driver.execute_script(__js_code)
        return __xpath
