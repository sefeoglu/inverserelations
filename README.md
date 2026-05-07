## Inverse Relation Pairs from FewRel 1.0 
This project's paper is to be submitted for possible publication
Evaluation of LLMs on inverse relations.

<p align="center">
  <img src="https://github.com/sefeoglu/inverserelations/blob/master/fig/example.png" width="400"/>
</p>

 Dataset is available on [🤗](https://huggingface.co/datasets/Sefika/FewRel_Converse_Relations)

| Relation Pair               |
|-----------------------------|
| Child ↔ Mother              |
| Child ↔ Father              |
| Follows ↔ Followed_by       |
| Has Part ↔ Part of          |

## Supported Approaches

* Multiple Choice Question w/o Relation Type Description.
In addition to this, we examine if the models are familiar with entity representations.

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

```bash
cd inverserelations/llms
```
* Synthetic data generations

* Predictions
```
python artificial_entity_generation.py \
    
python llm.py \
  --input_file ./input_file_name.json \
  --output_file ./out_filename.json \
  --model_name google/flan-t5-xl

```


