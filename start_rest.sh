#!/usr/bin/env bash

source ./functions.sh

function show_menu {
    echo -n "Kill? [y/n]: "
    read -n ans
    if [[ ${ans} =~ "y|Y" ]]; then
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

rest_start CP 3002
rest_start AP 3001

while show_menu; do
    show_menu
done