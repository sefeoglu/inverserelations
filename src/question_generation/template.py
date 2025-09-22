
from random import shuffle
import os
import sys
import json

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
    
    with open(file_path, 'r') as file:
        return json.load(file)
    
def write_json_file(data, file_path):
    """
    Writes data to a JSON file.
    
    Args:
        data (dict): The data to be written to the file.
        file_path (str): The path to the JSON file.
    """
    if os.path.exists(file_path):
        print(f"Warning: The file {file_path} already exists and will be overwritten.", file=sys.stderr)
    
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def write_json_str(data, file_path):
    """
    Writes data to a JSON file, converting non-serializable types (like sets).

    Args:
        data (dict): The data to be written to the file.
        file_path (str): The path to the JSON file.
    """
    def convert(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    if os.path.exists(file_path):
        print(f"Warning: The file {file_path} already exists and will be overwritten.", file=sys.stderr)
    
    json_str = json.dumps(data, indent=4, default=convert)
    
    with open(file_path, 'w') as file:
        file.write(json_str)
        
def write_turtle_to_ttl(file_path, content):
    """
    Writes Turtle content to a TTL file.
    
    Args:
        file_path (str): The path to the TTL file.
        content (str): The Turtle content to be written.
    """
    content = "\n".join(content)  # Ensure content is a single string
    content = content.replace(' .', '.')
    content = content.replace(' ;', ';')

    with open(file_path, 'w') as file:
        file.write(content)

def relation_info(item, relations):
    rel_desc1 = ""
    rel_desc2 = ""
    rel_name1 = ""
    rel_name2 = ""
    for relation in relations:
        if relation['pid'] == item['possible_probs'][0]:
            rel_desc1 = relation['definition']
            rel_name1 = relation['name']
        if relation['pid'] == item['possible_probs'][1]:
            rel_desc2 = relation['definition']
            rel_name2 = relation['name']
    return rel_name1, rel_name2, rel_desc1, rel_desc2
        
def get_template_first(item: str, relations) -> str:
    """
    _summary_
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    rel_name1, rel_name2, rel_desc1, rel_desc2 = relation_info(item, relations)

    template = f""" What is the relation from {item['h'][0]} to {item['t'][0]} in the sentence?
                Sentence: {' '.join(item['tokens'])}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                C .) None of the above.
                Answer:"""
    return template
def get_template_second(item: str, relations) -> str:
    """
    _summary_
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    
    rel_name1, rel_name2, rel_desc1, rel_desc2 = relation_info(item, relations)

    template = f""" What is the relation from {item['t'][0]} to {item['h'][0]} in the sentence?
                Sentence: {' '.join(item['tokens'])}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                C .) None of the above.
                Answer:"""
    return template

def all_data(data, relations, out_file):
    templates = []

    for item in data:
        template = get_template_first(item, relations)
        item['template_1'] = template
        
        template = get_template_second(item, relations)
        item['template_2'] = template
        templates.append(item)
    shuffle(templates)
    write_json_file(templates, out_file)



if __name__ == "__main__":
    data = read_json_file("/Users/sefika/phd_projects/converse_relations/data/cleaned_asymetrics.json")
    relations = read_json_file("/Users/sefika/phd_projects/converse_relations/data/subset_inverse_relations.json")
    out_file = "/Users/sefika/phd_projects/converse_relations/data/templates.json"
    all_data(data, relations, out_file)