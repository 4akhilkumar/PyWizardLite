import io
import os
import re
from setuptools import setup

script_folder = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_folder)

# Find version info from module (without importing the module):
with open('pywizardlite/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

# Use the README.md content for the long description:
with io.open("README.md", encoding="utf-8") as fileObj:
    long_description = fileObj.read()

setup(
    name='PyWizardLite',
    version=version,
    url='https://github.com/4akhilkumar/PyWizardLite',
    author='Sai Akhil Kumar Reddy N',
    author_email='4akhilkumar@gmail.com',
    description=('PyWizardLite automates downloading the correct Chrome driver and generates XPath expressions for visible elements using their text.'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache',
    packages=['PyWizardLite'],
    keywords= "Python script, Selenium, ChromeDriver, XPath, Element visibility, Download, Web scraping, Automated testing",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    zip_safe=True
)
