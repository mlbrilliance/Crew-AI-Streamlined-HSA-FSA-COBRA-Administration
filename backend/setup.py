from setuptools import setup, find_packages

setup(
    name="hsa_fsa_cobra_admin",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "crewai>=0.10.0",
        "pydantic>=2.5.2",
        "python-multipart>=0.0.6",
        "httpx>=0.25.2"
    ],
) 