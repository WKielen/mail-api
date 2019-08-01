import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mailapi",
    version="0.0.2",
    author="Wim Kielen",
    author_email="wim_kielen@hotmail.com",
    description="A small rest-api server with one api which can send a mail.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wkielen/mail-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'mailapi=mailapi.mailapi:main',
        ],
    }
)
