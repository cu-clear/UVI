"""
Setup script for the UVI (Unified Verb Index) package.

This script provides installation configuration for the comprehensive standalone
UVI package that provides integrated access to nine linguistic corpora with
cross-resource navigation, semantic validation, and hierarchical analysis capabilities.
"""

from setuptools import setup, find_packages
from pathlib import Path
import re

# Read the README file for long description
def read_readme():
    """Read README file for package description."""
    readme_path = Path(__file__).parent / 'README.md'
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "UVI (Unified Verb Index) - A comprehensive linguistic corpus integration package"

# Read requirements from requirements.txt if it exists
def read_requirements():
    """Read requirements from requirements.txt file."""
    req_path = Path(__file__).parent / 'requirements.txt'
    if req_path.exists():
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Get version from package __init__.py
def get_version():
    """Extract version from package __init__.py file."""
    init_path = Path(__file__).parent / 'src' / 'uvi' / '__init__.py'
    if init_path.exists():
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
            version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", content)
            if version_match:
                return version_match.group(1)
    return '1.0.0'  # Default version

# Core package information
PACKAGE_NAME = "uvi"
VERSION = get_version()
AUTHOR = "UVI Development Team"
AUTHOR_EMAIL = "uvi-dev@example.com"
DESCRIPTION = "Unified Verb Index: Comprehensive linguistic corpus integration package"
LONG_DESCRIPTION = read_readme()
URL = "https://github.com/yourusername/UVI"
LICENSE = "MIT"

# Python version requirement
PYTHON_REQUIRES = ">=3.8"

# Core dependencies (minimal for basic functionality)
INSTALL_REQUIRES = [
    # Core dependencies - only standard library is required for basic functionality
    # All external dependencies are optional
]

# Optional dependencies for enhanced features
EXTRAS_REQUIRE = {
    'monitoring': [
        'watchdog>=2.1.0',  # For file system monitoring (CorpusMonitor)
    ],
    'performance': [
        'psutil>=5.8.0',     # For performance benchmarking
    ],
    'validation': [
        'lxml>=4.6.0',       # For XML schema validation
    ],
    'dev': [
        'pytest>=6.0.0',
        'pytest-cov>=2.0.0',
        'flake8>=3.8.0',
        'mypy>=0.800',
        'black>=21.0.0',
        'isort>=5.0.0',
    ],
    'docs': [
        'sphinx>=4.0.0',
        'sphinx-rtd-theme>=0.5.0',
        'sphinxcontrib-napoleon>=0.7',
    ],
    'jupyter': [
        'jupyter>=1.0.0',
        'ipywidgets>=7.0.0',
        'matplotlib>=3.0.0',  # For visualization in notebooks
    ]
}

# Add 'all' option that includes everything except dev
EXTRAS_REQUIRE['all'] = (
    EXTRAS_REQUIRE['monitoring'] + 
    EXTRAS_REQUIRE['performance'] + 
    EXTRAS_REQUIRE['validation'] +
    EXTRAS_REQUIRE['jupyter']
)

# Package data to include
PACKAGE_DATA = {
    'uvi': [
        'parsers/*.py',
        'utils/*.py',
        'tests/*.py',
    ]
}

# Entry points for command-line tools
ENTRY_POINTS = {
    'console_scripts': [
        'uvi-validate=uvi.cli:validate_command',
        'uvi-export=uvi.cli:export_command',
        'uvi-benchmark=uvi.cli:benchmark_command',
    ],
}

# Classifiers for PyPI
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Text Processing :: Linguistic',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Natural Language :: English',
]

# Keywords for PyPI search
KEYWORDS = [
    'linguistics', 'nlp', 'corpus', 'verbnet', 'framenet', 'propbank', 
    'wordnet', 'ontonotes', 'semantic-analysis', 'cross-corpus', 
    'linguistic-resources', 'semantic-roles', 'verb-classification'
]

# Project URLs
PROJECT_URLS = {
    'Bug Reports': f'{URL}/issues',
    'Source': URL,
    'Documentation': f'{URL}/docs',
    'Changelog': f'{URL}/blob/master/CHANGELOG.md',
}

setup(
    # Basic package information
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url=URL,
    project_urls=PROJECT_URLS,
    license=LICENSE,
    
    # Package discovery and structure
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data=PACKAGE_DATA,
    include_package_data=True,
    
    # Dependencies
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    
    # Entry points
    entry_points=ENTRY_POINTS,
    
    # PyPI metadata
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    
    # Configuration
    zip_safe=False,  # Allow access to package files
    
    # Test configuration
    test_suite='tests',
    
    # Additional metadata
    platforms=['any'],
)

# Post-installation message
def print_post_install_message():
    """Print helpful information after installation."""
    message = """
    
🎉 UVI (Unified Verb Index) package installed successfully!

🚀 Quick Start:
    from uvi import UVI
    uvi = UVI(corpora_path='path/to/corpora', load_all=False)
    print(f"Available corpora: {list(uvi.get_corpus_paths().keys())}")

📚 Documentation:
    - Package README: src/uvi/README.md
    - Examples: examples/ directory
    - Tests: Run 'python -m pytest tests/' from the project root

🔧 Optional Features:
    pip install uvi[monitoring]    # File system monitoring
    pip install uvi[performance]   # Performance benchmarking  
    pip install uvi[validation]    # XML schema validation
    pip install uvi[all]          # All optional features

💡 Command Line Tools:
    uvi-validate    # Validate corpus files
    uvi-export      # Export corpus data
    uvi-benchmark   # Performance benchmarking

📖 For detailed usage instructions, see src/uvi/README.md

Happy corpus analysis! 🔍✨
    """
    print(message)

# Print the message if running setup.py directly
if __name__ == '__main__':
    import sys
    if 'install' in sys.argv:
        import atexit
        atexit.register(print_post_install_message)