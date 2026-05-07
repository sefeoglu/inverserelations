import os
import sys
import json
import argparse

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    precision_recall_fscore_support,
)


def read_json_file(file_path):
    """
    Reads a JSON file and returns its content.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json_file(data, file_path):
    """
    Writes data to a JSON file.
    Safely handles numpy arrays/scalars by converting them with default serializer.
    """
    def to_serializable(obj):
        if hasattr(obj, "tolist"):
            return obj.tolist()
        if isinstance(obj, set):
            return list(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    dirpath = os.path.dirname(file_path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    if os.path.exists(file_path):
        print(
            f"Warning: The file {file_path} already exists and will be overwritten.",
            file=sys.stderr,
        )

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False, default=to_serializable)


def write_turtle_to_ttl(file_path, content):
    """
    Writes Turtle content to a TTL file.
    """
    content = "\n".join(content)
    content = content.replace(" .", ".")
    content = content.replace(" ;", ";")

    dirpath = os.path.dirname(file_path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def clean_response_label(response):
    """
    Extract class label from model response.
    Defaults to C if nothing valid is found.
    """
    response = str(response).strip()

    if "A" in response:
        return "A"
    if "B" in response:
        return "B"
    if "C" in response:
        return "C"
    return "C"


def gemini_convert_predictions(item):
    """
    Maps label letters to ground-truth relations.
    """
    return {
        "A": item["ground_truth_1"],
        "B": item["ground_truth_2"],
        "C": "",
    }


def mistral_convert_predictions(prediction):
    truths = [prediction["ground_truth_1"], prediction["ground_truth_2"]]
    pred_1, pred_2 = "", ""

    for truth in truths:
        if truth in prediction.get("predictions_1", ""):
            pred_1 = truth
        if truth in prediction.get("predictions_2", ""):
            pred_2 = truth

    return pred_1, pred_2


def llama3_convert_predictions(prediction):
    truths = [prediction["ground_truth_1"], prediction["ground_truth_2"]]
    pred_1, pred_2 = "", ""

    for truth in truths:
        if truth in prediction.get("predictions_1", ""):
            pred_1 = truth
        if truth in prediction.get("predictions_2", ""):
            pred_2 = truth

    return pred_1, pred_2


def qwen_convert_predictions(prediction):
    return {
        "A": prediction["ground_truth_1"],
        "B": prediction["ground_truth_2"],
        "C": "",
    }


def evaluate_predictions(input_data, predictions_data, out_result_report):
    """
    Evaluates predictions and stores:
    - accuracy
    - macro / micro precision, recall, f1
    - per-class precision, recall, f1, support
    """
    if len(input_data) != len(predictions_data):
        raise ValueError(
            f"Length mismatch: input_data has {len(input_data)} items, "
            f"predictions_data has {len(predictions_data)} items."
        )

    predictions = []
    gt_relations = []

    for pred_item, gt_item in zip(predictions_data, input_data):
        label_map = gemini_convert_predictions(gt_item)
        predicted_letter = clean_response_label(pred_item.get("response", ""))
        predicted_relation = label_map.get(predicted_letter, "")

        predictions.append(predicted_relation)
        gt_relations.append(pred_item["relation"])

    labels = sorted(set(gt_relations) | set(predictions))

    accuracy = accuracy_score(gt_relations, predictions)

    macro_precision = precision_score(
        gt_relations, predictions, average="macro", zero_division=0
    )
    macro_recall = recall_score(
        gt_relations, predictions, average="macro", zero_division=0
    )
    macro_f1 = f1_score(
        gt_relations, predictions, average="macro", zero_division=0
    )

    micro_precision = precision_score(
        gt_relations, predictions, average="micro", zero_division=0
    )
    micro_recall = recall_score(
        gt_relations, predictions, average="micro", zero_division=0
    )
    micro_f1 = f1_score(
        gt_relations, predictions, average="micro", zero_division=0
    )

    per_class_precision, per_class_recall, per_class_f1, support = (
        precision_recall_fscore_support(
            gt_relations,
            predictions,
            labels=labels,
            average=None,
            zero_division=0,
        )
    )

    per_class_results = {}
    for cls, p, r, f, s in zip(
        labels, per_class_precision, per_class_recall, per_class_f1, support
    ):
        per_class_results[str(cls)] = {
            "precision": float(p),
            "recall": float(r),
            "f1": float(f),
            "support": int(s),
        }

        print(f"Class {cls}:")
        print(f"  Precision: {p:.3f}")
        print(f"  Recall:    {r:.3f}")
        print(f"  F1-score:  {f:.3f}")
        print(f"  Support:   {s}")

    print(f"Accuracy:        {accuracy:.3f}")
    print(f"Macro Precision: {macro_precision:.3f}")
    print(f"Macro Recall:    {macro_recall:.3f}")
    print(f"Macro F1:        {macro_f1:.3f}")
    print(f"Micro Precision: {micro_precision:.3f}")
    print(f"Micro Recall:    {micro_recall:.3f}")
    print(f"Micro F1:        {micro_f1:.3f}")

    results = {
        "accuracy": float(accuracy),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "micro_precision": float(micro_precision),
        "micro_recall": float(micro_recall),
        "micro_f1": float(micro_f1),
        "labels": [str(x) for x in labels],
        "per_class_precision": [float(x) for x in per_class_precision],
        "per_class_recall": [float(x) for x in per_class_recall],
        "per_class_f1": [float(x) for x in per_class_f1],
        "support": [int(x) for x in support],
        "per_class": per_class_results,
    }

    write_json_file(results, out_result_report)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate model predictions against ground truth."
    )
    parser.add_argument(
        "--base_input_dir",
        type=str,
        default="/Users/sefika/phd_projects/converse_relations/data/mqa/fewrel",
        help="Base directory containing input JSON files.",
    )
    parser.add_argument(
        "--base_predictions_dir",
        type=str,
        default="/Users/sefika/phd_projects/converse_relations/results/fewrel/original",
        help="Base directory containing prediction JSON files.",
    )
    parser.add_argument(
        "--base_output_dir",
        type=str,
        default="/Users/sefika/phd_projects/converse_relations/results/fewrel/original/report_class",
        help="Base directory where evaluation reports will be saved.",
    )

    args = parser.parse_args()

    experiments = ["original"]
    input_files = ["original_templates_without_desc.json"]
    models = [{"model":"google/flan-t5-xl", "folder":"model_flan-t5-xl"},
              {"model":"meta-llama/Llama-3.1-8B-Instruct", "folder":"model_Llama-3.1-8B-Instruct"},
              {"model":"Qwen/Qwen2.5-7B-Instruct", "folder": "model_Qwen2.5-7B-Instruct"},
              {"model":"Qwen/Qwen3-4B-Instruct-2507", "folder":"model_Qwen3-4B-Instruct-2507"},
              {"model":"mistralai/Mistral-7B-Instruct-v0.3", "folder":"model_Mistral-7B-Instruct-v0.3"}

        ]

    for model in models:
        run_id =1

        for exp in experiments:
        
            print(f"\nEvaluating Experiment: {exp}, Model: {model['model']}, Input File: {input_files[0]}")
            gt_file = input_files[0]

            input_path = os.path.join(args.base_input_dir, gt_file)
            predictions_path = os.path.join(
                args.base_predictions_dir,
              
                model["folder"],
                f"tail_head_templates_without_desc_{run_id}.json",
            )
            output_path = os.path.join(
                args.base_output_dir,
                model["folder"],
             
                f"report_tail_head_templates_without_desc_{run_id}.json",
            )

            print(f"Experiment: {exp}, Model: {model['model']}, Input File: {gt_file}")
            print(f"Ground Truth: {input_path}")
            print(f"Predictions : {predictions_path}")
            print(f"Output      : {output_path}")

            input_data = read_json_file(input_path)
            predictions_data = read_json_file(predictions_path)

            evaluate_predictions(input_data, predictions_data, output_path)

if __name__ == "__main__":
    main()