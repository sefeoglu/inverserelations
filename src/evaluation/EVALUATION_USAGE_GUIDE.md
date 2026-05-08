# Evaluation Script

## Overview
This script evaluates model predictions against ground truth data with comprehensive metrics including accuracy, precision, recall, F1-score, and per-class statistics. Supports both single and batch evaluation modes.

## Installation
Requires scikit-learn:
```bash
pip install scikit-learn
```

## Basic Usage

### Single Evaluation Mode
```bash
python evaluation_script.py \
  --ground-truth ground_truth.json \
  --predictions predictions.json \
  --output report.json
```

### Batch Evaluation Mode
```bash
python evaluation_script.py \
  --batch \
  --input-dir ./data \
  --predictions-dir ./predictions \
  --output-dir ./reports \
  --models model_flan-t5-xl model_Llama-3.1-8B-Instruct
```

## Arguments

### Single Evaluation Mode (Mutually exclusive with --batch)

#### Required
- `--ground-truth` : Path to ground truth JSON file
- `--predictions` : Path to predictions JSON file
- `--output` : Path for output evaluation report

### Batch Evaluation Mode (Use with --batch flag)

#### Required
- `--batch` : Enable batch evaluation mode (flag)

#### Optional (Batch Mode)
- `--input-dir` : Base directory containing ground truth files (default: .)
- `--predictions-dir` : Base directory containing prediction files (default: .)
- `--output-dir` : Base directory where reports will be saved (default: .)
- `--input-file` : Ground truth filename (default: templates_without_desc.json)
- `--predictions-pattern` : Predictions file pattern with {run_id} placeholder
  - Default: `predictions_{run_id}.json`
- `--output-pattern` : Output report pattern with {run_id} placeholder
  - Default: `report_{run_id}.json`
- `--models` : List of model folder names to evaluate (default: model_flan-t5-xl)
- `--run-ids` : List of run IDs to evaluate (default: 1)

## Examples

### 1. Single File Evaluation
```bash
python evaluation_script.py \
  --ground-truth ./data/templates.json \
  --predictions ./results/predictions.json \
  --output ./results/evaluation_report.json
```

### 2. Batch Evaluation - Single Model, Multiple Runs
```bash
python evaluation_script.py \
  --batch \
  --input-dir ./data \
  --predictions-dir ./predictions/model_flan-t5-xl \
  --output-dir ./reports/model_flan-t5-xl \
  --input-file original_templates_without_desc.json \
  --run-ids 1 2 3 4 5
```

### 3. Batch Evaluation - Multiple Models, Multiple Runs
```bash
python evaluation_script.py \
  --batch \
  --input-dir ./data \
  --predictions-dir ./predictions \
  --output-dir ./reports \
  --input-file templates_without_desc.json \
  --models model_flan-t5-xl model_Llama-3.1-8B-Instruct model_Qwen2.5-7B-Instruct \
  --run-ids 1 2 3
```

### 4. Custom File Patterns (Batch Mode)
```bash
python evaluation_script.py \
  --batch \
  --input-dir ./data/ground_truth \
  --predictions-dir ./data/predictions \
  --output-dir ./data/reports \
  --input-file ground_truth_inv.json \
  --predictions-pattern tail_head_predictions_{run_id}.json \
  --output-pattern tail_head_report_{run_id}.json \
  --models model_llama model_qwen \
  --run-ids 1 2
```

### 5. Original Use Case (Adapted)
```bash
# For the original nested directory structure
python evaluation_script.py \
  --batch \
  --input-dir /path/to/data/mqa/fewrel \
  --predictions-dir /path/to/results/fewrel/original \
  --output-dir /path/to/results/fewrel/original/report_class \
  --input-file original_templates_without_desc.json \
  --models model_flan-t5-xl model_Llama-3.1-8B-Instruct model_Qwen2.5-7B-Instruct model_Qwen3-4B-Instruct-2507 model_Mistral-7B-Instruct-v0.3 \
  --run-ids 1
```

## Output Structure

### Evaluation Report (JSON)
```json
{
  "accuracy": 0.85,
  "macro_precision": 0.82,
  "macro_recall": 0.80,
  "macro_f1": 0.81,
  "micro_precision": 0.85,
  "micro_recall": 0.85,
  "micro_f1": 0.85,
  "labels": ["relation_1", "relation_2", ...],
  "per_class_precision": [0.90, 0.75, ...],
  "per_class_recall": [0.85, 0.78, ...],
  "per_class_f1": [0.87, 0.76, ...],
  "support": [100, 120, ...],
  "per_class": {
    "relation_1": {
      "precision": 0.90,
      "recall": 0.85,
      "f1": 0.87,
      "support": 100
    },
    ...
  }
}
```

## Input Data Requirements

### Ground Truth JSON Structure
Each item should have:
```json
{
  "template_1": "Question about relation...",
  "ground_truth_1": "relation_name",
  "template_2": "Question about inverse relation...",
  "ground_truth_2": "inverse_relation_name",
  "relation": "relation_label",
  ...other fields...
}
```

### Predictions JSON Structure
Each item should have:
```json
{
  "response": "A",  // or "B", "C" - the model's answer
  "relation": "relation_name",  // for validation
  ...other fields...
}
```

## Metrics Explained

### Overall Metrics
- **Accuracy**: Proportion of correct predictions
- **Macro Precision/Recall/F1**: Average across all classes (unweighted)
- **Micro Precision/Recall/F1**: Average calculated globally across all samples

### Per-Class Metrics
- **Precision**: TP / (TP + FP) - Correctness of positive predictions
- **Recall**: TP / (TP + FN) - Coverage of positive cases
- **F1-Score**: Harmonic mean of precision and recall
- **Support**: Number of samples for that class

## Console Output

The script provides:
- Per-class metrics printed to console
- Overall accuracy, precision, recall, F1 scores
- JSON report saved to specified output file
- Status messages for batch processing

## Error Handling

Handles gracefully:
- ✓ Missing input files
- ✓ Invalid JSON format
- ✓ Length mismatches between ground truth and predictions
- ✓ Missing keys in data
- ✓ File I/O errors

## Features

1. **Two Evaluation Modes**: Single file or batch processing
2. **Flexible File Patterns**: Use placeholders like {run_id} for dynamic paths
3. **Multiple Models**: Evaluate many models in one command
4. **Batch Run IDs**: Test multiple runs per model
5. **Auto Directory Creation**: Creates output directories automatically
6. **Comprehensive Metrics**: Accuracy, precision, recall, F1 at macro/micro/per-class level
7. **Detailed Reports**: Saves complete evaluation results as JSON
8. **Console Feedback**: Real-time status updates and metrics

## Help

```bash
python evaluation.py --help
```
