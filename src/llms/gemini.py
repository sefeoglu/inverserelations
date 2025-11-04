from http import client
from google import genai
import json
import os
import argparse
from tqdm import tqdm
import time
def generate_text_with_gemini(question, config):
    """
    Gemini 2.5 Pro modelini kullanarak basit bir metin oluşturma örneği.
    """

    client = genai.Client(api_key=config["gemini_api_key"])

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=question +"Please only answer with A, B, or C."
    )
    return response.text


def bulk_test(templates, out_file, config):
    results = []
    for item in tqdm(templates, desc="Processing templates"):
       
        template_1 = item['template_1']
        template_2 = item['template_2']

        prediction_1 = generate_text_with_gemini(template_1, config)
        prediction_2 = generate_text_with_gemini(template_2, config)

        item['predictions_1'] = prediction_1.split('\n')
        item['predictions_2'] = prediction_2.split('\n')

        results.append(item)

        with open(out_file, 'w') as f:
            json.dump(results, f, indent=4)
        time.sleep(1)  # API rate limitine dikkat etmek için kısa bir bekleme ekleyin


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine contextual information from multiple sources.")
    parser.add_argument("--input_file", type=str, default="./templates_with_desc.json", help="Path to the input JSON file containing contextual information.")
    parser.add_argument("--output_file", type=str, default="./results/gemini/gemini_rag_predictions_with_desc.json", help="Path to the output JSON file to save combined information.")
    parser.add_argument("--config", type=str, default="./data/gemini_key.json", help="Path to the config JSON file.")

    args = parser.parse_args()
    input_data = json.load(open(args.input_file, 'r'))
    out_path = args.output_file
    config_path = args.config 
    config = json.load(open(config_path, 'r'))
    bulk_test(input_data, out_path, config)
    print(f"Predictions saved to {out_path}")
