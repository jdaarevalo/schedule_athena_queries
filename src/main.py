import os
import boto3
import logging
import cfnresponse


from utils.yaml_handler import list_yaml_files, read_multiple_yamls
from utils.schedule_management import sync_schedules, validate_or_initialize_schedule_group
from utils.schedule_validation import validate_schedule_files

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize boto3 session and client
session = boto3.Session()
client = session.client('scheduler', region_name='eu-west-1')

# Environment variables
ROLE_ARN = os.getenv("ROLE_ARN")
STACK_TAGS = os.getenv("STACK_TAGS", [])
STM_ARN = os.getenv("STM_ARN")
OUTPUT_LOCATION = os.getenv("OUTPUT_LOCATION")
SCHEDULE_GROUP_NAME = os.getenv("SCHEDULE_GROUP_NAME")
YAML_QUERIES_PATH = "queries/"

def lambda_handler(event, context):
    logger.info({"action": "invoke_lambda", "payload": {"event": event, "context":context}})
    try:
        # Read and validate YAML files containing the schedules
        paths = list_yaml_files(YAML_QUERIES_PATH)
        schedule_yamls = read_multiple_yamls(paths)
        validate_schedule_files(schedule_yamls)
        logger.info({"action": "validate_schedule_files", "payload": {"len_yaml":len(schedule_yamls)}})

        # Ensure the schedule group exists or create a new one
        validate_or_initialize_schedule_group(client, SCHEDULE_GROUP_NAME, STACK_TAGS)
        logger.info({"action": "validate_or_initialize_schedule_group", "payload": {"group_name":SCHEDULE_GROUP_NAME}})

        # Sync the schedules from the YAML files with the scheduler service
        sync_schedules(client, SCHEDULE_GROUP_NAME, schedule_yamls, OUTPUT_LOCATION, STM_ARN, ROLE_ARN)
        logger.info({"action": "validate_or_initialize_schedule_group", 
                    "payload": {"group_name":SCHEDULE_GROUP_NAME, "schedule_yamls":schedule_yamls}})

        if event.get('ServiceToken'):
            response_data = {"message ": "Schedules synchronized successfully."}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data, "Custom resource executed successfully")
     
    except Exception as execution_error:
        logger.error(str(execution_error))

        if event.get('ServiceToken'):
            error_message = f"An error occurred: {str(execution_error)}"
            cfnresponse.send(event, context, cfnresponse.FAILED, {}, error_message)
