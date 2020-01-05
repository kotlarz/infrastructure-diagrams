import setuptools

try:
    from pypandoc import convert

    read_md = lambda f: convert(f, "rst")
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, "r").read()

setuptools.setup(
    name="infrastructure-diagrams",
    version="0.0.6",
    author="Marius Kotlarz",
    author_email="marius@kotlarz.no",
    description="Create infrastructure diagrams from configuration files (YAML and JSON) by using Graphviz",
    long_description=read_md("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/kotlarz/infrastructure-diagrams",
    packages=setuptools.find_packages(),
    scripts=["bin/infrastructure-diagrams"],
    install_requires=[
        "graphviz>=0.13.2",
        "PyYAML>=5.2",
        "python-magic>=0.4.15",
        "colour>=0.1.5",
        "SecretColors>=1.1.0",
    ],
    classifiers=[
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Documentation",
        "Topic :: Internet",
        "Topic :: Software Development :: Documentation",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
)
