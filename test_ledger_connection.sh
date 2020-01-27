#!/usr/bin/env bash

if composer network ping --card admin@digid &> output.log; then
    printf "\e[32m Successfully pinged admin@digid\e[0m\n"
else \
    printf "\e[31m Pinging admin@digid failed\n\e[0m"
    OUTPUT=1
fi

if composer network ping --card CP@digid &>> output.log; then
    printf "\e[32m Successfully pinged CP@digid\e[0m\n"
else \
    printf "\e[31m Pinging CP@digid failed\n\e[0m"
    OUTPUT=1
fi

if composer network ping --card AP@digid &>> output.log; then
    printf "\e[32m Successfully pinged AP@digid\e[0m\n"
else \
    printf "\e[31m Pinging AP@digid failed\n\e[0m"
    OUTPUT=1
fi

if [[ -e OUTPUT ]]; then
    printf "\e[0m Please check output.log for more information\e[0m\n"
fi