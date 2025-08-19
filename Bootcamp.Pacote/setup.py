"""
Setup.py

    Parameters:
        Nenhum

    Returns:
        Nenhum.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    page_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="bootcamp_claudio",
    version="0.0.1",
    author="my_name",
    author_email="my_email",
    description="My short description",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/portfolio-2025br/bootcamp-python/tree/main/Bootcamp.Pacote",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.10",
)
