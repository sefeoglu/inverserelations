import os
import sys
import json
import argparse
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    precision_recall_fscore_support,
)

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from utils import read_json_file, write_json_file


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
    """
    Extracts predictions from Mistral model output.
    """
    truths = [prediction["ground_truth_1"], prediction["ground_truth_2"]]
    pred_1, pred_2 = "", ""

    for truth in truths:
        if truth in prediction.get("predictions_1", ""):
            pred_1 = truth
        if truth in prediction.get("predictions_2", ""):
            pred_2 = truth

    return pred_1, pred_2


def llama3_convert_predictions(prediction):
    """
    Extracts predictions from Llama3 model output.
    """
    truths = [prediction["ground_truth_1"], prediction["ground_truth_2"]]
    pred_1, pred_2 = "", ""

    for truth in truths:
        if truth in prediction.get("predictions_1", ""):
            pred_1 = truth
        if truth in prediction.get("predictions_2", ""):
            pred_2 = truth

    return pred_1, pred_2


def qwen_convert_predictions(prediction):
    """
    Extracts predictions from Qwen model output.
    """
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

    print(f"\nAccuracy:        {accuracy:.3f}")
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
    print(f"\n✓ Results saved to: {out_result_report}")


def evaluate_single_pair(ground_truth_file, predictions_file, output_file):
    """
    Evaluates a single ground truth vs predictions pair.
    
    Args:
        ground_truth_file: Path to ground truth JSON file
        predictions_file: Path to predictions JSON file
        output_file: Path where evaluation report will be saved
    """
    print(f"\n{'='*70}")
    print(f"Ground Truth: {ground_truth_file}")
    print(f"Predictions : {predictions_file}")
    print(f"Output      : {output_file}")
    print(f"{'='*70}")

    input_data = read_json_file(ground_truth_file)
    predictions_data = read_json_file(predictions_file)

    evaluate_predictions(input_data, predictions_data, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate model predictions against ground truth data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate single prediction file
  python src/evaluation/evaluation.py \\
    --ground-truth ground_truth.json \\
    --predictions predictions.json \\
    --output report.json

  # Evaluate multiple models (batch evaluation)
  python src/evaluation/evaluation.py \\
    --batch \\
    --input-dir ./data \\
    --predictions-dir ./predictions \\
    --output-dir ./reports \\
    --models model_flan-t5-xl model_Llama-3.1-8B-Instruct

  # Batch evaluation with custom file patterns
  python src/evaluation/evaluation.py \\
    --batch \\
    --input-dir ./data \\
    --predictions-dir ./predictions \\
    --output-dir ./reports \\
    --models model_flan-t5-xl \\
    --input-file "templates_without_desc.json" \\
    --predictions-pattern "predictions_{run_id}.json" \\
    --output-pattern "report_{run_id}.json" \\
    --run-ids 1 2 3
        """
    )

    # Single evaluation mode
    single_group = parser.add_argument_group('Single Evaluation Mode')
    single_group.add_argument(
        '--ground-truth',
        type=str,
        help='Path to ground truth JSON file'
    )
    single_group.add_argument(
        '--predictions',
        type=str,
        help='Path to predictions JSON file'
    )
    single_group.add_argument(
        '--output',
        type=str,
        help='Path for output evaluation report'
    )

    # Batch evaluation mode
    batch_group = parser.add_argument_group('Batch Evaluation Mode')
    batch_group.add_argument(
        '--batch',
        action='store_true',
        help='Enable batch evaluation mode'
    )
    batch_group.add_argument(
        '--input-dir',
        type=str,
        default='.',
        help='Base directory containing ground truth JSON files'
    )
    batch_group.add_argument(
        '--predictions-dir',
        type=str,
        default='.',
        help='Base directory containing prediction JSON files'
    )
    batch_group.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Base directory where evaluation reports will be saved'
    )
    batch_group.add_argument(
        '--input-file',
        type=str,
        default='templates_without_desc.json',
        help='Input ground truth file name (default: templates_without_desc.json)'
    )
    batch_group.add_argument(
        '--predictions-pattern',
        type=str,
        default='predictions_{run_id}.json',
        help='Predictions file pattern with {run_id} placeholder'
    )
    batch_group.add_argument(
        '--output-pattern',
        type=str,
        default='report_{run_id}.json',
        help='Output report pattern with {run_id} placeholder'
    )
    batch_group.add_argument(
        '--models',
        type=str,
        nargs='+',
        default=['model_flan-t5-xl'],
        help='List of model folder names to evaluate'
    )
    batch_group.add_argument(
        '--run-ids',
        type=int,
        nargs='+',
        default=[1],
        help='List of run IDs to evaluate (default: [1])'
    )

    args = parser.parse_args()

    # Validate mode
    has_single_args = args.ground_truth and args.predictions and args.output
    
    if args.batch and has_single_args:
        parser.error("Cannot use both --batch mode and single evaluation arguments together")
    
    if not args.batch and not has_single_args:
        parser.error("Provide either --batch flag with batch arguments, or --ground-truth, --predictions, and --output for single evaluation")

    try:
        if args.batch:
            # Batch evaluation mode
            print("\n" + "="*70)
            print("BATCH EVALUATION MODE")
            print("="*70)
            print(f"Input Dir      : {args.input_dir}")
            print(f"Predictions Dir: {args.predictions_dir}")
            print(f"Output Dir     : {args.output_dir}")
            print(f"Models         : {', '.join(args.models)}")
            print(f"Run IDs        : {args.run_ids}")
            print("="*70)

            # Validate input file exists
            input_path = os.path.join(args.input_dir, args.input_file)
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Ground truth file not found: {input_path}")

            for model_folder in args.models:
                for run_id in args.run_ids:
                    print(f"\n>>> Evaluating Model: {model_folder}, Run ID: {run_id}")

                    predictions_file = args.predictions_pattern.format(run_id=run_id)
                    output_file = args.output_pattern.format(run_id=run_id)

                    predictions_path = os.path.join(
                        args.predictions_dir,
                        model_folder,
                        predictions_file
                    )
                    output_path = os.path.join(
                        args.output_dir,
                        model_folder,
                        output_file
                    )

                    if not os.path.exists(predictions_path):
                        print(f"⚠ Skipping: Predictions file not found: {predictions_path}")
                        continue

                    evaluate_single_pair(input_path, predictions_path, output_path)

            print("\n" + "="*70)
            print("✓ Batch evaluation completed!")
            print("="*70)

        else:
            # Single evaluation mode
            if not os.path.exists(args.ground_truth):
                raise FileNotFoundError(f"Ground truth file not found: {args.ground_truth}")
            if not os.path.exists(args.predictions):
                raise FileNotFoundError(f"Predictions file not found: {args.predictions}")

            evaluate_single_pair(args.ground_truth, args.predictions, args.output)

    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
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
