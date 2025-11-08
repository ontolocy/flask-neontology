from setuptools import find_packages, setup

setup(
    name="Flask-Neontology",
    version="0.0.2",
    packages=find_packages(include=["flask_neontology", "flask_neontology.*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "flask",
        "neontology",
        "pydantic",
        "Frozen-Flask",
        "markdown",
        "markdown-link-attr-modifier",
        "email-validator",
        "PyYAML",
    ],
)
