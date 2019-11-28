#!/usr/bin/env bash

NETWORK_VERSION=0.2.1

if [[ -e "output.log" ]]; then
  rm output.log
fi


function add_participant() {
    composer participant add -c $1 -d '{"$class":"digid.'$2'","participantID":"'$3'"}'
}

function issue_identity() {
    composer identity issue -c $1 -f $4.card -u $4 -a "digid."$2"#"$3
    composer card import -f $4.card
}

function new_provider() {
    add_participant $1 $2 $3 >> output.log
    issue_identity $1 $2 $3 $4 >> output.log
}

# Remove all state
#./fabric-dev-servers/teardownFabric.sh >> output.log
composer card delete -c PeerAdmin@hlfv1 >> output.log
composer card delete -c admin@digid >> output.log
composer card delete -c CP@digid >> output.log
composer card delete -c AP@digid >> output.log

# Start again
bash ./fabric-dev-servers/createPeerAdminCard.sh >> output.log
#./fabric-dev-servers/startFabric.sh >> output.log
composer network install --card PeerAdmin@hlfv1 --archiveFile digid@$NETWORK_VERSION.bna >> output.log
composer network start --networkName digid --networkVersion $NETWORK_VERSION --networkAdmin admin --networkAdminEnrollSecret adminpw --card PeerAdmin@hlfv1 --file networkadmin.card >> output.log
composer card import --file networkadmin.card >> output.log

new_provider "admin@digid" "CertificationProvider" 2000 "CP"
new_provider "admin@digid" "AuthenticationProvider" 3000 "AP"

bash ./test_ledger_connection.sh

# Create REST Interface
printf "\e[31m Please run: \n \e[0m composer-rest-server -c CP@digid -n never -u true -d n -w true -p 3002 \n"
printf "\e[31m Please run: \n \e[0m composer-rest-server -c AP@digid -n never -u true -d n -w true -p 3001 \n"