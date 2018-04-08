from setuptools import setup, find_packages

setup(
    name='py_yahoo_prices',
    packages=find_packages(),
    version='0.3.1',
    description="Get daily/weekly/monthly returns and prices of equities from yahoo's new tricky endpoint",
    long_description='README.md',
    author = 'Ali Siddiq',
    author_email = 'ali.bin.siddiq@gmail.com',
    url = 'https://github.com/alisiddiq/py_yahoo_prices',
    license='MIT',
    keywords = ['stocks', 'yahoo', 'prices'],
    install_requires = ['pandas', 'requests', 'lxml'],
)