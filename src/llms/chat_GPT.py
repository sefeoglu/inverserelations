import openai
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
    # print(config)
    user_query = config['user_query']
   
    API_KEY = config['openai_api_key']
    model = config['model']

    openai.api_key = API_KEY

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": user_query}
        ],
        temperature=0,          # Makes output deterministic
        seed=42                 # Ensures repeatability across runs
    )

    return response['choices'][0]['message']['content'].split('\n')



def prediction_gpt(input_data, config, out_path):
    all_predictions = []
    for idx, item in tqdm(enumerate(input_data), total=len(input_data), desc="Processing items with GPT"):
        template_1 = item['template_1']
        template_2 = item['template_2']
        item['predictions_1'] = run_gpt_chat({'user_query': template_1, 'openai_api_key': config['openai_api_key'], 'model': config['model']})
        item['predictions_2'] = run_gpt_chat({'user_query': template_2, 'openai_api_key': config['openai_api_key'], 'model': config['model']})
        all_predictions.append(item)

        with open(out_path, 'w') as f:
            json.dump(all_predictions, f, indent=4)

    return all_predictions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine contextual information from multiple sources.")
    parser.add_argument("--input_file", type=str, default="/Users/sefika/phd_projects/converse_relations/data/experiment_2/templates_without_desc.json", help="Path to the input JSON file containing contextual information.")
    parser.add_argument("--output_file", type=str, default="/Users/sefika/phd_projects/converse_relations/data/experiment_2/gpt_predictions_without_desc_4.json", help="Path to the output JSON file to save combined information.")
    parser.add_argument("--config", type=str, default="/Users/sefika/phd_projects/converse_relations/data/gpt_key.json", help="Path to the config JSON file.")
    
    args = parser.parse_args()
    config = json.load(open(args.config, 'r'))
    input_data = json.load(open(args.input_file, 'r'))[2084:]
    out_path = args.output_file
    predictions = prediction_gpt(input_data, config, out_path)
    print(f"Predictions saved to {out_path}")