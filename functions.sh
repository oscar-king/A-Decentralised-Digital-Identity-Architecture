#!/usr/bin/env bash

function wait_for_ping {
    I=0
    printf "\tWaiting for ping "
    while $(! nc -vz $1 $2 &> /dev/null); do
        printf "."; sleep 0.3
    done
    printf "\e[32m Success\e[0m\n"
}

function rest_start {
    if [[ -d $1 ]] && [[ -n $(composer card list | grep $1"@digid") ]] 2> $1.log; then
        composer-rest-server -c $1@digid -n never -u true -d n -w true -p $2 &>> $1.log &
        printf "\e[32mStarting $1 rest server\e[0m\n"
    else \
        printf "\e[31m$1@digid does not seem to exist. Check $1.log for more information.\e[0m\n"
        for i in "${@:2}"; do
            pgrep -f "composer-rest-server -c $i@digid" | xargs kill
        done
        exit
    fi
}

function handle_response {
    if [[ $1 -ne $2 ]]; then \
        printf "\e[31m$4\e[0m\n"
        printf "\e[31mExiting...\e[0m\n"
        pgrep -f "composer-rest-server -c" | xargs kill
        pgrep -f "/app.py" | xargs kill
        exit
    else \
        printf "\e[32m$3\e[0m\n"
    fi
}

function signup_user {
    RESPONSE=$(curl --write-out %{http_code} --silent --output /dev/null -X POST \
        $1/signup \
        -H 'Cache-Control: no-cache' \
        -H 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
        -F  email=$2 \
        -F  name=$3 \
        -F  password=$4
    )
    handle_response $RESPONSE 302 "Signed up user" "Could not sign up user!!"
}

function login_user {
    RESPONSE=$(curl --write-out %{http_code} --silent --output /dev/null -X POST \
        $1/login \
        -H 'Cache-Control: no-cache' \
        -H 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
        -F  email=$2 \
        -F  password=$3 \
        -F  remember=False)
#         | jq -r ".access"

#    if [[ -z $ACCESS_TOKEN ]]; then
#        printf "\e[31mCould not log user in.\e[0m\n"
#        printf "\e[31mExiting...\e[0m\n"
#        exit
#    fi

    handle_response $RESPONSE 302 "Logged user in." "Could not log user in!!"
}

function signup_login {
    signup_user $1 $2 $3 $4
    login_user $1 $2 $4
}

function today() {
    CUR=$(date -u +%s)
    SECONDS_PER_DAY=$(( 86400 ))
    DATE=$(( $CUR - ($CUR % $SECONDS_PER_DAY) ))
    echo $(date -u -r $DATE)
}

function generate_keys {
    RESPONSE=$(curl --write-out %{http_code} --silent --output /dev/null -X POST \
        $1/generate_keys \
        -H 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
        -F number=$2 \
        -F time=$3 \
        -F policy=$4)
    return $RESPONSE
}

function start {
    if [[ -d $1 ]] && [[ -e "$1/app.py" ]] 2> $1.log; then
        python $1/app.py &>> $1.log &
        printf "\e[32mStarting $1\e[0m\n"
    else \
        printf "\e[31m$1 does not seem to exist. Check $1.log for more information.\e[0m\n"
        for i in "${@:2}"; do
            pgrep -f "$i/app.py" | xargs kill
        done
        exit
    fi
}

function kill_application {
    pgrep -f "$1/app.py" | xargs kill
}

function start_some {
    for i in $@ ; do
        start $i
    done
}

function kill_some {
    for i in $@ ; do
        kill_application $i
    done
}

function rest_stop {
    pgrep -f "composer-rest-server -c" | xargs kill
}