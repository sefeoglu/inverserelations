import argparse


from utils import read_json_file, write_json_file




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean model predictions for evaluation.")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input JSON file containing model predictions.",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to output JSON file for cleaned predictions.",
    )
    args = parser.parse_args()
    
    input_path = args.input
    output_path = args.output
    
    data = read_json_file(input_path)
    
    cleaned_data = []
    for item in data:
        cleaned_item = {
            "id": item["id"],
            "predictions_1": item["predictions_1"][0][0],
            "predictions_2": item["predictions_2"][0][0],
            "ground_truth_1": item["ground_truth_1"],
            "ground_truth_2": item["ground_truth_2"]
        }
        cleaned_data.append(cleaned_item)
    
    write_json_file(cleaned_data, output_path)