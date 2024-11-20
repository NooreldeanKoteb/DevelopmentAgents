from setuptools import setup, find_packages

setup(
    name="autonomous-ai-dev",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "redis>=5.0.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "prometheus-client>=0.19.0",
        "aiohttp>=3.9.0",
    ],
) 