[![Build Status](https://travis-ci.com/oscar-king/A-Decentralised-Digital-Identity-Architecture.svg?token=L8y7QxZfxoXmp3WcvyPR&branch=master)](https://travis-ci.com/oscar-king/A-Decentralised-Digital-Identity-Architecture)

[![Maintainability](https://api.codeclimate.com/v1/badges/253cb83f374b8a7dfd99/maintainability)](https://codeclimate.com/github/oscar-king/A-Decentralised-Digital-Identity-Architecture/maintainability)

# A Decentralised Digital Identity Architecture

This is a toy implementation of the architecture proposed by Geoff Goodell and Tomaso Aste in [this](https://arxiv.org/abs/1902.08769) paper.

## Structure
A brief overview of the file structure of this project.

```bash
    .
    ├── ap
        ├── tests
            ├── tests_app_pytest.py  
        ├── .dockerfile
        ├── app.ini
        ├── app.py
        ├── Dockerfile            
    ├── cp
        ├── tests
            ├── tests_app_pytest.py  
        ├── .dockerfile
        ├── app.ini
        ├── app.py
        ├── Dockerfile            
    ├── nginx
        ├── Dockerfile
        ├── nginx.conf         
    ├── .env                
    ├── .gitignore    
    ├── requirements.txt      
    ├── docker-compose.yml
    ├── settings.py
    └── README.md
```

## Download

Use [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) to clone the project.

```bash
git clone https://github.com/oscar-king/A-Decentralised-Digital-Identity-Architecture.git
```

## Setup
The project makes use of Docker and Docker Compose so if you do not already have them you can install them here:
1. [Install Docker](https://docs.docker.com/v17.09/engine/installation/)
2. [Install Docker Compose](https://docs.docker.com/v17.09/compose/install/#install-compose)

Additionally this project makes use of self-signed certificates so something like [OpenSSL](https://www.openssl.org/) is useful. The examples assume the use of OpenSSL.

Before deploying it is important to generate certificates for each entity (i.e Certification Provider, Authentication Provider, etc). It is important to store the certificate and key in the directory of the entity you are creating the certificate for because the `settings.py` file assumes this.

Assuming you are in the project's root directory:
```bash
user@host:~$cd ap
user@host:~$openssl req -newkey rsa:2048 -nodes -keyout ap_cert.key -x509 -days 365 -out ap_cert.crt
``` 
The above should be done for all entities. It is also vital that the following naming conventions are respected: `<current_directory>_cert.key` and `<current_directory>_cert.crt` e.g. If you are in the `ap` directory then the certificate and key will have the following names: `ap_cert.crt` and `ap_cert.key`. There are no restrictions as to the type of certificate, the algorithm or how it what tool you use to create it, the example happens to use OpenSSL. 

### Sockets
The default configuration for the project is to have docker compose deploy all the containers locally on `localhost`. Additionally the endpoints for the specific entities are as follows:

|           Entity        | Directory Name  |      Port     |
| :-----------------------|:---------------:|: ------------:|
| Cerfication Provider    |        cp       |     5001      |
| Authentication Provider |        ap       |     5000      |

The ports can be changed by merely altering them in the `.env` file. However after changing the ports the `settings.py` script must be run to ensure all the configuration files are updated.
```bash
python3 settings.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
