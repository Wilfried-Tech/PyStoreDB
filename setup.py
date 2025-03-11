from setuptools import setup, find_packages
import re

setup(
    name='PyStoreDB',
    version='0.1.0',
    packages=find_packages(include=['PyStoreDB', 'PyStoreDB.*']),
    description='A simple NoSQL database greatly inspired by Firestore and Django Filters.',
    long_description=re.sub(r':\w+:', '', open('README.md').read()),
    long_description_content_type='text/markdown',
    url='https://github.com/Wilfried-Tech/PyStoreDB',
    license='MIT',
    author='Wilfried Tech',
    author_email='wilfriedtech.dev@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
)
