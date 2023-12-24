import re
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(essage)s')

# Custom Exceptions
class InvalidNameError(Exception):
    def __init__(self, name: str, pattern: str, message: str = "Name does not match the required pattern"):
        super().__init__(f"{message}: {name} (Pattern: {pattern})")

class DuplicateNameError(Exception):
    def __init__(self, duplicates: List[str], message: str = "Duplicate titles found"):
        super().__init__(f"{message}: {duplicates}")

class ScheduleExpressionError(Exception):
    def __init__(self, expression: str, message: str = "Invalid schedule expression"):
        super().__init__(f"{message}: {expression}")

# Validation Functions
def validate_name_pattern(name: str, pattern: str = r'^[0-9a-zA-Z-_.]+$') -> None:
    if not re.match(pattern, name):
        raise InvalidNameError(name, pattern)

def validate_names(names: List[str]) -> None:
    seen_names, duplicates = set(), set()
    for name in names:
        validate_name_pattern(name)
        if name in seen_names:
            duplicates.add(name)
        seen_names.add(name)
    if duplicates:
        raise DuplicateNameError(list(duplicates))

def validate_schedule_expression(expression: str) -> None:
    at_pattern = r'^at\(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\)$'
    rate_pattern = r'^rate\(\d+\s+(minutes|hours|days)\)$'
    cron_pattern = r'^cron\((\S+\s+){5,6}\S+\)$'

    if not (re.match(at_pattern, expression) or re.match(rate_pattern, expression) or re.match(cron_pattern, expression)):
        raise ScheduleExpressionError(expression)

def validate_expressions(expressions: List[str]) -> None:
    for expression in expressions:
        validate_schedule_expression(expression)

def validate_schedule_files(schedule_yamls: Dict[str, Dict]) -> None:
    validate_names([schedule["name"] for schedule in schedule_yamls.values()])
    validate_expressions([schedule["schedule_expression"] for schedule in schedule_yamls.values()])
