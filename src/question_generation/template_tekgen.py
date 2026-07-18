from random import shuffle, choice
import os
import sys
import json
import argparse

MATH_ENTITY_1 = "XXXX"
MATH_ENTITY_2 = "YYYY"
MATH_NEG_ENTITY = "ZZZZ"

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
            Please choose A or B.
                Answer:"""
    elif type_ent == "MT":
        entity1 = MATH_ENTITY_1
        entity2 = MATH_ENTITY_2
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                Please choose A or B.
                Answer:"""
    else:
        entity1 = o_entity1
        entity2 = o_entity2
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                    Sentence: {item['sent']}
                    A .) {rel_name1}: {rel_desc1}.
                    B .) {rel_name2}: {rel_desc2}.
                    Please choose A or B.
                    Answer:"""
    return template, rel_name1

def get_template_second(item: str, relations, type_ent = "AI") -> str:
    """
    Generates a template for the second question in a relation extraction task.
    
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
            Please choose A or B.
                Answer:"""
    elif type_ent == "MT":
        entity1 = MATH_ENTITY_1
        entity2 = MATH_ENTITY_2
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)

        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
                Please choose A or B.
                Answer:"""
    else:
        entity1 = item['sub_label']
        entity2 = item['obj_label']
        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                    Sentence: {item['sent']}
                    A .) {rel_name1}: {rel_desc1}.
                    B .) {rel_name2}: {rel_desc2}.
                    Please choose A or B.
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
                    Please choose A or B.
                    Answer:"""

    elif type_ent == "MT":
        entity1 = MATH_ENTITY_1
        entity2 = MATH_ENTITY_2
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    Please choose A or B.
                    Answer:"""

    else:
        entity1 = item['sub_label']
        entity2 = item['obj_label']
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                    Sentence: {item['sent']}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    Please choose A or B.
                    Answer:"""
    return template, rel_name1

def get_template_nodesc_second(item: str, relations, type_ent = "AI") -> str:
    """
    Generates a template for the second question in a relation extraction task without descriptions.
    
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
                    Please choose A or B.
                    Answer:"""

    elif type_ent == "MT":
        entity1 = MATH_ENTITY_1
        entity2 = MATH_ENTITY_2
        o_entity1 = item['sub_label']
        o_entity2 = item['obj_label']
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)
        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    Please choose A or B.
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
                    Please choose A or B.
                    Answer:"""
    return template, rel_name2


def build_negative_entity_pool(data, type_ent="AI"):
    """
    Build a pool of entity mentions used to sample negative (unrelated) entities.
    """
    entity_pool = []
    for item in data:
        if type_ent == "AI":
            entity_pool.append(item['artificial_data'][0]['Artifical'])
            entity_pool.append(item['artificial_data'][1]['Artifical'])
        else:
            entity_pool.append(item['sub_label'])
            entity_pool.append(item['obj_label'])

    # Deduplicate while preserving order.
    return list(dict.fromkeys(entity_pool))


def get_item_entities_and_sentence(item, type_ent="AI"):
    """
    Return entity mentions and sentence representation for the configured entity type.
    """
    if type_ent == "AI":
        entity1 = item['artificial_data'][0]['Artifical']
        entity2 = item['artificial_data'][1]['Artifical']
        o_entity1 = item['sub_label']
        o_entity2 = item['obj_label']
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)
    elif type_ent == "MT":
        entity1 = MATH_ENTITY_1
        entity2 = MATH_ENTITY_2
        o_entity1 = item['sub_label']
        o_entity2 = item['obj_label']
        sent = item['sent'].replace(o_entity1, entity1).replace(o_entity2, entity2)
    else:
        entity1 = item['sub_label']
        entity2 = item['obj_label']
        sent = item['sent']
    return entity1, entity2, sent


def sample_negative_entity(entity1, entity2, entity_pool):
    """
    Sample an entity that is different from both entities in the current item.
    """
    candidates = [ent for ent in entity_pool if ent not in {entity1, entity2}]
    if not candidates:
        return "Unknown Entity"
    return choice(candidates)


