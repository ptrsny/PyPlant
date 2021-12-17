from setuptools import setup

setup(
    name="pyplant",
    version="0.0.0",
    description="Parse Sourcecode and create UML Diagrams from that",
    author="Petersen, Yannik",
    author_email="yannikpetersen@hotmail.de",
    packages=["pyplant"],
    entry_points={
        "console_scripts": [
            'pyplantcli = pyplant.__main__:main'
        ]
    },
)
