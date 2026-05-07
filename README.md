## Reversing Arrows: A Benchmark Dataset for Inverse

### This project's paper is to be submitted for possible publication.


Reversing Arrows is a benchmark dataset for evaluating whether Large Language Models (LLMs) correctly capture the direction-dependent semantics of inverse relations in text-to-knowledge-graph and relation-classification tasks.

The dataset focuses on inverse relation pairs where reversing the subject and object changes the semantic meaning of the relation, such as:


<p align="center">
  <img src="https://github.com/sefeoglu/inverserelations/blob/master/fig/example.png" width="400"/>
</p>

 
The dataset focuses on inverse relation pairs where reversing the subject and object changes the semantic meaning of the relation, such as:

| Relation Pair               |
|-----------------------------|
| Child ↔ Mother              |
| Child ↔ Father              |
| Follows ↔ Followed_by       |
| Has Part ↔ Part of          |

Unlike general relation extraction benchmarks, Reversing Arrows explicitly evaluates:
- head-to-tail vs. tail-to-head relation interpretation,
- sentence-level inverse relation classification,
- direction-aware semantic understanding,
- and robustness under entity perturbation.

## Dataset Construction

The dataset is constructed from:
- **FewRel 1.0**
- **Wikidata**

We retrieve and verify inverse relations using Wikidata properties and directional consistency checks.

The benchmark contains:
- **3,401 instances**
- **7 relation labels**
- verified directional relation pairs

## Benchmark Variants

The dataset includes multiple evaluation settings:

### Original Entities
Uses the original entity mentions from FewRel.

### Synthetic Entities
Replaces original entities with synthetic alternatives to analyze the effects of entity familiarity.

### Mathematical Variables
Replaces entities with anonymized variables (e.g., `XXX`, `YYY`) to evaluate robustness under full anonymization.

## Evaluation Tasks

The benchmark supports:
- inverse relation classification,
- directional semantic evaluation,
- LLM robustness analysis,
- and relation-aware prompting experiments.

All evaluations are performed using zero-shot multiple-choice prompting.

## Resource Availability

- Dataset:  [🤗](https://huggingface.co/datasets/Sefika/FewRel_Converse_Relations)
- Code: GitHub
- Experimental Results: [Zenodo](https://zenodo.org/records/19650827)
- 
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


