#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

# Stop flask containers
docker-compose -f "docker-compose.yml" down

cd $DIR/ledger
export FABRIC_VERSION=hlfv12

# Stop Hyperledger
./fabric-dev-servers/stopFabric.sh
./fabric-dev-servers/teardownFabric.sh

# Delete old state
composer card delete -c PeerAdmin@hlfv1
composer card delete -c admin@digid
composer card delete -c CP@digid
composer card delete -c AP@digid

echo "All containers stopped"
