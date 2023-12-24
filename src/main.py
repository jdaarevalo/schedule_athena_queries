# TODO
# execute query
# check the s3_output, is a file created on failure?
# trigger next lambda to check status


import os
import sys
import re
import json
import yaml
import boto3

from datetime import datetime, timedelta
# import awswrangler as wr

from aws_lambda_powertools import Logger
from utils import interpret_relative_time

# ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME")
# SOURCE_BUCKET_NAME = os.getenv("SOURCE_BUCKET_NAME")
# TARGET_BUCKET_NAME = os.getenv("TARGET_BUCKET_NAME")

## Rollbar alerts
# import rollbar
# ROLLBAR_SECRET_KEY = os.getenv("ROLLBAR_SECRET_KEY")
# rollbar.init(ROLLBAR_SECRET_KEY, ENVIRONMENT_NAME)

logger = Logger()
b3s = boto3.Session()

# @rollbar.lambda_function
def lambda_handler(event, _):
    # Invoke lambda by event
    logger.info({"action": "invoke_lambda", "payload": {"event": event}})
    try:
        yaml_path = "queries/query_one.yaml"
        yaml_file = read_yaml(yaml_path)
        query = format_query(yaml_file)
        execute_athena_query(query)

        return {
            'statusCode': 200,
            'body': json.dumps({  })
        }
    except Exception as exception:
        logger.error(
            {
                "action": "lambda_execution_error",
                "payload": {"exception": exception, "event": event},
            }
        )

def execute_athena_query(query:str):
    logger.info({"action": "start_query_execution", "payload": {"query": query[:30]}})
    pass

def format_query(yaml_file: dict) -> str:
    # Process parameters
    parameters = yaml_file['parameters']
    for key, value in parameters.items():
        if "date" in key:
            parameters[key] = interpret_relative_time.interprete(value.lower()).strftime('%Y-%m-%d %H:%M:%S')

    # Format the query with the parameters
    query = yaml_file["query"].format(**parameters)
    logger.info({"action": "query", "payload": {"quey": query}})
    return query

def read_yaml(path: str) -> dict:
    with open(path, "r") as file:
        yaml_file = yaml.safe_load(file)
    logger.info({"action": "read_yaml_file", "payload": {"yaml_file": yaml_file}})
    return yaml_file
