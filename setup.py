"""
Setup configuration for Orgaplex-Analyzer Software.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read version from __version__.py
version_dict = {}
version_path = Path(__file__).parent / "src" / "__version__.py"
exec(version_path.read_text(), version_dict)

setup(
    name="orgaplex-analyzer",
    version=version_dict["__version__"],
    author=version_dict["__author__"],
    description=version_dict["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/philius19/orgaplex-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "pandas>=2.0.0,<2.2.0",
        "numpy>=1.24.0,<2.0.0",
        "openpyxl>=3.1.0,<4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "orgaplex-gui=src.gui.main_window:launch_gui",
        ],
    },
)
