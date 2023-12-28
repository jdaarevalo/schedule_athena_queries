import boto3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ScheduleManagementError(Exception):
    """Base exception class for Schedule Management errors."""
    pass

class ScheduleGroupNotFoundError(ScheduleManagementError):
    def __init__(self, group_name: str):
        message = f"Schedule group not found: {group_name}"
        super().__init__(message)

class ScheduleOperationError(ScheduleManagementError):
    def __init__(self, operation: str, message: str):
        super().__init__(f"Error in {operation}: {message}")

# Helper functions
def log_error_and_raise(exception: Exception, message: str):
    """Log an error and raise a custom exception."""
    logging.error(message)
    raise exception

def safe_get(dictionary: Dict, *keys):
    """Safely get a value from a nested dictionary."""
    for key in keys:
        dictionary = dictionary.get(key)
        if dictionary is None:
            return None
    return dictionary

# Main functions
def validate_or_initialize_schedule_group(client: boto3.client, schedule_group_name: str, stack_tags: List = []) -> Optional[str]:
    """Validate or initialize a schedule group."""
    try:
        response = client.list_schedule_groups(NamePrefix=schedule_group_name)
        schedule_groups = response.get("ScheduleGroups")

        if not schedule_groups:
            return create_schedule_group(client, schedule_group_name, stack_tags)
        return safe_get(schedule_groups[0], "Arn")
    except Exception as e:
        raise ScheduleOperationError("validate_or_initialize_schedule_group", str(e))

def create_schedule_group(client: boto3.client, schedule_group_name: str, stack_tags: List = []) -> Optional[str]:
    """Create a schedule group."""
    try:
        response = client.create_schedule_group(Name=schedule_group_name, Tags=stack_tags)
        return response.get('ScheduleGroupArn')
    except Exception as e:
        raise ScheduleOperationError("create_schedule_group", str(e))

def sync_schedules(client: boto3.client, schedule_group_name: str, schedule_yamls: Dict[str, Dict], output_location: str, stm_arn: str, role_arn: str):
    """Synchronize schedules."""
    try:
        existing_schedule_names = list_schedules_names(client, schedule_group_name)
        schedule_names = [details["name"] for details in schedule_yamls.values()]

        # Perform schedule operations
        create_new_schedules(client, schedule_group_name, schedule_yamls, existing_schedule_names, schedule_names, output_location, stm_arn, role_arn)
        update_existing_schedules(client, schedule_group_name, schedule_yamls, existing_schedule_names, schedule_names, output_location, stm_arn, role_arn)
        delete_old_schedules(client, schedule_group_name, existing_schedule_names, schedule_names)
    except Exception as e:
        raise ScheduleOperationError("sync_schedules", str(e))

def list_schedules_names(client: boto3.client, schedule_group_name: str) -> List[str]:
    """List schedule names."""
    response = client.list_schedules(GroupName=schedule_group_name)
    schedules = response.get("Schedules", [])
    return [schedule.get("Name") for schedule in schedules]

def find_schedule_by_name(schedule_yamls: Dict[str, Dict], schedule_name: str) -> Optional[Dict]:
    """Find a schedule by name."""
    return next((details for details in schedule_yamls.values() if details.get('name') == schedule_name), None)

def get_schedule_params(schedule_group_name: str, schedule_dic: Dict, output_location: str, stm_arn: str, role_arn: str) -> Dict:
    """Get schedule parameters."""
    input_json = json.dumps({"QueryString": schedule_dic["query_string"],
                             "OutputLocation": output_location,
                             "WaitSeconds": schedule_dic.get("wait_seconds", 60)})
    schedule_params = {
        'FlexibleTimeWindow': {'Mode': 'OFF'},
        'ScheduleExpression': schedule_dic["schedule_expression"],
        'Description': schedule_dic.get("schedule_description", "Schedule to trigger Athena Query STF"),
        'GroupName': schedule_group_name,
        'Name': schedule_dic["name"],
        'State': schedule_dic.get("state", "ENABLED"),
        'Target': {
            'Arn': stm_arn,
            "RoleArn": role_arn,
            "Input": input_json
        }
    }
    # Add optional date parameters
    if "start_date" in schedule_dic:
        schedule_params["StartDate"] = datetime.strptime(schedule_dic["start_date"], "%Y-%m-%d %H:%M")
    if "end_date" in schedule_dic:
        schedule_params["EndDate"] = datetime.strptime(schedule_dic["end_date"], "%Y-%m-%d %H:%M")

    return schedule_params

def schedule_operation(client: boto3.client, operation: str, **kwargs):
    """Perform a schedule operation (create, update, delete)."""
    try:
        return getattr(client, operation)(**kwargs)
    except Exception as e:
        raise ScheduleOperationError(operation, str(e))

def create_new_schedules(client, group_name, yamls, existing_names, schedule_names, output_location, stm_arn, role_arn):
    for new_schedule in set(schedule_names) - set(existing_names):
        schedule_dic = find_schedule_by_name(yamls, new_schedule)
        if schedule_dic:
            params = get_schedule_params(group_name, schedule_dic, output_location, stm_arn, role_arn)
            schedule_operation(client, 'create_schedule', **params)

def update_existing_schedules(client, group_name, yamls, existing_names, schedule_names, output_location, stm_arn, role_arn):
    for update_schedule in set(existing_names) & set(schedule_names):
        schedule_dic = find_schedule_by_name(yamls, update_schedule)
        if schedule_dic:
            params = get_schedule_params(group_name, schedule_dic, output_location, stm_arn, role_arn)
            schedule_operation(client, 'update_schedule', **params)

def delete_old_schedules(client, group_name, existing_names, schedule_names):
    for delete_schedule in set(existing_names) - set(schedule_names):
        schedule_operation(client, 'delete_schedule', GroupName=group_name, Name=delete_schedule)
