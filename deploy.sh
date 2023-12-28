#!/bin/bash

if ! [[ $1 ]]; then
  echo "use: $0 <ENVIRONMENT {production, staging}>"
  exit 1
fi

# Variables
export AWS_REGION=eu-west-1
export DEPLOYMENT_ID=$(date +%s)
export PROFILE_NAME=$1
export QUERY_OUTPUT_LOCATION=$2

rm -rf .aws-sam/
rm -rf libs/
mkdir -p libs/python/lib/python3.10/site-packages/
pip install -r requirements.txt --target libs/python/lib/python3.10/site-packages


STACK_NAME="test-lambda"


template_file=$(pwd)/template.yaml
if [[ -f $template_file ]]; then
  sam build -t $template_file

  sam deploy \
    --no-fail-on-empty-changeset \
    --profile=${PROFILE_NAME} \
    --stack-name "${STACK_NAME}-${PROFILE_NAME}" \
    --region "${AWS_REGION}" \
    --parameter-overrides QueryOutputLocation=${QUERY_OUTPUT_LOCATION} \
                          DeploymentId=${DEPLOYMENT_ID} \
    --capabilities CAPABILITY_NAMED_IAM \
    --s3-prefix ${STACK_NAME} \
    --resolve-s3 \
    --resolve-image-repos \
    --force-upload --debug
else
  echo "No SAM template found for deployment".
fi
