#!/usr/bin/env bash

NETWORK_VERSION=0.2.1

function add_participant() {
    composer participant add -c $1 -d '{"$class":"digid.'$2'","participantID":"'$3'"}'
}

function issue_identity() {
    composer identity issue -c $1 -f $4.card -u $4 -a "digid."$2"#"$3
    composer card import -f $4.card
}

function new_provider() {
    add_participant $1 $2 $3
    issue_identity $1 $2 $3 $4
}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR/ledger"
export FABRIC_VERSION=hlfv12
export FABRIC_START_TIMEOUT=30

# Start Hyperledger
./fabric-dev-servers/downloadFabric.sh
./fabric-dev-servers/startFabric.sh
./fabric-dev-servers/createPeerAdminCard.sh

# Install network
composer network install --card PeerAdmin@hlfv1 --archiveFile digid@$NETWORK_VERSION.bna
composer network start --networkName digid --networkVersion $NETWORK_VERSION --networkAdmin admin --networkAdminEnrollSecret adminpw --card PeerAdmin@hlfv1 --file networkadmin.card
composer card import --file networkadmin.card

new_provider "admin@digid" "CertificationProvider" 2000 "CP"
new_provider "admin@digid" "AuthenticationProvider" 3000 "AP"

# Change localhost to container names
sed -e 's/localhost:7051/peer0.org1.example.com:7051/' -e 's/localhost:7053/peer0.org1.example.com:7053/' -e 's/localhost:7054/ca.org1.example.com:7054/'  -e 's/localhost:7050/orderer.example.com:7050/'  < $HOME/.composer/cards/PeerAdmin@hlfv1/connection.json  > /tmp/connection.json && cp -p /tmp/connection.json $HOME/.composer/cards/PeerAdmin@hlfv1/
sed -e 's/localhost:7051/peer0.org1.example.com:7051/' -e 's/localhost:7053/peer0.org1.example.com:7053/' -e 's/localhost:7054/ca.org1.example.com:7054/'  -e 's/localhost:7050/orderer.example.com:7050/'  < $HOME/.composer/cards/admin@digid/connection.json  > /tmp/connection.json && cp -p /tmp/connection.json $HOME/.composer/cards/admin@digid/
sed -e 's/localhost:7051/peer0.org1.example.com:7051/' -e 's/localhost:7053/peer0.org1.example.com:7053/' -e 's/localhost:7054/ca.org1.example.com:7054/'  -e 's/localhost:7050/orderer.example.com:7050/'  < $HOME/.composer/cards/CP@digid/connection.json  > /tmp/connection.json && cp -p /tmp/connection.json $HOME/.composer/cards/CP@digid/
sed -e 's/localhost:7051/peer0.org1.example.com:7051/' -e 's/localhost:7053/peer0.org1.example.com:7053/' -e 's/localhost:7054/ca.org1.example.com:7054/'  -e 's/localhost:7050/orderer.example.com:7050/'  < $HOME/.composer/cards/AP@digid/connection.json  > /tmp/connection.json && cp -p /tmp/connection.json $HOME/.composer/cards/AP@digid/

cd "$DIR"

# Start flask containers
docker-compose -f "docker-compose.yml" up -d

echo "All containers started"
