import os
import glob
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YamlReadError(Exception):
    """Exception raised when a YAML file cannot be read."""
    def __init__(self, file_path: str, error: Exception):
        super().__init__(f"Failed to read {file_path}: {error}")


def list_yaml_files(directory: str, exclude: str = "template_query.yaml") -> list:
    """
    List all YAML files in the specified directory excluding the specified file.
    A list of paths to the YAML files in the specified directory excluding the specified file.
    """
    directory = os.path.join(directory, '')  # Ensure the path ends with a separator
    pattern = os.path.join(directory, '*.y*ml')  # Create a pattern to match all .yaml and .yml files
    yaml_files = [f for f in glob.glob(pattern) if os.path.basename(f) != exclude]  # Exclude the specified file
    return yaml_files

def read_yaml(path: str) -> dict:
    """Read a single YAML file and return its contents as a dictionary."""
    try:
        with open(path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise YamlReadError(path, e)

def read_multiple_yamls(paths: list) -> dict:
    """Read multiple YAML files and return their contents in a dictionary."""
    all_yaml_files = {}
    for path in paths:
        try:
            all_yaml_files[path] = read_yaml(path)
        except YamlReadError as e:
            logging.error(e)
    return all_yaml_files
