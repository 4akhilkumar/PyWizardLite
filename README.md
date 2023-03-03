# PyWizardLite
PyWizardLite is a python script that automates the process of downloading the suitable version of
chrome driver for the chrome version installed on the machine. It also has the functionality
to generate the xpath of an element on a webpage using the text of the element and the it
will wait for the element to be visible.

* Support Windows OS Only
* Source/Reference - [SergeyPirogov/webdriver_manager](https://github.com/SergeyPirogov/webdriver_manager/)

## Requirements
### Modules - selenium, requests
```
python -m pip install selenium requests
```

## Installation
```python -m pip install pywizardlite```

## Usage
```python
from pywizardlite import PyWizardLite

# Download suitable version of chrome driver for the chrome version installed on the machine
PyWizardLite().setup_chrome_web_driver(
    proxy_url = "https://proxy.com:8080"
)


# Generate XPath of an element using String
xpath = PyWizardLite().generate_string_xpath(
    driver = driver, text = "Some Text"
)
print(xpath)
# Output could be //*[@id="some_id"] or None


# Wait for an element to be visible
PyWizardLite().wait_until_element_is_visible(
    driver = driver, element_by = "ID", element = "some_id"
)

```
