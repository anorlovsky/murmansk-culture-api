#!/usr/bin/bash

PROXY_FLAGS="--proxy-headers --forwarded-allow-ips='*'"
LOG_CONFIG="--log-config murmansk_culture_api/log_config.yaml"
ROOT_PATH="--root-path /murmansk-culture/api/"

script_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$script_path"/..
./env/bin/python -m uvicorn murmansk_culture_api.main:app --port 8000 $PROXY_FLAGS $LOG_CONFIG $ROOT_PATH &
