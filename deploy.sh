#!/bin/bash

if ! [[ $1 ]]; then
  echo "use: $0 <ENVIRONMENT {production, staging}>"
  exit 1
fi

# Variables
export AWS_REGION=eu-west-1
export ENVIRONMENT=$1

rm -rf .aws-sam/

STACK_NAME="schedule-athena-queries"

template_file=$(pwd)/template.yaml
if [[ -f $template_file ]]; then
  sam build -t $template_file

  sam deploy \
    --no-fail-on-empty-changeset \
    --profile=channels-${ENVIRONMENT} \
    --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
    --region "${AWS_REGION}" \
    --capabilities CAPABILITY_NAMED_IAM \
    --s3-prefix ${STACK_NAME} \
    --resolve-s3 \
    --resolve-image-repos \
    --force-upload --debug
else
  echo "No SAM template found for deployment".
fi