def sample_negative_relation_pair(rel_name1, rel_name2, relations):
    """
    Sample a real relation pair (relation + inverse relation) different from the item's pair.
    """
    relation_names = list(relations.keys())
    candidates = [
        relation_name
        for relation_name in relation_names
        if relation_name != rel_name1 and relations[relation_name]['inverse']['name'] != rel_name2
    ]

    if not candidates:
        # Fallback to the item's pair when no alternative is available.
        return rel_name1, rel_name2, relations[rel_name1]['description'], relations[rel_name1]['inverse']['description']

    sampled_relation = choice(candidates)
    sampled_inverse = relations[sampled_relation]['inverse']['name']
    sampled_desc = relations[sampled_relation]['description']
    sampled_inverse_desc = relations[sampled_relation]['inverse']['description']
    return sampled_relation, sampled_inverse, sampled_desc, sampled_inverse_desc


def add_negative_choice_to_prompt(template, negative_relation, negative_description="", include_desc=True):
    """
    Inject a third option (C) into an existing prompt template.
    """
    marker = "Please choose A or B."
    lines = template.split("\n")

    for i, line in enumerate(lines):
        if marker in line:
            indent = line[:line.index("P")]
            if include_desc:
                negative_line = f"{indent}C .) {negative_relation}: {negative_description}."
            else:
                negative_line = f"{indent}C .) {negative_relation}."

            lines[i:i + 1] = [negative_line, f"{indent}Please choose A, B, or C."]
            break

    return "\n".join(lines)


def get_negative_templates(item, relations, entity_pool, type_ent="AI", include_desc=True):
    """
    Generate two negative prompts with real relation labels as answer options.
    """
    rel_name1, rel_name2, _, _ = relation_info(item, relations)
    neg_rel_name1, neg_rel_name2, neg_rel_desc1, neg_rel_desc2 = sample_negative_relation_pair(
        rel_name1,
        rel_name2,
        relations
    )
    entity1, entity2, sent = get_item_entities_and_sentence(item, type_ent=type_ent)
    if type_ent == "MT":
        negative_entity = MATH_NEG_ENTITY
    else:
        negative_entity = sample_negative_entity(entity1, entity2, entity_pool)

    if include_desc:
        template_1 = f""" What is the relation from {entity1} to {negative_entity} in the sentence?
                Sentence: {sent}
                A .) {neg_rel_name1}: {neg_rel_desc1}.
                B .) {neg_rel_name2}: {neg_rel_desc2}.
            Please choose A or B.
                Answer:"""
        template_2 = f""" What is the relation from {negative_entity} to {entity2} in the sentence?
                Sentence: {sent}
                A .) {neg_rel_name1}: {neg_rel_desc1}.
                B .) {neg_rel_name2}: {neg_rel_desc2}.
            Please choose A or B.
                Answer:"""
    else:
        template_1 = f""" What is the relation from {entity1} to {negative_entity} in the sentence?
                    Sentence: {sent}
                    A .) {neg_rel_name1}.
                    B .) {neg_rel_name2}.
                    Please choose A or B.
                    Answer:"""
        template_2 = f""" What is the relation from {negative_entity} to {entity2} in the sentence?
                    Sentence: {sent}
                    A .) {neg_rel_name1}.
                    B .) {neg_rel_name2}.
                    Please choose A or B.
                    Answer:"""

    # Negative samples now use real relation labels instead of None-of-the-above labels.
    return template_1, template_2, neg_rel_name1, neg_rel_name2


