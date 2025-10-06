
from random import shuffle
import os
import sys
import json
from tqdm import tqdm
import argparse

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

def get_triples(triples, h, t):
    triple_list = []
    if triples is None:
        return triple_list
    for triple in triples:
       
        if 'subjectLabel' in triple:
            subject = triple['subjectLabel']['value']
        else:
            subject = h
        
        predicate = triple['predicateLabel']['value'].split('/')[-1]
        if 'objectLabel' not in triple:
            object_ = t
        else:
            object_ = triple['objectLabel']['value']
        triple_list.append((subject, predicate, object_))
    return triple_list

def get_entity_information(item):
    head_info = item['head_info']
    tail_info = item['tail_info']
    h = item['h'][0]
    t = item['t'][0]
    head_triples = get_triples(head_info, h, t)
    tail_triples = get_triples(tail_info, h, t)
    return head_triples, tail_triples

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
    ent_1_info, ent_2_info = get_entity_information(item)

    template = f""" What is the relation from {item['h'][0]} to {item['t'][0]} in the sentence?
                Head entity information: {ent_1_info}
                Tail entity information: {ent_2_info}
                Sentence: {' '.join(item['tokens'])}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                C .) None of the above.
                Please choose A, B, or C.
                Answer:"""
    return template, rel_name1
def get_template_second(item: str, relations) -> str:
    """
    _summary_
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    
    rel_name1, rel_name2, rel_desc1, rel_desc2 = relation_info(item, relations)
    ent_1_info, ent_2_info = get_entity_information(item)

    template = f""" What is the relation from  {item['t'][0]} to {item['h'][0]} in the sentence?
                Head entity information: {ent_1_info}
                Tail entity information: {ent_2_info}
                Sentence: {' '.join(item['tokens'])}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                C .) None of the above.
                Please choose A, B, or C.
                Answer:"""
    return template, rel_name2
def get_template_nodesc_first(item: str, relations) -> str:
    """
    _summary_
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    rel_name1, rel_name2, _, _ = relation_info(item, relations)

    template = f""" What is the relation from [HEAD] {item['h'][0]} [/HEAD] to [TAIL] {item['t'][0]} [/TAIL] in the sentence?
                Sentence: {' '.join(item['tokens'])}
                A .) {rel_name1}.
                B .) {rel_name2}.
                C .) None of the above.
                Please choose A, B, or C.
                Answer:"""
    return template, rel_name1
def get_template_nodesc_second(item: str, relations) -> str:
    """
    _summary_
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    
    rel_name1, rel_name2, _, _ = relation_info(item, relations)

    template = f""" What is the relation from [TAIL] {item['t'][0]} [/TAIL] to [HEAD] {item['h'][0]} [/HEAD] in the sentence?
                Sentence: {' '.join(item['tokens'])}
                A .) {rel_name1}.
                B .) {rel_name2}.
                C .) None of the above.
                Please choose A, B, or C.
                Answer:"""
    
    return template, rel_name2

def all_data(data, relations, out_file):
    templates = []

    for item in data:
        template, ground_truth_1 = get_template_first(item, relations)
        item['template_1'], item['ground_truth_1'] = template, ground_truth_1

        template, ground_truth_2 = get_template_second(item, relations)
        item['template_2'], item['ground_truth_2'] = template, ground_truth_2
        new_item = {'h': item['h'], 't': item['t'], 'tokens': item['tokens'], 'possible_probs': item['possible_probs'], 'template_1': item['template_1'], 'ground_truth_1': item['ground_truth_1'], 'template_2': item['template_2'], 'ground_truth_2': item['ground_truth_2']}
        templates.append(new_item)

    shuffle(templates)
    write_json_file(templates, out_file)


def all_data_nodesc(data, relations, out_file):
    templates = []

    for item in data:
        template, ground_truth_1 = get_template_nodesc_first(item, relations)
        item['template_1'], item['ground_truth_1'] = template, ground_truth_1

        template, ground_truth_2 = get_template_nodesc_second(item, relations)
        item['template_2'], item['ground_truth_2'] = template, ground_truth_2
        new_item = {'h': item['h'], 't': item['t'], 'tokens': item['tokens'], 'possible_probs': item['possible_probs'], 'template_1': item['template_1'], 'ground_truth_1': item['ground_truth_1'], 'template_2': item['template_2'], 'ground_truth_2': item['ground_truth_2']}
        templates.append(new_item)

    shuffle(templates)
    write_json_file(templates, out_file)
def remove_duplicate_dicts(dict_list):
    seen = set()
    unique_list = []
    for d in dict_list:
        # Convert dict to a JSON string with sorted keys — safe for nested/unhashable values
        key = json.dumps(d, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique_list.append(d)
    return unique_list
if __name__ == "__main__":
    # data = read_json_file("/Users/sefika/phd_projects/converse_relations/data/cleaned_asymetrics.json")
    argparser = argparse.ArgumentParser(description="Generate templates for question generation.")
    argparser.add_argument('--input_relations', type=str, default="/Users/sefika/phd_projects/converse_relations/data/subset_inverse_relations.json", help="Path to the input relations JSON file.")
    argparser.add_argument('--input_folder', type=str, default="/Users/sefika/phd_projects/converse_relations/results/entities/", help="Path to the folder containing entity JSON files.")
    argparser.add_argument('--output_with_desc', type=str, default="/Users/sefika/phd_projects/converse_relations/data/rag_data/templates_with_desc.json", help="Path to the output JSON file with descriptions.")
    argparser.add_argument('--output_without_desc', type=str, default="/Users/sefika/phd_projects/converse_relations/data/rag_data/templates_without_desc.json", help="Path to the output JSON file without descriptions.")
    args = argparser.parse_args()
    relations = read_json_file(args.input_relations)
    out_file = args.output_with_desc
    folder_path = args.input_folder
    all = []
    for file_id in range(0, 5):
        file_path = os.path.join(folder_path, f"cleaned_asymetrics_entity_{file_id}.json")
        data = read_json_file(file_path)
        all.extend(data)
    all = remove_duplicate_dicts(all)
    print(f"Total unique items: {len(all)}")
    all_data(all, relations, out_file)
    all_data_nodesc(all, relations, out_file.replace("_with_desc.json", "_without_desc.json"))