
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
    rel_name1 = item['rel_label']
    rel_name2 = item['inverse_rel_label']
   
    for relation_key, relation_value in relations.items():
        if relation_key == rel_name1:
            print(f"Relation found: {relation_key}")
            rel_desc1 = relation_value['description']
            rel_desc2 = relation_value['inverse']['description']
            break
    return rel_name1, rel_name2, rel_desc1, rel_desc2
        
def get_template_first(item: str, relations, type_ent = "AI") -> str:
    """
    Generates a template for the first question in a relation extraction task.
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    rel_name1, rel_name2, rel_desc1, rel_desc2 = relation_info(item, relations)
    o_entity1 = item['sub_label']
    o_entity2 = item['obj_label']
    if type_ent == "AI":
        entity1 = item['artificial_data'][0]['Artifical']
        entity2 = item['artificial_data'][1]['Artifical']
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                C .) None of the above.
                Please choose A, B, or C.
                Answer:"""
    else:
        entity1 = o_entity1
        entity2 = o_entity2
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                    Sentence: {item['sent']}
                    A .) {rel_name1}: {rel_desc1}.
                    B .) {rel_name2}: {rel_desc2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""
    return template, rel_name1

def get_template_second(item: str, relations, type_ent = "AI") -> str:
    """
    _summary_
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    
    rel_name1, rel_name2, rel_desc1, rel_desc2 = relation_info(item, relations)
    o_entity1 = item['sub_label']
    o_entity2 = item['obj_label']
    if type_ent == "AI":
        entity1 = item['artificial_data'][0]['Artifical']
        entity2 = item['artificial_data'][1]['Artifical']
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)

        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                C .) None of the above.
                Please choose A, B, or C.
                Answer:"""
    else:
        entity1 = item['sub_label']
        entity2 = item['obj_label']
        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                    Sentence: {item['sent']}
                    A .) {rel_name1}: {rel_desc1}.
                    B .) {rel_name2}: {rel_desc2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""
    return template, rel_name2
def get_template_nodesc_first(item: str, relations, type_ent = "AI") -> str:
    """
    Generates a template for the first question in a relation extraction task without descriptions.
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    rel_name1, rel_name2 = item['rel_label'], item['inverse_rel_label']
    o_entity1 = item['sub_label']
    o_entity2 = item['obj_label']
    if type_ent == "AI":
        entity1 = item['artificial_data'][0]['Artifical']
        entity2 = item['artificial_data'][1]['Artifical']
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""

    else:
        entity1 = item['sub_label']
        entity2 = item['obj_label']
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                    Sentence: {item['sent']}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""
    return template, rel_name1

def get_template_nodesc_second(item: str, relations, type_ent = "AI") -> str:
    """
    _summary_
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    
    rel_name1, rel_name2 = item['rel_label'], item['inverse_rel_label']

    if type_ent == "AI":
        entity1 = item['artificial_data'][0]['Artifical']
        entity2 = item['artificial_data'][1]['Artifical']
        o_entity1 = item['artificial_data'][0]['Original']
        o_entity2 = item['artificial_data'][1]['Original']
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)
        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""

    else:
        entity1 = item['sub_label']
        entity2 = item['obj_label']
        o_entity1 = item['sub_label']
        o_entity2 = item['obj_label']
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)
        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""
    return template, rel_name2

def all_data(data, relations, out_file, type_ent = "AI"):
    templates = []

    for item in data:
        template, ground_truth_1 = get_template_first(item, relations, type_ent = type_ent)
        item['template_1'], item['ground_truth_1'] = template, ground_truth_1

        template, ground_truth_2 = get_template_second(item, relations, type_ent = type_ent)
        item['template_2'], item['ground_truth_2'] = template, ground_truth_2
        templates.append(item)
    shuffle(templates)
    write_json_file(templates, out_file)


def all_data_nodesc(data, relations, out_file, type_ent = "AI"):
    templates = []

    for item in data:
        template, ground_truth_1 = get_template_nodesc_first(item, relations, type_ent = type_ent)
        item['template_1'], item['ground_truth_1'] = template, ground_truth_1

        template, ground_truth_2 = get_template_nodesc_second(item, relations, type_ent = type_ent)
        item['template_2'], item['ground_truth_2'] = template, ground_truth_2
        templates.append(item)
    shuffle(templates)

    write_json_file(templates, out_file)


def wiki_tekgen():
    data = read_json_file("../inverserelations/data/wikidata_tekgen_data/bulk_output_with_inverse.json")
    relations = read_json_file("../inverserelations/data/wikidata_tekgen_data/tekgen_relations.json")
    out_file = "../inverserelations/data/mqa/tekgen.json"
    all_data(data, relations, out_file.replace(".json", "_with_desc.json"), type_ent = "TEKGEN")
    # all_data_nodesc(data, relations, out_file.replace(".json", "_nodesc.json"), "TEKGEN")

def wiki_tekgen_artificial():
    data = read_json_file("../inverserelations/data/wikidata_tekgen_data/bulk_output_with_inverse_artificial.json")
    relations = read_json_file("../inverserelations/data/wikidata_tekgen_data/tekgen_relations.json")
    out_file = "../inverserelations/data/mqa/artificial_tekgen.json"
    all_data(data, relations, out_file.replace(".json", "_with_desc.json"), type_ent = "AI")
    # all_data_nodesc(data, relations, out_file.replace(".json", "_nodesc.json"), "AI")
if __name__ == "__main__":
   
    wiki_tekgen()
    wiki_tekgen_artificial()
    