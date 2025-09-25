
from random import shuffle
import os
import sys
import json
from sklearn.metrics import  accuracy_score
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
def clean_text(text):
    text = text.strip().split(':')[0]
    text = text.strip().split('.')[1].split('(')[-1]
    return text.strip()
def gemini_convert_predictions(prediction):
    # print(prediction)
    
    gt_dict = {'A': prediction['ground_truth_1'], 'B': prediction['ground_truth_2'], 'C':''}
    print(gt_dict)
     
    return gt_dict

def mistral_convert_predictions(prediction):
    # print(prediction)
    truths = [prediction['ground_truth_1'], prediction['ground_truth_2']]
    # print(prediction['predictions_1'][0])
    pred_1, pred_2 = '', ''
    for truth in truths:
        if truth in prediction['predictions_1'][0][0].split('\n')[0]:
            pred_1 = truth
        if truth in prediction['predictions_2'][0][0].split('\n')[0]:
            pred_2 = truth
    print(pred_1, pred_2)
    return pred_1, pred_2

def evaluate_predictions(data, out_result_report, model_name="gpt-3.5-turbo"):
    if model_name == 'gemini':
        predictions_head_to_tail = [ gemini_convert_predictions(item)[item['predictions_1'][0][0]] for item in data]
        predictions_tail_to_head = [ gemini_convert_predictions(item)[item['predictions_2'][0][0]] for item in data]
    elif model_name == 'gpt-3.5-turbo' or model_name == 'gpt-4':
        predictions_head_to_tail = [ clean_text(item['predictions_1'][0]) for item in data]
        predictions_tail_to_head = [ clean_text(item['predictions_2'][0]) for item in data]
    elif model_name == 'mistral':
        predictions = [ (mistral_convert_predictions(item)) for item in data]
        # print( predictions)
        predictions_head_to_tail = [ item[0] for item in predictions]
        predictions_tail_to_head = [ item[1] for item in predictions]
    
    gt_head_to_tail = [ item['ground_truth_1'] for item in data]
    gt_tail_to_head = [ item['ground_truth_2'] for item in data]
    # print((predictions_head_to_tail))
    # print(len(gt_head_to_tail))
    accuracy_head_to_tail = accuracy_score(gt_head_to_tail, predictions_head_to_tail)
    accuracy_tail_to_head = accuracy_score(gt_tail_to_head, predictions_tail_to_head)
    print(f"Accuracy Head to Tail: {accuracy_head_to_tail}")
    print(f"Accuracy Tail to Head: {accuracy_tail_to_head}")
    results = {
        "accuracy_head_to_tail": accuracy_head_to_tail,
        "accuracy_tail_to_head": accuracy_tail_to_head,
        'predictions_head_to_tail': predictions_head_to_tail,
        'predictions_tail_to_head': predictions_tail_to_head,
        'gt_head_to_tail': gt_head_to_tail,
        'gt_tail_to_head': gt_tail_to_head
    }

    write_json_file(results, out_result_report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate model predictions against ground truth.")

    parser.add_argument("--predictions_file", type=str, default="/Users/sefika/phd_projects/converse_relations/results/mistral/output_mistral_v3_with_desc.json", help="Path to the JSON file containing model predictions.")
    parser.add_argument("--out_result_report", type=str, default="/Users/sefika/phd_projects/converse_relations/results/mistral/report_mistral_v3_with_desc.json", help="Path to the JSON file containing evaluation results.")
    
    args = parser.parse_args()
    predictions_data = []
    predictions_file = args.predictions_file
    predictions_data.extend( read_json_file(predictions_file))
    # for i in range(1, 5):
    #     predictions_file = f"/Users/sefika/phd_projects/converse_relations/data/experiment_1/gpt_predictions_with_desc_{i}.json"
    #     predictions_data.extend( read_json_file(predictions_file))

    out_result_report = args.out_result_report

    evaluate_predictions(predictions_data, out_result_report, model_name="mistral")