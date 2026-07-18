from random import shuffle, choice
import os
import sys
import json
import argparse
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from utils import read_json_file, write_json_file

MATH_ENTITY_1 = "XXXX"
MATH_ENTITY_2 = "YYYY"
ARTIFICIAL_ENTITY_KEY = "Artifical"


def build_sentence(tokens, source_entity_1, source_entity_2, target_entity_1, target_entity_2, lowercase=False):
    """Build a sentence from tokens and replace the two entity mentions."""
    sentence = " ".join(tokens)
    if lowercase:
        sentence = sentence.lower()
    return sentence.replace(source_entity_1, target_entity_1).replace(source_entity_2, target_entity_2)


def find_relation(relations, pid):
    """Return the relation name and definition for a PID, or empty strings if not found."""
    for relation_item in relations:
        if relation_item["pid"] == pid:
            return relation_item["name"], relation_item["definition"]
    return "", ""


def get_required_item_value(item, key):
    """Read a required item field and raise a descriptive error if it is missing."""
    if key not in item:
        raise KeyError(f"Missing required key '{key}' in input item: {item}")
    return item[key]


def get_artificial_entity(item, index):
    """Return the synthetic entity value using the dataset's existing field name."""
    artificial_data = get_required_item_value(item, 'artificial_data')
    if len(artificial_data) <= index:
        raise KeyError(
            f"Missing artificial_data[{index}] in input item: {item}"
        )
    return get_required_item_value(artificial_data[index], ARTIFICIAL_ENTITY_KEY)

def relation_info(item, relations):
    rel_pid1 = get_required_item_value(item, 'head_to_tail')
    rel_pid2 = get_required_item_value(item, 'tail_to_head')
    rel_name1, rel_desc1 = find_relation(relations, rel_pid1)
    rel_name2, rel_desc2 = find_relation(relations, rel_pid2)

    return rel_name1, rel_name2, rel_desc1, rel_desc2


def build_relation_pair_pool(data):
    """Collect unique relation/inverse-relation PID pairs from the dataset."""
    unique_pairs = []
    seen_pairs = set()
    for item in data:
        pair = (
            get_required_item_value(item, 'head_to_tail'),
            get_required_item_value(item, 'tail_to_head')
        )
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_pairs.append(pair)
    return unique_pairs


def sample_negative_relation_pair(rel_pid1, rel_pid2, pair_pool, relations):
    """Sample a real negative relation pair that differs from the item's true pair."""
    rel_name1, _ = find_relation(relations, rel_pid1)
    rel_name2, _ = find_relation(relations, rel_pid2)

    candidates = []
    for pair in pair_pool:
        if pair == (rel_pid1, rel_pid2):
            continue
        cand_name1, _ = find_relation(relations, pair[0])
        cand_name2, _ = find_relation(relations, pair[1])
        if cand_name1 in {rel_name1, rel_name2}:
            continue
        if cand_name2 in {rel_name1, rel_name2}:
            continue
        candidates.append(pair)
    if not candidates:
        for pair in pair_pool:
            cand_name1, _ = find_relation(relations, pair[0])
            cand_name2, _ = find_relation(relations, pair[1])
            if cand_name1 != rel_name1 and cand_name2 != rel_name2:
                candidates.append(pair)
    if not candidates:
        candidates = [(rel_pid1, rel_pid2)]

    neg_pid1, neg_pid2 = choice(candidates)
    neg_name1, neg_desc1 = find_relation(relations, neg_pid1)
    neg_name2, neg_desc2 = find_relation(relations, neg_pid2)
    return neg_name1, neg_name2, neg_desc1, neg_desc2


def add_negative_choice_to_prompt(template, negative_relation, negative_description="", include_desc=True):
    """Inject a third option (C) into an existing prompt template."""
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


