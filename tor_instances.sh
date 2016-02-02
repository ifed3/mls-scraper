#!/usr/bin/env bash

BASE_SOCKS_PORT=9050
BASE_CONTROL_PORT=8188

#Create folder if it doesn't exist
if [ ! -d "data" ]; then
    mkdir "data"
fi

#Create iterator representing number of Tor instances
for i in {0..80}

do
    j=$((i+1))
    socks_port=$((BASE_SOCKS_PORT+i))
    control_port=$((BASE_CONTROL_PORT+i))
    if [ ! -d "data/tor$i" ]; then
        echo "Creating directory data/tor$i"
        mkdir "data/tor$i"
    fi

    echo "Running: tor --RunAsDaemon 1 --CookieAuthentication 0 --HashedControlPassword \"\" --ControlPort $control_port --PidFile tor$i.pid --SocksPort $socks_port --DataDirectory data/tor$i"

    tor --RunAsDaemon 1 --CookieAuthentication 0 --HashedControlPassword "" --ControlPort $control_port --PidFile tor$i.pid --SocksPort $socks_port --DataDirectory data/tor$i
done
