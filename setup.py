from setuptools import setup
from setuptools import find_packages

VERSION = '0.1.1'

with open('README.md', 'r', encoding='UTF-8') as f:
    LONG_DESCRIPTION = f.read()

with open('requirements.txt', 'r') as f:
    REQUIREMENTS = list(filter(None, f.read().split('\n')))

setup(
    name='beancount-periodic',
    version=VERSION,
    url='https://github.com/dallaslu/beancount-periodic',
    project_urls={
        "Issue tracker": "https://github.com/dallaslu/beancount-periodic/issues",
    },
    author='Dallas Lu',
    author_email='914202+dallaslu@users.noreply.github.com',
    description='Beancount plugin to generate periodic transactions #Amortize #Depreciate #Recur',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Financial :: Accounting',
    ],
    python_requires='>=3.6',
)
