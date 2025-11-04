This project's paper is planned to submit for Web Conf. 2026

## Converse (Inverse) Relation Pairs from FewRel 1.0 

Evaluation of LLMs on inverse relations.

 Dataset is available on [🤗](https://huggingface.co/datasets/Sefika/FewRel_Converse_Relations)

 Evaluated Relations are follows:

* Child <-> Mother

* Child <-> Father

* Follows <-> Followed_by

* Has Part <-> Part of
## Supported Approaches

* Multiple Choice Question w/o Relation Type Description from Wikidata
  
* RAG: with triples of entities (from Wikidata) w/o Relation Type Description from Wikidata
  
* CoT
  
## Supported Models
| **Model**                | **Without Desc**<br>Head→Tail | **Without Desc**<br>Tail→Head | **With Relation Desc**<br>Head→Tail | **With Relation Desc**<br>Tail→Head | **With Relation + Entity Desc**<br>Head→Tail | **With Relation + Entity Desc**<br>Tail→Head |
| ------------------------ | ----------------------------- | ----------------------------- | ----------------------------------- | ----------------------------------- | -------------------------------------------- | -------------------------------------------- |
| GPT-3.5 Turbo            | 14.58%                        | 30.23%                        | 44.43%                              | 49.07%                              | 45.84%                                       | 48.72%                                       |
| Gemini 2.5 Flash-Lite    | 39.34%                        | 20.82%                        | 39.81%                              | 22.32%                              | 43.10%                                       | 24.99%                                       |
| Qwen2.5-1.5B-Instruct    | 23.76%                        | 43.99%                        | 25.67%                              | 50.34%                              | 29.11%                                       | 52.98%                                       |
| Llama-3.1-8B-Instruct    | 32.90%                        | 42.99%                        | 32.17%                              | 56.87%                              | 46.66%                                       | 53.07%                                       |
| Mistral-7B-Instruct-v0.3 | 36.64%                        | 39.11%                        | 32.31%                              | 37.02%                              | 34.37%                                       | 57.13%                                       |
| Flan-T5 XL               | 39.16%                        | 60.54%                        | 41.08%                              | 62.42%                              | 42.16%                                       | 61.60%                                       |


