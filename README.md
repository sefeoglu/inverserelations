## Inverse Relation Pairs from FewRel 1.0 
This project's paper is to be submitted for possible publication
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



## Folders
```bash
.
├── LICENSE
├── README.md
├── data
│   ├── ablation-tekgen
│   └── mqa
│       ├── fewrel
│       └── tekgen
├── fig
├── notebooks
└── src
    ├── analysis
    ├── data_preparation
    ├── evaluation
    ├── llms
    ├── notebooks
    ├── question_generation
    ├── report
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