def build_experiment_prompt_list(item):
    """
    Build one list that combines positive and negative prompts for a single experiment.
    """
    prompt_list = [
        {
            "sample_type": "positive",
            "prompt_id": "positive_1",
            "prompt": item['template_1'],
            "ground_truth": item['ground_truth_1']
        },
        {
            "sample_type": "positive",
            "prompt_id": "positive_2",
            "prompt": item['template_2'],
            "ground_truth": item['ground_truth_2']
        }
    ]

    if 'template_negative_1' in item and 'ground_truth_negative_1' in item:
        prompt_list.append(
            {
                "sample_type": "negative",
                "prompt_id": "negative_1",
                "prompt": item['template_negative_1'],
                "ground_truth": item['ground_truth_negative_1']
            }
        )

    if 'template_negative_2' in item and 'ground_truth_negative_2' in item:
        prompt_list.append(
            {
                "sample_type": "negative",
                "prompt_id": "negative_2",
                "prompt": item['template_negative_2'],
                "ground_truth": item['ground_truth_negative_2']
            }
        )

    return prompt_list

def all_data(data, relations, out_file, type_ent = "AI", include_negative=False):
    """
    Generate templates with descriptions.
    
    Args:
        data: List of data items
        relations: Relations dictionary
        out_file: Output file path
        type_ent: Entity type (AI, TEKGEN, etc.)
    """
    templates = []
    entity_pool = build_negative_entity_pool(data, type_ent=type_ent) if include_negative else None

    for item in data:
        template, ground_truth_1 = get_template_first(item, relations, type_ent = type_ent)
        item['template_1'], item['ground_truth_1'] = template, ground_truth_1

        template, ground_truth_2 = get_template_second(item, relations, type_ent = type_ent)
        item['template_2'], item['ground_truth_2'] = template, ground_truth_2

        if include_negative:
            neg_rel_name1, neg_rel_name2, neg_rel_desc1, neg_rel_desc2 = sample_negative_relation_pair(
                item['rel_label'],
                item['inverse_rel_label'],
                relations
            )
            item['template_1'] = add_negative_choice_to_prompt(
                item['template_1'],
                neg_rel_name1,
                neg_rel_desc1,
                include_desc=True
            )
            item['template_2'] = add_negative_choice_to_prompt(
                item['template_2'],
                neg_rel_name2,
                neg_rel_desc2,
                include_desc=True
            )

            # Ensure legacy standalone negative fields are not carried into output.
            item.pop('template_negative_1', None)
            item.pop('ground_truth_negative_1', None)
            item.pop('template_negative_2', None)
            item.pop('ground_truth_negative_2', None)

        # Keep one combined list for experiments that need positive and negative samples together.
        item['experiment_prompt_list'] = build_experiment_prompt_list(item)

        templates.append(item)
    shuffle(templates)
    write_json_file(templates, out_file)


def all_data_nodesc(data, relations, out_file, type_ent = "AI", include_negative=False):
    """
    Generate templates without descriptions.
    
    Args:
        data: List of data items
        relations: Relations dictionary
        out_file: Output file path
        type_ent: Entity type (AI, TEKGEN, etc.)
    """
    templates = []
    entity_pool = build_negative_entity_pool(data, type_ent=type_ent) if include_negative else None

    for item in data:
        template, ground_truth_1 = get_template_nodesc_first(item, relations, type_ent = type_ent)
        item['template_1'], item['ground_truth_1'] = template, ground_truth_1

        template, ground_truth_2 = get_template_nodesc_second(item, relations, type_ent = type_ent)
        item['template_2'], item['ground_truth_2'] = template, ground_truth_2

        if include_negative:
            neg_rel_name1, neg_rel_name2, _, _ = sample_negative_relation_pair(
                item['rel_label'],
                item['inverse_rel_label'],
                relations
            )
            item['template_1'] = add_negative_choice_to_prompt(
                item['template_1'],
                neg_rel_name1,
                include_desc=False
            )
            item['template_2'] = add_negative_choice_to_prompt(
                item['template_2'],
                neg_rel_name2,
                include_desc=False
            )

            # Ensure legacy standalone negative fields are not carried into output.
            item.pop('template_negative_1', None)
            item.pop('ground_truth_negative_1', None)
            item.pop('template_negative_2', None)
            item.pop('ground_truth_negative_2', None)

        # Keep one combined list for experiments that need positive and negative samples together.
        item['experiment_prompt_list'] = build_experiment_prompt_list(item)

        templates.append(item)
    shuffle(templates)
    write_json_file(templates, out_file)


