## Images Processing App
| [![Build Status](https://travis-ci.com/arahmanhamdy/img-process.svg?branch=master)](https://travis-ci.com/arahmanhamdy/img-process) 	| [![codecov](https://codecov.io/gh/arahmanhamdy/img-process/branch/master/graph/badge.svg)](https://codecov.io/gh/arahmanhamdy/img-process) 	|  [![CodeFactor](https://www.codefactor.io/repository/github/arahmanhamdy/img-process/badge)](https://www.codefactor.io/repository/github/arahmanhamdy/img-process) 	|
|-------------------------------------------------------------------------------------------------------------------------------------	|--------------------------------------------------------------------------------------------------------------------------------------------	|--------------------------------------------------------------------------------------------------------------------------------------------------------------------	|

Image Processing API written in Python using Flask API to upload images and process them. 

- [Quick Start](#Quick-Start)
    - [Using virtualenv](#using-virtualenv)
    - [Using Docker](#using-docker)
- [Configuration](#configuration)
- [Extending processors](#extending-processors)
- [Running Unit Test](#running-unit-tests)
- [CI/CD](#ci--cd)
- [AWS Live Demo](#aws-live-demo)
- [Architecture Q/A](#architecture-qa)

### Quick Start
- #### Using virtualenv
    ```bash
  git clone https://github.com/arahmanhamdy/img-process.git
  cd img-process
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  python start.py 
    ```

- #### Using Docker
    There is a docker image on dockerhub containing the app
    ```bash
   sudo docker run -d --name myapp -p 8080:8080 arahmanhamdy/img-process
    ```

After starting the app you can test that it is up and running by curling the image history endpoint:

```bash
curl -s http://localhost:8080/images # The response should be empty list []
```

or you can start uploading images:
```bash
curl -s -F image=@<IMAGE_PATH> http://localhost:8080/images
```

### Configuration
The default configuration for the app is to run on `dev` environment, with backend `sqlite` database.
To be able to change the default behaviour you can edit the [configuration file](svc/config.py) to set new sqlalchemy url and other options.

### Extending processors
To be able to extend processors and add new image processing tasks we need the following steps:

1 - Create new python module in [processors directory](svc/processors)
```bash
touch <REPO_DIR>/svc/processors/my_task.py
```
2 - Add NAME attribute and implement `execute` function in this module
```python
# svc/processors/my_task.py
from PIL import Image


NAME = "My New Task"

def execute(img_obj):
    image = Image.open(img_obj)
    return {"width": image.width, "height": image.height}
```

3 - Explicitly add `my_task` module to processors [REGISTERED_TASKS](svc/processors/__init__.py)
```python
from svc.processors import my_task

REGISTERED_TASKS = [
    ....,
    my_task,
]
```

When we upload any image all registered tasks will be executed on the uploaded image and the results will be returned.

### Running Unit Tests
```bash
nosetests --with-coverage --cover-package=svc
```

### CI / CD
The repo is configured using [travis](https://travis-ci.com/arahmanhamdy/img-process) to run ci/cd pipeline.
The pipeline execute the following automatically with new commits:
- Run all unit tests
- Push test coverage results to [codecov.io](https://codecov.io/gh/arahmanhamdy/)
- Build new docker image and push it to [dockerhub](https://hub.docker.com/r/arahmanhamdy/img-process)
- Deploy the app to aws lambda 

### AWS live demo
I have created a live [demo](https://4dbz3odohd.execute-api.us-east-2.amazonaws.com/stg/images) using AWS free-tier with the following deployment architecture
![AWS Deployment](deploy.jpg)

### Architecture Q/A
**Why do we use zappa serverless framework?**
- Zappa offers an easy way to deploy flask apps using aws api gateway

**Why do we use sql database instead of a no-sql one, specially while we need flexible schema for saving results?**
- Most modern sql engines support json data type with better performance (i.e. Postgresql VS MongoDb) but consumes more disk space which is not an issue in our project
- Sqlalchemy provides unified data access layer for different sql engines  
- Using sqlite in `dev` environment enabled quick start development without the hassle of setup separate db engine

**Why do we have separate utilities for image readers and writers?**
- To be able to use different types of storage (local, s3) in a unified way and be extendable in the future to include other types if any (i.e. ftp)

**Why do we need to register tasks explicitly instead of dynamic loading of modules?**
- Explicit is better than implicit [PEP-20](https://www.python.org/dev/peps/pep-0020/)

**What if the processing task takes long time (longer than request max time)?**
- The current architecture enables us with flexibility that if we found specific tasks takes long time, we can change the execute method to just push a job to a queue and add a new endpoint for updating results when finished  

**Why do we have different main.py and start.py outside svc dir?**
- To be able to use them with zappa and with manual deployment

**Why do we have to install numpy for such a small task?**
- Actually that is true, it is not needed but in such projects which aims for adding image processing tasks we will use numpy sooner or later