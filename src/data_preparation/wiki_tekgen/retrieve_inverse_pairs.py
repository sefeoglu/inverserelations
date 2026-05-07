import os
import json
import argparse
from pdb import main


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_num} in {path}: {e}") from e
    return data


def write_json(data, path):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def retrieve_data(input_path, sentence_input_path, output_path):
    data = read_json(input_path)

    if "relations" not in data:
        raise KeyError(f"'relations' key not found in {input_path}")

    relations = data["relations"]
    sentences = read_jsonl(sentence_input_path)

    rel_labels = {
        relation["label"]
        for relation in relations
        if isinstance(relation, dict) and "label" in relation
    }

    new_data = [
        sentence
        for sentence in sentences
        if isinstance(sentence, dict) and sentence.get("rel_label") in rel_labels
    ]

    write_json(new_data, output_path)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        default="/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen/ontologies/10_culture_ontology_inverse.json",
        help="Path to input JSON file",
    )
    parser.add_argument(
        "--sentence_input",
        type=str,
        default="/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen/train/ont_10_culture_train.jsonl",
        help="Path to sentence input JSONL file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen_data/ont_10_culture_output.json",
        help="Path to output JSON file",
    )

    args = parser.parse_args()

    retrieve_data(args.input, args.sentence_input, args.output)
    print(f"Data retrieved and saved to {args.output}")

def save_bulk_data(input_path, output_path):
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    all_data = []
    rel = []
    for file_name in os.listdir(input_path):
        file_path = os.path.join(input_path, file_name) 
        data = read_json(file_path)
        all_data.extend(data)
        relations = [rel["rel_label"] for rel in data]
        rel.extend(relations)
    rel = list(set(rel))
    write_json(rel, os.path.join(dir_name, "relations.json"))
    write_json(all_data, output_path)


def save_bulk_relation_pairs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        default="/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen/ontologies",
        help="Path to input JSON file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen_data/bulk_relation_pairs.json",
        help="Path to output JSON file",
    )
    args = parser.parse_args()
    output_path = args.output
    input_path = args.input
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    all_data = []
    for file_name in os.listdir(input_path):
        file_path = os.path.join(input_path, file_name) 
        if "inverse"  in file_name:
            data = read_json(file_path)
            relations = data["relations"]
            all_data.extend(relations)
    write_json(all_data, output_path)

def map_relation_pairs():
    relations = read_json("/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen_data/relations.json")
    data = read_json("/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen_data/bulk_output.json")
    new_data = []
    for item in data:
        item['inverse_rel_label'] = relations[item['rel_label']]
        new_data.append(item)
    write_json(new_data, "/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen_data/bulk_output_with_inverse.json")
    
if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--input",
    #     type=str,
    #     default="/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen_data",
    #     help="Path to input directory containing JSONL files",
    # )
    # parser.add_argument(
    #     "--output",
    #     type=str,
    #     default="/Users/sefika/phd_projects/converse_relations/data/wikidata_tekgen_data/bulk_output.json",
    #     help="Path to output JSON file",
    # )
    # args = parser.parse_args()
    # save_bulk_data(args.input, args.output)
    # main()
    # save_bulk_relation_pairs()
    map_relation_pairs()