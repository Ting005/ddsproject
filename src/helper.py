import yaml
import pdb
import json
import json5
import re

class Config:
    """Converts a dictionary into a Python object with attribute-style access."""
    
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, Config(value) if isinstance(value, dict) else value)  # Recursively convert nested dictionaries

    def __repr__(self):
        return f"{self.__dict__}"  # Pretty print for debugging


def load_yaml_config(file_path: str) -> Config:
    """Loads a YAML file and returns it as a Config object."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)  # Load as dictionary
            return Config(config_dict)  # Convert to object
    except FileNotFoundError:
        print(f"Error: Config file '{file_path}' not found.")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
    
    return Config({})


def read_prompt(path: str) -> str:
    """Reads a file and returns its content."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()  # Read entire file
            # print(content)
            return content
    except FileNotFoundError:
        print(f"Error: File '{path}' not found.")
        return ""


def correct_json_errors(json_str: str):
    """
    Attempts to fix common JSON errors such as:
    - Missing quotes around keys
    - Trailing commas
    - Single quotes instead of double quotes
    """
    try:
        return json5.loads(json_str)  # Try parsing with json5 (handles more flexible JSON)
    except Exception:
        pass  # If json5 fails, attempt manual correction

    # Fix single quotes around keys and strings
    json_str = re.sub(r"(\s|[{,])'([^']+?)'(\s*[:])", r'\1"\2"\3', json_str)  # Keys
    json_str = re.sub(r"(:\s*)'([^']+?)'", r'\1"\2"', json_str)  # String values
    
    # Remove trailing commas before closing brackets or braces
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)

    try:
        return json.loads(json_str)  # Try standard JSON parsing
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return None  # Return None if parsing fails

