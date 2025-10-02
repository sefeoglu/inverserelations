This project's paper is planned to submit for Web Conf. 2026

## Converse (Inverse) Relation Pairs from FewRel 1.0 
Evaluation of LLMs on converse relations
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

| #  | Model          | Status | h-to-t (No Desc) | t-to-h (No Desc) | h-to-t (With Desc) | t-to-h (With Desc) |RAG (h-to-t)|RAG (t-to-h)|CoT (h-to-t)|CoT (t-to-h)|
|----|----------------|--------|------------------|------------------|--------------------|--------------------|------------|------------|------------|------------|
| 1  | GPT-3.5        | ✔️     |    14.58%        |       30.23%     |    44.43%          |    49.07%          |            |            |            |            |
| 2  | Gemini Flash   | ✔️     |    39.34%        |       20.82%     |    39.81%          |    22.32%          |            |            |            |            |
| 3  | Owen 2.5       | ✔️     |                  |                  |                    |                    |            |            |            |            |
| 4  | Llama 3.1      | ✔️     |                  |                  |                    |                    |            |            |            |            |
| 5  | Mistral v3     | ✔️     |    36.64%        |       39.11%     |    32.31%          |    37.02%          |            |            |            |            |
| 6  | Flan-T5        | ✔️     |    39.16%        |       60.54%     |    41.08%          |    62.42%          |            |            |            |            |

