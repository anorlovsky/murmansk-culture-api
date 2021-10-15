#!/usr/bin/bash

script_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

PROXY_FLAGS="--proxy-headers --forwarded-allow-ips='*'"
ROOT_PATH="--root-path /artmuseum/"

cd "$script_path"/artmuseum
../env/bin/python -m uvicorn main:app --port 8000 --log-config logging.yaml $PROXY_FLAGS $ROOT_PATH &

