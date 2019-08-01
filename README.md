# Api-Server

This project was created using Python 3.7.3

##
The API-server checks the JWT token which is created by logging in into www.ttvn.nl/app

### Prerequisites

A settings.ini has to be present in the parent folder from where the api-server runs. 

The file should look like

```
[tokens]
key = ThisIsMySecretKey 
```


### Used commands
How-to-do this example from here: 
* https://packaging.python.org/tutorials/packaging-projects/

First upload package to test pypi
* python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

Install the package on another environment
* python -m pip install --index-url https://test.pypi.org/simple/ --no-deps mailapi-pkg

Upload subsequent versions to pypi
* pip install --upgrade https://test.pypi.org/simple/ mailapi-pkg