# A Decentralised Digital Identity Architecture

This is a toy implementation of the architecture proposed by Geoff Goodell and Tomaso Aste in [this](https://arxiv.org/abs/1902.08769) paper.

## Structure
A brief overview of the file structure of this project.

```bash
    .
    ├── ap
        ├── tests
            ├── tests_app_pytest.py  
        ├── app.py
        ├── Dockerfile            
    ├── cp
        ├── tests
            ├── tests_app_pytest.py  
        ├── app.py
        ├── Dockerfile
    ├── user
        ├── tests
            ├── tests_app_pytest.py  
        ├── app.py
        ├── Dockerfile
    ├── service
        ├── tests
            ├── tests_app_pytest.py  
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

## Setup
The project makes use of Docker, Docker Compose, and Hyperledger Composer, so if you do not already have them you can install them here:
1. [Install Docker](https://docs.docker.com/v17.09/engine/installation/)
2. [Install Docker Compose](https://docs.docker.com/v17.09/compose/install/#install-compose)
3. [Install Hyperledger Composer CLI](https://hyperledger.github.io/composer/v0.19/installing/development-tools.html) (remove @19 from npm commands)

## Building Dependencies
The project makes use of a base image with all dependencies installed on it. This is done to save time in subsequent builds. This base image can be built manually:
1. Ensure you are in the project's root directory.
2. Run the following `docker build -t test_latest:latest .`
This builds the image from the dockerfile located in the project root. 

## Running
2 shell scripts are included to start and stop the project (bring up Hyperledger Fabric and Flask containers). To start the project, run `./start.sh`. To stop the project, run `./stop.sh`. After `start.sh` completes successfully, you can bring up and down the Flask containers only with `docker-compose down` and `docker-compose up --build -d`.

## Usage
Once the docker containers are running, navigate to the pages for the AP and CP, for both create a policy. This can be done by filling out the forms on the pages `Generate AP Policy` and `Generate Policy` for the AP and CP respectively. Then you must sign up on the User page, and subsequently log in. After logging in, go to `Generate and Post Keys`. Here you can generate the desired number of credentials with the CP. After these keys have been generated, return the the CP page. The CP must publish the generated key by filling out the form on the `Publish Policies` page. Once this is done the User can either verify or use a key by navigating to the `Verify` and `Access Service` page respectively, where the corresponding forms must be filled out. 

## Sockets
The default configuration for the project is to have docker compose deploy all the containers locally on `localhost/0.0.0.0`. Additionally the endpoints for the specific entities are as follows:

|           Entity        | Directory Name  |      Port     |
| ------------------------|:---------------:|:-------------:|
|           User          |      user       |     5000      |
| Authentication Provider |      ap         |     5001      |
| Cerfication Provider    |      cp         |     5002      |
|          Service        |      service    |     5003      |
|          Ledger         |      ledger     |     8080      |

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
