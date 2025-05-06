#!/bin/bash

while getopts a: option
do
case "${option}"
in
a) APP_BUNDLE=${OPTARG};;
esac
done

export OPENAI_API_KEY=***
# echo $OPENAI_API_KEY

export TOKENIZERS_PARALLELISM=true

python -m src.main --app_bundle "$APP_BUNDLE"
