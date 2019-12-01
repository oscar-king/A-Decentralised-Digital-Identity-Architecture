[![Build Status](https://travis-ci.com/oscar-king/A-Decentralised-Digital-Identity-Architecture.svg?token=L8y7QxZfxoXmp3WcvyPR&branch=master)](https://travis-ci.com/oscar-king/A-Decentralised-Digital-Identity-Architecture) [![Maintainability](https://api.codeclimate.com/v1/badges/253cb83f374b8a7dfd99/maintainability)](https://codeclimate.com/github/oscar-king/A-Decentralised-Digital-Identity-Architecture/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/253cb83f374b8a7dfd99/test_coverage)](https://codeclimate.com/github/oscar-king/A-Decentralised-Digital-Identity-Architecture/test_coverage) [![Requirements Status](https://requires.io/github/oscar-king/A-Decentralised-Digital-Identity-Architecture/requirements.svg?branch=master)](https://requires.io/github/oscar-king/A-Decentralised-Digital-Identity-Architecture/requirements/?branch=master) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# A Decentralised Digital Identity Architecture

This is a toy implementation of the architecture proposed by Geoff Goodell and Tomaso Aste in [this](https://arxiv.org/abs/1902.08769) paper. Currently still being developed!!

## Structure
A brief overview of the file structure of this project.

```bash
    .
    ├── ap
        ├── tests
            ├── tests_app_pytest.py  
        ├── .dockerfile
        ├── app.py
        ├── Dockerfile            
    ├── cp
        ├── tests
            ├── tests_app_pytest.py  
        ├── .dockerfile
        ├── app.py
        ├── Dockerfile
    ├── user
        ├── tests
            ├── tests_app_pytest.py  
        ├── .dockerfile
        ├── app.py
        ├── Dockerfile
    ├── service
        ├── tests
            ├── tests_app_pytest.py  
        ├── .dockerfile
        ├── app.py
        ├── Dockerfile
    ├── .env                
    ├── .gitignore    
    ├── requirements.txt
    ├── Dockerfile
    ├── docker-compose.yml
    └── README.md
```

## Download

Use [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) to clone the project.

```bash
git clone https://github.com/oscar-king/A-Decentralised-Digital-Identity-Architecture.git
```
Currently the most up to date branch is the `crypto` branch, please clone this one.

## Setup
The project makes use of Docker, Docker Compose, and Hyperledger Composer, so if you do not already have them you can install them here:
1. [Install Docker](https://docs.docker.com/v17.09/engine/installation/)
2. [Install Docker Compose](https://docs.docker.com/v17.09/compose/install/#install-compose)
3. [Install Hyperledger Composer CLI](https://hyperledger.github.io/composer/v0.19/installing/development-tools.html)

## Building Dependencies
The project makes use of a base image with all dependencies installed on it. This is done to save time in subsequent builds. This base image can be built manually, or the prebuilt image supplied can be loaded such that docker can use it.

Building the image manually:
1. Ensure you are in the project's root directory.
2. Run the following `docker build -t code_latest:latest .`
This builds the image from the dockerfile located in the project root. 

To load the prebuilt image:
1. Ensure you are in the project's root directory.
2. Run the following `docker load --input code_base.tar.gz`

### Sockets
The default configuration for the project is to have docker compose deploy all the containers locally on `localhost`. Additionally the endpoints for the specific entities are as follows:

|           Entity        | Directory Name  |      Port     |
| ------------------------|:---------------:|:-------------:|
|           User          |        ap       |     5000      |
| Authentication Provider |        ap       |     5001      |
| Cerfication Provider    |        cp       |     5002      |
|          Service        |        ap       |     5003      |
|          Ledger         |      ledger     |     8080      |

Then to run the project issue the following commands:
```bash
docker-compose build
docker-compose up
```

After issuing these commands all components should be up and running. To initialise the system with participants please run the following script located in the root directory `init.sh`.
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
