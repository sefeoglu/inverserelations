import os
import sys
import json


def _warn_if_overwriting(file_path):
    if os.path.exists(file_path):
        print(
            f"Warning: The file {file_path} already exists and will be overwritten.",
            file=sys.stderr,
        )


def _ensure_parent_dir(file_path):
    dirpath = os.path.dirname(file_path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)


def _to_serializable(obj):
    if hasattr(obj, "tolist"):
        return obj.tolist()
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def read_json_file(file_path):
    """
    Reads a JSON file and returns its content.
    
    Args:
        file_path (str): The path to the JSON file.
        
    Returns:
        dict: The content of the JSON file.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def read_json(file_path):
    """Compatibility alias for read_json_file."""
    return read_json_file(file_path)


def write_json_file(data, file_path):
    """
    Writes data to a JSON file.
    
    Args:
        data (dict): The data to be written to the file.
        file_path (str): The path to the JSON file.
    """
    _ensure_parent_dir(file_path)
    _warn_if_overwriting(file_path)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False, default=_to_serializable)


def write_json(data, file_path):
    """Compatibility alias for write_json_file."""
    write_json_file(data, file_path)


def write_json_str(data, file_path):
    """
    Writes data to a JSON file, converting non-serializable types (like sets).

    Args:
        data (dict): The data to be written to the file.
        file_path (str): The path to the JSON file.
    """
    _ensure_parent_dir(file_path)
    _warn_if_overwriting(file_path)

    json_str = json.dumps(data, indent=4, ensure_ascii=False, default=_to_serializable)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(json_str)


def write_turtle_to_ttl(file_path, content):
    """
    Writes Turtle content to a TTL file.
    
    Args:
        file_path (str): The path to the TTL file.
        content (str): The Turtle content to be written.
    """
    if not isinstance(content, str):
        content = "\n".join(content)
    content = content.replace(' .', '.')
    content = content.replace(' ;', ';')

    _ensure_parent_dir(file_path)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
