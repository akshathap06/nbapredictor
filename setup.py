from setuptools import setup, find_packages

setup(
    name="nba_predictor_app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mcp",
        "python-dotenv",
        "streamlit",
    ],
) 