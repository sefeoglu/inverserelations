# Converse (Inverse) Relation Pairs from FewRel 1.0 
Evaluation of LLMs on converse relations
Dataset is available on [🤗](https://huggingface.co/datasets/Sefika/FewRel_Converse_Relations)
Evaluated Relations are follows:

* Child <-> Mother

* Child <-> Father

* Follows <-> Followed_by

* Has Part <-> Part of

# Supported Models

| #  | Model          | Status | Head-to-Tail (No Desc) | Tail-to-Head (No Desc) | Head-to-Tail (With Desc) | Tail-to-Head (With Desc) |
|----|----------------|--------|------------------------|------------------------|--------------------------|--------------------------|
| 1  | GPT-3.5        | ✔️     |    14.58%              |       30.23%           |    44.43%                |    49.07%                |
| 2  | Gemini Flash   | ✔️     |    39.34%              |       20.82%           |    39.81%                |    22.32%                |
| 3  | Owen 2.5       | ✔️     |                        |                        |                          |                          |
| 4  | Llama 3.1      | ✔️     |                        |                        |                          |                          |
| 5  | Mistral v3     | ✔️     |    36.64%              |       39.11%           |    32.31%                |    37.02%                |
| 6  | Flan-T5        | ✔️     |    39.16%              |       60.54%           |    41.08%                |    62.42%                |

