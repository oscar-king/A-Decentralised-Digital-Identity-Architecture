docker-compose -f "docker-compose.yml" down

cd ledger 
export FABRIC_VERSION=hlfv12

./fabric-dev-servers/stopFabric.sh
./fabric-dev-servers/teardownFabric.sh

cd ..

composer card delete -c PeerAdmin@hlfv1
composer card delete -c admin@digid
composer card delete -c CP@digid
composer card delete -c AP@digid

echo "All containers stopped"
