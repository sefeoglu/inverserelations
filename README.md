## Inverse Relation Pairs from FewRel 1.0 
This project's paper is to submit for KR'2026
Evaluation of LLMs on inverse relations.

<p align="center">
  <img src="https://github.com/sefeoglu/inverserelations/blob/master/fig/example.png" width="400"/>
</p>


 Dataset is available on [🤗](https://huggingface.co/datasets/Sefika/FewRel_Converse_Relations)
 Flan-T5 distributions: [here](https://github.com/sefeoglu/inverserelations/blob/master/src/notebooks/converse_relations.ipynb)

| Relation Pair               |
|-----------------------------|
| Child ↔ Mother              |
| Child ↔ Father              |
| Follows ↔ Followed_by       |
| Has Part ↔ Part of          |

## Supported Approaches

* Multiple Choice Question w/o Relation Type Description, and Rel. and Entity Descs. from Wikidata

## Supported Models
Visualization

![image](https://github.com/sefeoglu/inverserelations/blob/master/fig/desc_acc_viz.png)

| **Model**                | **Without Desc**<br>Head→Tail | **Without Desc**<br>Tail→Head | **With Relation Desc**<br>Head→Tail | **With Relation Desc**<br>Tail→Head | **With Relation + Entity Desc**<br>Head→Tail | **With Relation + Entity Desc**<br>Tail→Head |
| ------------------------ | ----------------------------- | ----------------------------- | ----------------------------------- | ----------------------------------- | -------------------------------------------- | -------------------------------------------- |
| GPT-3.5 Turbo            | 14.58%                        | 30.23%                        | 44.43%                              | 49.07%                              | 45.84%                                       | 48.72%                                       |
| Gemini 2.5 Flash-Lite    | 39.34%                        | 20.82%                        | 39.81%                              | 22.32%                              | 43.10%                                       | 24.99%                                       |
| Qwen2.5-7B-Instruct    | 23.76%                        | 43.99%                        | 25.67%                              | 50.34%                              | 29.11%                                       | 52.98%                                       |
| Llama-3.1-8B-Instruct    | 32.90%                        | 42.99%                        | 32.17%                              | 56.87%                              | 46.66%                                       | 53.07%                                       |
| Mistral-7B-Instruct-v0.3 | 36.64%                        | 39.11%                        | 32.31%                              | 37.02%                              | 34.37%                                       | 57.13%                                       |
| Flan-T5 XL               | 39.16%                        | 60.54%                        | 41.08%                              | 62.42%                              | 42.16%                                       | 61.60%                                       |


## Folders
```bash
.
├── LICENSE
├── README.md
├── data
├── fig
├── results
│   ├── gemini
│   ├── gpt
│   ├── llama3
│   ├── mistral
│   ├── qwen
│   └──  t5
└── src
    ├── analysis
    ├── data_preparation
    ├── evaluation
    ├── llms
    ├── notebooks
    ├── question_generation
    └── utils.py
```

## Usage:
* For open sources
```bash
cd  converse_relations/llms
python llm.py \
  --input_file ./templates_with_desc.json \
  --output_file ./output_t5_xxl_rag_with_desc.json \
  --model_name google/flan-t5-xl

```
Chat GPT
```bash
cd  converse_relations/llms
python chat_GPT.py \
  --input_file ./templates_with_desc.json \
  --output_file ./gpt_with_desc.json \
  --config ./gpt_key.json
```
Gemini
```bash
cd  converse_relations/llms
python gemini.py \
  --input_file ./templates_with_desc.json \
  --output_file ./gpt_with_desc.json \
  --config ./gemini_keys.json
```