def normalize_prompt_indentation(template):
    """Normalize generated prompt indentation for stable JSON output."""
    lines = template.split("\n")
    normalized_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Sentence:"):
            normalized_lines.append(f"                    {stripped}")
        elif stripped.startswith(("A .)", "B .)", "C .)", "Please choose", "Answer:")):
            normalized_lines.append(f"                    {stripped}")
        elif normalized_lines:
            normalized_lines.append(line)
        else:
            normalized_lines.append(line)
    return "\n".join(normalized_lines)
        
        
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
        a_entity1 = get_artificial_entity(item, 0)
        a_entity2 = get_artificial_entity(item, 1)
        sent = build_sentence(item['tokens'], o_entity1, o_entity2, a_entity1, a_entity2)
        template = f""" What is the relation from {a_entity1} to {a_entity2} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
            Please choose A or B.
                Answer:"""
    elif type_ent == "MT":
        entity1 = MATH_ENTITY_1
        entity2 = MATH_ENTITY_2
        sent = build_sentence(item['tokens'], o_entity1, o_entity2, entity1, entity2)
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
            Please choose A or B.
                Answer:"""
    else:

        template = f""" What is the relation from {item['head'][0]} to {item['tail'][0]} in the sentence?
                    Sentence: {' '.join(item['tokens'])}
                    A .) {rel_name1}: {rel_desc1}.
                    B .) {rel_name2}: {rel_desc2}.
                    Please choose A or B.
                    Answer:"""
    return normalize_prompt_indentation(template), rel_name1

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
        a_entity1 = get_artificial_entity(item, 0)
        a_entity2 = get_artificial_entity(item, 1)
        sent = build_sentence(item['tokens'], o_entity1, o_entity2, a_entity1, a_entity2)
        template = f""" What is the relation from {a_entity2} to {a_entity1} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
            Please choose A or B.
                Answer:"""
    elif type_ent == "MT":
        entity1 = MATH_ENTITY_1
        entity2 = MATH_ENTITY_2
        sent = build_sentence(item['tokens'], o_entity1, o_entity2, entity1, entity2)
        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                Sentence: {sent}
                A .) {rel_name1}: {rel_desc1}.
                B .) {rel_name2}: {rel_desc2}.
            Please choose A or B.
                Answer:"""
    else:
        template = f""" What is the relation from {item['tail'][0]} to {item['head'][0]} in the sentence?
                    Sentence: {' '.join(item['tokens'])}
                    A .) {rel_name1}: {rel_desc1}.
                    B .) {rel_name2}: {rel_desc2}.
                    Please choose A or B.
                    Answer:"""
    return normalize_prompt_indentation(template), rel_name2

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
        a_entity1 = get_artificial_entity(item, 0)
        a_entity2 = get_artificial_entity(item, 1)
        sent = build_sentence(item['tokens'], o_entity1, o_entity2, a_entity1, a_entity2, lowercase=True)
        template = f""" What is the relation from {a_entity1} to {a_entity2} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    Please choose A or B.
                    Answer:"""
    elif type_ent == "MT":
        entity1 = MATH_ENTITY_1
        entity2 = MATH_ENTITY_2
        sent = build_sentence(item['tokens'], o_entity1, o_entity2, entity1, entity2, lowercase=True)
        template = f""" What is the relation from {entity1} to {entity2} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    Please choose A or B.
                    Answer:"""
    else:
        template = f""" What is the relation from {item['head'][0]} to {item['tail'][0]} in the sentence?
                    Sentence: {' '.join(item['tokens'])}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                Please choose A or B.
                    Answer:"""
    return normalize_prompt_indentation(template), rel_name1

def get_template_nodesc_second(item: str, relations, type_ent = "AI") -> str:
    """
    _summary_
    
    Args:
        item (str): _description_
        Returns:
            str: _description_"""
    
    rel_name1, rel_name2, rel_desc1, rel_desc2 = relation_info(item, relations)
    if type_ent == "AI":
        a_entity1 = get_artificial_entity(item, 0)
        a_entity2 = get_artificial_entity(item, 1)
        sent = build_sentence(item['tokens'], item['head'][0], item['tail'][0], a_entity1, a_entity2)

        template = f""" What is the relation from {a_entity2} to {a_entity1} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    Please choose A or B.
                    Answer:"""
    elif type_ent == "MT":
        entity1 = MATH_ENTITY_1
        entity2 = MATH_ENTITY_2
        sent = build_sentence(item['tokens'], item['head'][0], item['tail'][0], entity1, entity2)
        template = f""" What is the relation from {entity2} to {entity1} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    Please choose A or B.
                    Answer:"""
    else:
        sent = ' '.join(item['tokens'])
        template = f""" What is the relation from {item['tail'][0]} to {item['head'][0]} in the sentence?
                    Sentence: {sent}
                    A .) {rel_name1}.
                    B .) {rel_name2}.
                    Please choose A or B.
                    Answer:"""
    return normalize_prompt_indentation(template), rel_name2


