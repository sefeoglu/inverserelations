import openai
import tiktoken

import logging
import os
import sys
import json
import argparse
import logging
from tqdm import tqdm
PACKAGE_PARENT = '.'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
# sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PREFIX_PATH = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-3])
sys.path.append(PREFIX_PATH)


# logging.basicConfig(level=logging.INFO, filename=f"{PREFIX_PATH}/logging/contextual_information.log", format='%(asctime)s - %(levelname)s - %(message)s')



def run_gpt_chat(config):
    """
    Runs a GPT chat request safely, handling long inputs by chunking them.
    Returns a list of lines from the combined response.
    """
    user_query = config['user_query']
    API_KEY = config['openai_api_key']
    model = config.get('model', 'gpt-3.5-turbo')

    openai.api_key = API_KEY

    response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": user_query}],
            temperature=0,
            seed=42
    )

    text = response['choices'][0]['message']['content'].strip()
    

    # Combine all results
    
    return text

def prediction_gpt(input_data, config, out_path):
    all_predictions = []
    for idx, item in tqdm(enumerate(input_data), total=len(input_data), desc="Processing items with GPT"):
        template_1 = item['template_1']
        template_2 = item['template_2']
        item['predictions_1'] = run_gpt_chat({'user_query': template_1, 'openai_api_key': config['openai_api_key'], 'model': config['model']})
        item['predictions_2'] = run_gpt_chat({'user_query': template_2, 'openai_api_key': config['openai_api_key'], 'model': config['model']})
        all_predictions.append(item)

        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(all_predictions, f, indent=4)

    return all_predictions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine contextual information from multiple sources.")
    parser.add_argument("--input_file", type=str, default="./templates_with_desc.json", help="Path to the input JSON file containing contextual information.")
    parser.add_argument("--output_file", type=str, default="./results/gpt/gpt_with_desc.json", help="Path to the output JSON file to save combined information.")
    parser.add_argument("--config", type=str, default="./data/gpt_key.json", help="Path to the config JSON file.")

    args = parser.parse_args()
    config = json.load(open(args.config, 'r'))

    input_data = json.load(open(args.input_file, 'r'))  # Adjust slicing as needed
    out_path = args.output_file
    predictions = prediction_gpt(input_data, config, out_path)
    print(f"Predictions saved to {out_path}")