from setuptools import setup, find_packages

setup(
    name="clip-companion",
    version="0.1.0",
    description="Asistente IA Ambient Basado en Portapapeles",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Santiago Abreo",
    author_email="santiago.abreo@utec.edu.uy",
    url="https://github.com/santiagoabreo-dotcom/clip-companion",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "anthropic>=0.7.0",
        "pyperclip==1.8.2",
        "keyboard>=0.13.5",
        "pillow>=10.0.0",
        "pydantic==2.0.0",
        "python-dotenv==1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clip-companion=clipcompanion.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Office/Business",
        "Topic :: System :: Monitoring",
    ],
    keywords="ai assistant clipboard ambient ui",
    project_urls={
        "Bug Reports": "https://github.com/santiagoabreo-dotcom/clip-companion/issues",
        "Source": "https://github.com/santiagoabreo-dotcom/clip-companion",
    },
)
