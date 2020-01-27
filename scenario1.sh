#!/usr/bin/env bash

# In this scenario 4 users create generate proofs with the CP for 1 day. These proofs are pushed onto the ledger
# The CP only has 1 policy
# The AP only has 1 policy

source ./functions.sh
source ./delete_dbs.sh

start_some cp ap
rest_start CP 3002
rest_start AP 3001

INTERVAL=1440
HOST=127.0.0.1
BASE_URL=http://$HOST
CP_PORT=5002
AP_PORT=5001
USER_PORT=5000
TIME=`today`
POLICY=1
NUM_GEN_KEYS=5

wait_for_ping $HOST $CP_PORT; wait_for_ping $HOST $AP_PORT

# Generate policy on CP side
RESPONSE=$(curl --write-out %{http_code} --silent --output /dev/null -X POST \
  $BASE_URL:$CP_PORT/gen_policies \
  -H 'content-type: multipart/form-data' \
  -F interval=$INTERVAL \
  -F lifetime=$INTERVAL \
  -F description=1)

handle_response $RESPONSE 302 "Created CP policy" "Could not create policy for CP!!"

# Generate policy on AP side
RESPONSE=$(curl --write-out %{http_code} --silent --output /dev/null -X POST \
  $BASE_URL:$AP_PORT/gen_policies \
  -H 'content-type: multipart/form-data' \
  -F max_age=$INTERVAL \
  -F description=1)

handle_response $RESPONSE 302 "Created AP policy" "Could not create policy for AP!!"

# Generate keys for random users
for i in {1..3} ; do
    start user; wait_for_ping $HOST $USER_PORT
    signup_login $BASE_URL:$USER_PORT "$i@test.com" "Test" "test"
    generate_keys $BASE_URL:$USER_PORT $NUM_GEN_KEYS $TIME $POLICY
    handle_response $RESPONSE 200 "Generated user keys" "Could not generate keys!!"
    kill_some user
    rm user/user.sqlite
done

start user; wait_for_ping $HOST $USER_PORT
signup_login $BASE_URL:$USER_PORT "oscarking@live.com" "Oscar King" "test"
generate_keys $BASE_URL:$USER_PORT $NUM_GEN_KEYS $TIME $POLICY

handle_response $RESPONSE 200 "Generated user keys" "Could not generate keys!!"

# Publish Policy Pool
RESPONSE=$(curl --write-out %{http_code} --silent --output /dev/null -X POST \
  $BASE_URL:$CP_PORT/publish_policies \
  -H 'content-type: multipart/form-data' \
  -F policy=$POLICY \
  -F timestamp=$TIME)

handle_response $RESPONSE 302 "Published policy pool." "Could not publish policy pool!"

kill_some cp ap user
rest_stop

printf "\e[32mSuccess\e[0m\n"