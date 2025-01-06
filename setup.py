from setuptools import setup, find_packages

setup(
    name="edu_flow2",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'crewai',
        'langtrace-python-sdk',
        'pydantic',
        'python-dotenv',
        'hubspot-api-client'
    ],
) 