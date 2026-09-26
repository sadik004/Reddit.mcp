from setuptools import setup, find_packages

setup(
    name="reddit-mcp",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "playwright>=1.40.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "reddit-mcp=reddit_mcp.__main__:main",
        ],
    },
)
