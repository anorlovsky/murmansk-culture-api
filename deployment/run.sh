#!/usr/bin/bash

script_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

PROXY_FLAGS="--proxy-headers --forwarded-allow-ips='*'"
ROOT_PATH="--root-path /murmansk-culture/api/"

cd "$script_path"/murmansk_culture
../env/bin/python -m uvicorn main:app --port 8000 --log-config log_config.yaml $PROXY_FLAGS $ROOT_PATH &
