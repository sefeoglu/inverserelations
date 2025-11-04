"""Generates responses for prompts using a language model defined in Hugging Face."""
"""Created by: Sefika"""
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM, T5Tokenizer, T5ForConditionalGeneration
import json
import os
from tqdm import tqdm


def read_json(path):
    with open(path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data

def write_json(data, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class LLM(object):

    def __init__(self, model_id="google/flan-t5-xl"):
        """
        Initialize the LLM model
        Args:
            model_id (str, optional): model name from Hugging Face. Defaults to "google/flan-t5-xl".
        """

        if model_id=="google/flan-t5-xl":
            self.model, self.tokenizer = self.get_model(model_id)
        else:
            self.model, self.tokenizer = self.get_model_decoder(model_id)


    def get_model(self, model_id="google/flan-t5-xl"):
        """_summary_

        Args:
            model_id (str, optional): LLM name at HuggingFace . Defaults to "google/flan-t5-xl".

        Returns:
            model: model from Hugging Face
            tokenizer: tokenizer of this model
        """
        tokenizer = T5Tokenizer.from_pretrained(model_id)

        model = T5ForConditionalGeneration.from_pretrained(model_id,
                                                    device_map="auto",
                                                    load_in_8bit=False,
                                                    torch_dtype=torch.float16
                                                           )
        return model,tokenizer

    def get_prediction(self, prompt, length=30):
        """_summary_

        Args:
            model : loaded model
            tokenizer: loaded tokenizer
            prompt (str): prompt to generate response
            length (int, optional): Response length. Defaults to 30.

        Returns:
            response (str): response from the model
        """
        # if "Llama" in self.model:
        #     return self.get_prediction_llama3(self.model, self.tokenizer, prompt, length)

        inputs = self.tokenizer(prompt, add_special_tokens=True, max_length=526,return_tensors="pt").input_ids.to("cuda")

        outputs = self.model.generate(inputs, max_new_tokens=length)

        response = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)

        return response



    def get_prediction_chat_prediction(
        self,
        prompt: str,
        length: int = 250,
        stype: str = "greedy",   # "greedy" | "sample" | "beam"
        temperature: float = 0.0,
        top_p: float = 0.9,
        num_beams: int = 4
    ) -> str:
        """
        Generate a response from a LLaMA-3/3.1 chat model.
        """

        # Build chat messages
        messages = [
            {"role": "system", "content": "You are a helpful chatbot and always answer the user's question. Please do not explain"},
            {"role": "user", "content": prompt},
        ]

        # ✅ apply_chat_template is a tokenizer method, not model
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        )

        # Send to model's device
        device = next(self.model.parameters()).device
        input_ids = input_ids.to(device)

        # End-of-sequence / end-of-turn ids
        eot = self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        terminators = [tid for tid in {self.tokenizer.eos_token_id, eot} if tid is not None]

        # Base generation kwargs
        gen_kwargs = {
            "max_new_tokens": length,
            "eos_token_id": terminators if len(terminators) > 1 else terminators[0],
            "pad_token_id": self.tokenizer.eos_token_id,
            "use_cache": True,
        }

        if stype.lower() == "sample":
            gen_kwargs.update(
                dict(do_sample=True, temperature=temperature, top_p=top_p)
            )
        elif stype.lower() == "beam":
            gen_kwargs.update(
                dict(do_sample=False, num_beams=num_beams, early_stopping=True)
            )
        else:  # greedy
            gen_kwargs.update(dict(do_sample=False))

        with torch.inference_mode():
            outputs = model.generate(input_ids, **gen_kwargs)

        generated = outputs[:, input_ids.shape[-1]:]
        response = tokenizer.batch_decode(generated, skip_special_tokens=True)[0].strip()

        return response



    def get_model_decoder(self, model_id="mistralai/Mistral-7B-Instruct-v0.3"):
        """loades the model from Hugging Face such llama and mistral

        Args:
            model_id (str, optional): _description_. Defaults to "meta-llama/Llama-2-7b-chat-hf".

        Returns:
            model: loaded model
            tokenizer: loaded tokenizer
        """

        tokenizer = AutoTokenizer.from_pretrained(model_id, chat_template=AutoTokenizer.from_pretrained(model_id).chat_template)
        model = AutoModelForCausalLM.from_pretrained(model_id,
                                                    device_map="balanced",
                                                    load_in_8bit=False,
                                                    torch_dtype=torch.float16)
        return model,tokenizer

def main(data, out, model_name="google/flan-t5-xl"):


      responses = []
      llm_instance = LLM(model_name)
      tokenizer = llm_instance.tokenizer
      model = llm_instance.model

      for index, item in enumerate(data):

        print(f"index: {index}")


        if model_name!="google/flan-t5-xl":
            head_to_tail = llm_instance.get_prediction_chat_prediction( item['template_1'])
            tail_to_head = llm_instance.get_prediction_chat_prediction( item['template_2'])
        else:
            head_to_tail = llm_instance.get_prediction( item['template_1'])
            tail_to_head = llm_instance.get_prediction( item['template_2'])

        item["predictions_1"] = head_to_tail
        item["predictions_2"] = tail_to_head
        responses.append(item)
        # write_json(responses, out)

      return responses

if __name__ =="__main__":
  input_file = "./templates_with_desc.json"
  out = "drive/MyDrive/webconf_rag/output_t5_xxl_rag_with_desc.json"
  model_name="google/flan-t5-xl"
  data = read_json(input_file)

  responses = main(data, out, model_name=model_name)
  write_json(responses, out)