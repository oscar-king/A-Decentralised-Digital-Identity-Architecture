#!/usr/bin/env bash

source ./functions.sh

DIR=$PWD
if [[ "/code" != ${DIR:(-5)} ]]; then
    printf "\e[31mYou need to run this script in the code directory.\e[0m\n"
    exit
fi

function show_menu {
    echo -n "Kill? [y/n]: "
    read -n ans
    if [[ ${ans} =~ "y|Y" ]]; then
        pgrep -f "cp/app.py" | xargs kill
        pgrep -f "ap/app.py" | xargs kill
        pgrep -f "user/app.py" | xargs kill
        pgrep -f "service/app.py" | xargs kill
        pgrep -f "composer-rest-server -c CP@digid" | xargs kill
        pgrep -f "composer-rest-server -c AP@digid" | xargs kill
        printf "\e[31mKilled.\e[0m\n"
        exit
    elif [[ ${ans} =~ "n|N" ]]; then
        echo -n "Detach? [y/n]: "
        read -n ans
        if [[ $ans =~ "y|Y" ]]; then
            exit
        elif [[ $ans =~ "n|N" ]]; then
            return true
        else \
            echo "Unexpected character"
            return true
        fi
    else \
        echo "Unexpected character"
        return true
    fi
}

start cp
start ap cp
start user cp ap
start service cp ap user
rest_start CP 3002
rest_start AP 3001

while show_menu; do
    show_menu
done