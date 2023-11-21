from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='llamp',
    version='0.0.2',
    description='LLAMP - Large Language Model for Planning',
    long_description=long_description,
    long_description_content_type="markdown",
    author='Nikolai Rozanov',
    author_email='nikolai.rozanov@gmail.com',
    # url='',
    packages=find_packages(include=['llamp']),
    install_requires=[],
    # entry_points={
    #     'console_scripts': ['my-command=exampleproject.example:main']
    # },
    # package_data={'exampleproject': ['data/schema.json']}
)

