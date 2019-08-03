# Api-Server

This project is created using Python 3.7.4

##
The API-server checks the JWT token which is created by logging in into www.ttvn.nl/app

### Prerequisites

A 'config.yml' has to be present in the folder from where the api-server runs.

The file should look like

```
tokens:
    jwt_secret : ThisIsYourJWTSecret
```

### Used commands
How-to-do this example from here: 
* https://packaging.python.org/tutorials/packaging-projects/

Create a distribution
* python setup.py sdist bdist_wheel

First upload package to test pypi
* python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

Install the package on another environment
* python -m pip install --index-url https://test.pypi.org/simple/ --no-deps mailapi

Upload subsequent versions to pypi
* pip install --upgrade https://test.pypi.org/simple/ mailapi

Install distribution directly in path
* pip install --upgrade .

To fill the requirements file
* pip freeze > requirements.txt

I got the error "No module named C:\Users\wim_k\AppData\Local\Programs\Python\Python37-32\Scripts\mailapi"
when I run mailapi. The command below solved it.
* pip setup.py install