def build_experiment_prompt_list(item):
    """Build one list that combines the prompt pair for a single experiment."""
    return [
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

def all_data(data, relations, out_file, type_ent = "AI"):
    templates = []
    pair_pool = build_relation_pair_pool(data)

    for item in data:
        template, ground_truth_1 = get_template_first(item, relations, type_ent = type_ent)
        item['template_1'], item['ground_truth_1'] = template, ground_truth_1

        template, ground_truth_2 = get_template_second(item, relations, type_ent = type_ent)
        item['template_2'], item['ground_truth_2'] = template, ground_truth_2

        neg_name1, neg_name2, neg_desc1, neg_desc2 = sample_negative_relation_pair(
            item['head_to_tail'],
            item['tail_to_head'],
            pair_pool,
            relations
        )
        item['template_1'] = add_negative_choice_to_prompt(item['template_1'], neg_name1, neg_desc1, include_desc=True)
        item['template_2'] = add_negative_choice_to_prompt(item['template_2'], neg_name2, neg_desc2, include_desc=True)
        item['experiment_prompt_list'] = build_experiment_prompt_list(item)
        templates.append(item)
    shuffle(templates)
    write_json_file(templates, out_file)


def all_data_nodesc(data, relations, out_file, type_ent = "AI"):
    templates = []
    pair_pool = build_relation_pair_pool(data)

    for item in data:
        template, ground_truth_1 = get_template_nodesc_first(item, relations, type_ent = type_ent)
        item['template_1'], item['ground_truth_1'] = template, ground_truth_1

        template, ground_truth_2 = get_template_nodesc_second(item, relations, type_ent = type_ent)
        item['template_2'], item['ground_truth_2'] = template, ground_truth_2

        neg_name1, neg_name2, _, _ = sample_negative_relation_pair(
            item['head_to_tail'],
            item['tail_to_head'],
            pair_pool,
            relations
        )
        item['template_1'] = add_negative_choice_to_prompt(item['template_1'], neg_name1, include_desc=False)
        item['template_2'] = add_negative_choice_to_prompt(item['template_2'], neg_name2, include_desc=False)
        item['experiment_prompt_list'] = build_experiment_prompt_list(item)
        templates.append(item)
    shuffle(templates)
    write_json_file(templates, out_file)

def fewrel_mathematical_variable(data_file, relations_file, out_file):
    data = read_json_file(data_file)
    relations = read_json_file(relations_file)
    
    all_data(data, relations, out_file.replace(".json", "_with_desc.json"), "MT")
    all_data_nodesc(data, relations, out_file.replace(".json", "_without_desc.json"), "MT")

def fewrel_artificial_data(data_file, relations_file, out_file):
    data = read_json_file(data_file)
    relations = read_json_file(relations_file)
    all_data(data, relations, out_file.replace(".json", "_with_desc.json"), "AI")
    all_data_nodesc(data, relations, out_file.replace(".json", "_without_desc.json"), "AI")

def fewrel(data_file, relations_file, out_file):
    data = read_json_file(data_file)
    relations = read_json_file(relations_file)
    all_data(data, relations, out_file.replace(".json", "_with_desc.json"), "FEWREL")
    all_data_nodesc(data, relations, out_file.replace(".json", "_without_desc.json"), "FEWREL")


def main():
    parser = argparse.ArgumentParser(
        description="Generate relation templates from JSON data files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate templates for mathematical variables
  python src/question_generation/template.py --mode mt --data data.json --relations relations.json --output output.json

  # Generate templates for artificial data
  python src/question_generation/template.py --mode ai --data data.json --relations relations.json --output output.json

  # Generate templates for fewrel (default mode)
  python src/question_generation/template.py --mode fewrel --data data.json --relations relations.json --output output.json
        """
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['mt', 'ai', 'fewrel'],
        default='fewrel',
        help='Processing mode: mt (mathematical variable), ai (artificial data), or fewrel (default)'
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
        help='Path for the output file (will create _with_desc.json and _without_desc.json variants)'
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

    print(f"Processing mode: {args.mode}")
    print(f"Data file: {args.data}")
    print(f"Relations file: {args.relations}")
    print(f"Output file: {args.output}")
    print()

    try:
        if args.mode == 'mt':
            fewrel_mathematical_variable(args.data, args.relations, args.output)
        elif args.mode == 'ai':
            fewrel_artificial_data(args.data, args.relations, args.output)
        else:  # fewrel
            fewrel(args.data, args.relations, args.output)
        
        print(f"✓ Templates generated successfully!")
        print(f"✓ Output files:")
        print(f"  - {args.output.replace('.json', '_with_desc.json')}")
        print(f"  - {args.output.replace('.json', '_without_desc.json')}")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Error decoding JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
