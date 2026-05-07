
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
    rel_pid1 = item['head_to_tail']
    rel_pid2 = item['tail_to_head']
    rel_name1 = ""
    rel_name2 = ""
    for relation_item in relations:
        if relation_item['pid'] == rel_pid1:
            print(rel_pid1, rel_pid2)
            rel_desc1 = relation_item['definition']
            rel_name1 = relation_item['name']
            break
    for relation_item in relations:
        if relation_item['pid'] == rel_pid2:
            print(rel_pid1, rel_pid2)
            rel_desc2 = relation_item['definition']
            rel_name2 = relation_item['name']
            break
    
    return rel_name1, rel_name2, rel_desc1, rel_desc2
        
        
def get_template_first(item: str, relations, type_ent = "AI") -> str:
    """
    _summary_
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    rel_name1, rel_name2, rel_desc1, rel_desc2 = relation_info(item, relations)
    o_entity1 = item['head'][0]
    o_entity2 = item['tail'][0]
    if type_ent == "AI":
        a_entity1 = item['artificial_data'][0]['Artifical']
        a_entity2 = item['artificial_data'][1]['Artifical']
        sent = ' '.join(item['tokens']).replace(o_entity1, a_entity1).replace(o_entity2, a_entity2)
        template = f""" What is the relation from {a_entity1} to {a_entity2} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                C .) None of the above.
                Please choose A, B, or C.
                Answer:"""
    elif type_ent == "MT":
        entity1 = "XXXX"
        entity2 = "YYYY"
        sent = ' '.join(item['tokens']).replace(o_entity1, entity1).replace(o_entity2, entity2)
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                C .) None of the above.
                Please choose A, B, or C.
                Answer:"""
    else:

        template = f""" What is the relation from {item['head'][0]} to {item['tail'][0]} in the sentence?
                    Sentence: {' '.join(item['tokens'])}
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
    o_entity1 = item['head'][0]
    o_entity2 = item['tail'][0]
    if type_ent == "AI":
        a_entity1 = item['artificial_data'][0]['Artifical']
        a_entity2 = item['artificial_data'][1]['Artifical']


        sent = ' '.join(item['tokens']).replace(o_entity1, a_entity1).replace(o_entity2, a_entity2)
        template = f""" What is the relation from {a_entity2} to {a_entity1} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                C .) None of the above.
                Please choose A, B, or C.
                Answer:"""
    elif type_ent == "MT":

        entity1 = "XXXX"
        entity2 = "YYYY"
        sent = ' '.join(item['tokens']).replace(o_entity1, entity1).replace(o_entity2, entity2)
        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                C .) None of the above.
                Please choose A, B, or C.
                Answer:"""
    else:
        template = f""" What is the relation from {item['tail'][0]} to {item['head'][0]} in the sentence?
                    Sentence: {' '.join(item['tokens'])}
                    A .) {rel_name1}: {rel_desc1}.
                    B .) {rel_name2}: {rel_desc2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""
    return template, rel_name2
def get_template_nodesc_first(item: str, relations, type_ent = "AI") -> str:
    """
    _summary_
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    rel_name1, rel_name2, _, _ = relation_info(item, relations)
    o_entity1 = item['head'][0]
    o_entity2 = item['tail'][0]
    if type_ent == "AI":
        print("AI   ENTITIES", item['artificial_data'])
        a_entity1 = item['artificial_data'][0]['Artifical']
        a_entity2 = item['artificial_data'][1]['Artifical']
        sent = ' '.join(item['tokens'])
        sent = sent.lower().replace(o_entity1, a_entity1).replace(o_entity2, a_entity2)
        print("AI   SENTENCE", sent)
        template = f""" What is the relation from {a_entity1} to {a_entity2} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""
    elif type_ent == "MT":
        entity1 = "XXXX"
        entity2 = "YYYY"
        print("MT   ENTITIES", entity1, entity2)
        sent = ' '.join(item['tokens']).lower().replace(o_entity1, entity1).replace(o_entity2, entity2)
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""
    else:
        template = f""" What is the relation from {item['h'][0]} to {item['t'][0]} in the sentence?
                    Sentence: {' '.join(item['tokens'])}
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
    
    rel_name1, rel_name2, rel_desc1, rel_desc2 = relation_info(item, relations)
    if type_ent == "AI":
        a_entity1 = item['artificial_data'][0]['Artifical']
        a_entity2 = item['artificial_data'][1]['Artifical']
        sent = ' '.join(item['tokens']).replace(item['head'][0], a_entity1).replace(item['tail'][0], a_entity2)

        template = f""" What is the relation from {a_entity2} to {a_entity1} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""
    elif type_ent == "MT":
        entity1 = "XXXX"
        entity2 = "YYYY"
        sent = ' '.join(item['tokens']).replace(item['head'][0], entity1).replace(item['tail'][0], entity2)
        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    C .) None of the above.
                    Please choose A, B, or C.
                    Answer:"""
    else:
        sent = ' '.join(item['tokens'])
        template = f""" What is the relation from {item['tail'][0]} to {item['head'][0]} in the sentence?
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

def fewrel_mathematical_variable():

    data = read_json_file("/Users/sefika/phd_projects/converse_relations/zenodo/original_fewrel_inverse.json")
    relations = read_json_file("/Users/sefika/phd_projects/converse_relations/zenodo/fewrel_inverse_relations.json")
    out_file = "/Users/sefika/phd_projects/converse_relations/data/rag_data_1/mathematical_variable_templates.json"
    
    all_data(data, relations, out_file.replace(".json", "_with_desc.json"), "MT")
    all_data_nodesc(data, relations, out_file.replace(".json", "_without_desc.json"), "MT")

def fewrel_artificial_data():
    data = read_json_file("/Users/sefika/phd_projects/converse_relations/zenodo/artificial_fewrel_inverse.json")
    relations = read_json_file("/Users/sefika/phd_projects/converse_relations/zenodo/fewrel_inverse_relations.json")
    out_file = "/Users/sefika/phd_projects/converse_relations/data/rag_data_1/artificial_templates.json"
    all_data(data, relations, out_file.replace(".json", "_with_desc.json"), "AI")
    all_data_nodesc(data, relations, out_file.replace(".json", "_without_desc.json"), "AI")

def fewrel():
    data = read_json_file("/Users/sefika/phd_projects/converse_relations/data/cleaned_asymetrics.json")
    relations = read_json_file("/Users/sefika/phd_projects/converse_relations/data/subset_inverse_relations.json")
    out_file = "/Users/sefika/phd_projects/converse_relations/data/templates.json"
    all_data(data, relations, out_file.replace(".json", "_with_desc.json"))
    all_data_nodesc(data, relations, out_file.replace(".json", "_without_desc.json"))

def wiki_tekgen():
    data = read_json_file("/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen_data/bulk_output.json")
    relations = read_json_file("/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen_data/bulk_relation_pairs.json")
    out_file = "/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen_data/tec.json"
    all_data(data, relations, out_file.replace(".json", "_with_desc.json"))
    all_data_nodesc(data, relations, out_file.replace(".json", "_without_desc.json"))


if __name__ == "__main__":
    fewrel_mathematical_variable()
    fewrel_artificial_data()
    # wiki_tekgen()
    