def process_wiki_tekgen(data_file, relations_file, output_file, include_nodesc=False, type_ent="TEKGEN", include_negative=False):
    """
    Process WikiTekGen data.
    
    Args:
        data_file: Path to data JSON file
        relations_file: Path to relations JSON file
        output_file: Path for output file
        include_nodesc: Whether to include nodesc version
        type_ent: Entity type
    """
    data = read_json_file(data_file)
    relations = read_json_file(relations_file)
    
    all_data(
        data,
        relations,
        output_file.replace(".json", "_with_desc.json"),
        type_ent=type_ent,
        include_negative=include_negative
    )
    
    if include_nodesc:
        all_data_nodesc(
            data,
            relations,
            output_file.replace(".json", "_without_desc.json"),
            type_ent=type_ent,
            include_negative=include_negative
        )


def main():
    parser = argparse.ArgumentParser(
        description="Generate relation templates from WikiTekGen or similar data sources.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate templates for WikiTekGen with descriptions
  python script.py --data data.json --relations relations.json --output output.json

  # Generate templates with both descriptions and without
  python script.py --data data.json --relations relations.json --output output.json --include-nodesc

        # Generate templates including negative prompts
    python script.py --data data.json --relations relations.json --output output.json --include-negative

  # Specify entity type (default: TEKGEN)
  python script.py --data data.json --relations relations.json --output output.json --type-ent AI

    # Generate templates with mathematical-variable entities
    python script.py --data data.json --relations relations.json --output output.json --type-ent MT

  # Generate templates for artificial WikiTekGen data
  python script.py --data artificial_data.json --relations relations.json --output artificial_output.json --type-ent AI
        """
    )

    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Path to the input data JSON file'
    )
    
    parser.add_argument(
        '--relations',
        type=str,
        required=True,
        help='Path to the relations JSON file'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Path for the output file (will create _with_desc.json and optionally _without_desc.json)'
    )
    
    parser.add_argument(
        '--type-ent',
        type=str,
        default='TEKGEN',
        choices=['TEKGEN', 'AI', 'MT', 'WIKI', 'OTHER'],
        help='Entity type for template generation (default: TEKGEN)'
    )
    
    parser.add_argument(
        '--include-nodesc',
        action='store_true',
        help='Also generate templates without descriptions (_without_desc.json)'
    )

    parser.add_argument(
        '--include-negative',
        action='store_true',
        help='Add a negative relation as option C in each main prompt'
    )

    args = parser.parse_args()

    # Validate input files exist
    if not os.path.exists(args.data):
        parser.error(f"Data file not found: {args.data}")
    if not os.path.exists(args.relations):
        parser.error(f"Relations file not found: {args.relations}")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    print(f"Processing WikiTekGen data...")
    print(f"Data file: {args.data}")
    print(f"Relations file: {args.relations}")
    print(f"Output file: {args.output}")
    print(f"Entity type: {args.type_ent}")
    print(f"Include without descriptions: {args.include_nodesc}")
    print(f"Include negative prompts: {args.include_negative}")
    print()

    try:
        process_wiki_tekgen(
            args.data,
            args.relations,
            args.output,
            include_nodesc=args.include_nodesc,
            type_ent=args.type_ent,
            include_negative=args.include_negative
        )
        
        print(f"✓ Templates generated successfully!")
        print(f"✓ Output files:")
        print(f"  - {args.output.replace('.json', '_with_desc.json')}")
        if args.include_nodesc:
            print(f"  - {args.output.replace('.json', '_without_desc.json')}")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Error decoding JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"✗ Error: Missing expected key in data - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()