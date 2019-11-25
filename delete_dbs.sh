#!/usr/bin/env bash

if rm cp/cp.sqlite 2> output.log; then
    printf "\e[32mCP database removed\e[0m\n"
else \
    printf "\e[31mCP database couldn't be removed because it possibly does not exist\e[0m\n"
    OUTPUT=1
fi

if rm ap/ap.sqlite 2>> output.log; then
    printf "\e[32mAP database removed\e[0m\n"
else \
    printf "\e[31mAP database couldn't be removed because it possibly does not exist\e[0m\n"
    OUTPUT=1
fi

if rm user/user.sqlite 2>> output.log; then
    printf "\e[32mUser database removed\e[0m\n"
else \
    printf "\e[31mUser database couldn't be removed because it possibly does not exist\e[0m\n"
    OUTPUT=1
fi

if rm service/service.sqlite 2>> output.log; then
    printf "\e[32mService database removed\e[0m\n"
else \
    printf "\e[31mService database couldn't be removed because it possibly does not exist\e[0m\n"
    OUTPUT=1
fi

if [[ -e OUTPUT ]]; then
    printf "\e[0mPlease check output.log\e[0m\n"
fi



