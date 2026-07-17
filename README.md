# Reversing Arrows: A Benchmark Dataset for Inverse Relation Directionality in LLMs

[![Hugging Face Dataset](https://img.shields.io/badge/🤗%20Dataset-Hugging%20Face-yellow)](https://huggingface.co/datasets/Sefika/FewRel_Inverse_Relations)
[![DOI](https://img.shields.io/badge/DOI-10.57967%2Fhf%2F8462-blue)](https://doi.org/10.57967/hf/8462)
[![Zenodo](https://img.shields.io/badge/Zenodo-19650827-blue)](https://zenodo.org/records/19650827)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> *This work is currently under review for publication.*

**Reversing Arrows** is a benchmark dataset for evaluating whether Large Language Models (LLMs) correctly capture the **direction-dependent semantics of inverse relations** in sentence-level relation classification and text-to-knowledge graph generation tasks. 

Inverse relations are semantically sensitive because reversing the argument order changes the meaning of the relation. For example:

- `(Telephassa, mother, Phoenix)`
- `(Phoenix, child, Telephassa)`

represent inverse semantic directions.

<p align="center">
  <img src="https://github.com/sefeoglu/inverserelations/blob/master/figure/example.png" width="450"/>
</p>

Unlike existing benchmarks, **Reversing Arrows** explicitly evaluates:

- head-to-tail vs. tail-to-head relation interpretation,
- sentence-level inverse relation classification,
- direction-aware semantic understanding,
- and robustness under entity perturbation.
# Resources
| Resource             | Link                                                                                                                       | Description                                                                                                                                                                   |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dataset              | [FewRel_Inverse_Relations Dataset](https://huggingface.co/datasets/Sefika/FewRel_Inverse_Relations?utm_source=chatgpt.com) | Benchmark dataset for evaluating inverse relation directionality and entity substitution robustness in relation extraction models, derived from FewRel. ([huggingface.co][1]) |
| Code                 | [inverserelations GitHub Repository](https://github.com/sefeoglu/inverserelations?utm_source=chatgpt.com)                  | Source code and scripts for generating synthetic inverse-relation data and running experiments associated with the dataset. ([huggingface.co][1])                             |
| Experimental Results | [Zenodo Experimental Results Archive](https://zenodo.org/records/19650827?utm_source=chatgpt.com)                          | Archived experimental outputs, evaluation artifacts, and reproducibility materials associated with the benchmark.                                                             |

[1]: https://huggingface.co/datasets/Sefika/FewRel_Inverse_Relations/blob/main/README.md?utm_source=chatgpt.com "README.md · Sefika/FewRel_Inverse_Relations at main"

# Repository Structure
```text
.
├── data/                             # Dataset inputs, generated questions, and model outputs
├── figure/                           # Figures used in the paper/README
├── notebooks/                        # Exploratory notebooks
├── requirements.txt                  # Python dependencies
├── reversing_arrows_croissant.ttl    # RDF representation of the benchmark
└── src/
    ├── analysis/                     # Analysis and visualization scripts
    ├── data_preparation/             # Wikidata enrichment and synthetic entity generation
    ├── evaluation/                   # Cleaning predictions and computing metrics
    ├── llms/                         # Hugging Face inference script
    ├── question_generation/          # Prompt/template generation
    ├── report/                       # Report generation helpers
    └── utils.py                      # Shared JSON/Turtle file utilities
```

## Getting Started

Clone the repository and install the dependencies:

```bash
git clone https://github.com/sefeoglu/inverserelations.git
cd inverserelations
python -m pip install -r requirements.txt
```

All scripts in `src/` are intended to be run from the repository root with commands of the form `python src/...`.

## Typical Workflow

The repository is organized as a small pipeline: prepare data, generate question templates, run a model, and evaluate the predictions.

### 1. Enrich FewRel data with Wikidata relations

Use `src/data_preparation/construct_dataset.py` to load train/validation JSON files, attach relation metadata, and query Wikidata.

```bash
python src/data_preparation/construct_dataset.py \
  --train-data /path/to/train_wiki.json \
  --val-data /path/to/val_wiki.json \
  --relations /path/to/pid2name_fewrel.json \
  --output-dir ./data/mqa/fewrel/constructed
```

This produces annotated train/validation JSON files in the output directory. The required train/validation inputs are not committed to the repository, so point the script at your local FewRel/Wikidata JSON files.

### 2. Optionally create synthetic entities

If you want entity-perturbed variants, run:

```bash
python src/data_preparation/artificial_entity_generation.py \
  --input ./data/mqa/fewrel/constructed/val_fewrel.json \
  --output ./data/mqa/fewrel/constructed/val_fewrel_artificial.json
```

### 3. Generate multiple-choice question templates

Use `src/question_generation/template.py` to create prompt files. The `--output` path is a base name; the script writes both `*_with_desc.json` and `*_without_desc.json`.

```bash
python src/question_generation/template.py \
  --mode fewrel \
  --data /path/to/annotated_fewrel.json \
  --relations /path/to/pid2name_fewrel.json \
  --output ./data/mqa/fewrel/questions/val_templates.json
```

Other supported modes:

- `--mode ai` for artificial/synthetic entities
- `--mode mt` for mathematical-variable anonymization (`XXXX`/`YYYY`)

### 4. Run an LLM over the generated templates

`src/llms/llm.py` reads a template file and writes model predictions.

```bash
python src/llms/llm.py \
  --input_file ./data/mqa/fewrel/questions/val_templates_with_desc.json \
  --output_file ./data/mqa/fewrel/predictions/flan_t5_with_desc.json \
  --model_name google/flan-t5-xl
```

### 5. Optionally normalize prediction output

Some model outputs may need to be flattened before evaluation:

```bash
python src/evaluation/clean_answer.py \
  --input ./data/mqa/fewrel/predictions/raw_predictions.json \
  --output ./data/mqa/fewrel/predictions/clean_predictions.json
```

### 6. Evaluate predictions

Evaluate a single predictions file:

```bash
python src/evaluation/evaluation.py \
  --ground-truth ./data/mqa/fewrel/questions/val_templates_with_desc.json \
  --predictions ./data/mqa/fewrel/predictions/clean_predictions.json \
  --output ./data/mqa/fewrel/reports/flan_t5_with_desc.json
```

For larger experiments, `src/evaluation/evaluation.py --batch` can evaluate multiple model/run combinations and write one report per run.

The benchmark contains the following inverse relation pairs derived from FewRel and Wikidata: 

| Relation | Inverse Relation | Wikidata PIDs |
|---|---|---|
| Child | Mother (Parent) | P40 ↔ P25 |
| Child | Father (Parent) | P40 ↔ P22 |
| Follows | Followed by | P155 ↔ P156 |
| Has part | Part of | P527 ↔ P361 |

---

# Dataset Construction

The dataset is constructed from:

- **FewRel 1.0**
- **Wikidata** 

The construction process consists of:

1. Selecting candidate inverse relation pairs,
2. Extracting head-tail entity pairs,
3. Querying Wikidata properties,
4. Filtering inverse property pairs,
5. Assigning directional labels:
   - head-to-tail,
   - tail-to-head.

The benchmark contains:

| Property | Value |
|---|---|
| Total Instances | 3,401 |
| Relation Labels | 7 |
| Evaluation Setup | Zero-shot MCQ |
| Source Dataset | FewRel 1.0 |
| Knowledge Base | Wikidata |


---

# Benchmark Variants

To analyze robustness and entity familiarity effects, the benchmark includes multiple variants. 

## 1. Original Entities

Uses the original entity mentions from FewRel.

### Example (Head → Tail)

```text
What is the relation from Aage to Niels Bohr in the sentence?

Sentence:
Niels Bohr and his son Aage, a physicist who acted as his father's assistant,
arrived on 30 December on the first of several visits as a consultant.

A.) child
B.) father
C.) None of the above
```

Correct Answer:

```text
child
```

---

## 2. Synthetic Entities

Original entities are replaced with synthetic alternatives using Presidio Anonymizer to evaluate sensitivity to familiar entities.

### Example

```text
What is the relation from Aage to Devin Rodriguez in the sentence?

Sentence:
Devin Rodriguez and his son Aage, a physicist who acted as his father's assistant,
arrived on 30 December on the first of several visits as a consultant.

A.) child
B.) father
C.) None of the above
```

Correct Answer:

```text
child
```

---

## 3. Mathematical Variables

Entities are fully anonymized using mathematical variables such as `XXX` and `YYY`.

### Example

```text
What is the relation from XXX to YYY in the sentence?

Sentence:
YYY and his son XXX, a physicist who acted as his father's assistant,
arrived on 30 December on the first of several visits as a consultant.

A.) child
B.) father
C.) None of the above
```

Correct Answer:

```text
child
```


---

# Prompting Strategies

The benchmark evaluates zero-shot multiple-choice prompting under two settings:

- **Without relation descriptions**
- **With relation descriptions** 

Each question contains:

- A.) head-to-tail relation
- B.) tail-to-head relation
- C.) none of the above


---

# Evaluation

The benchmark evaluates:

- inverse relation classification,
- directional semantic understanding,
- robustness to entity perturbation,
- and entity familiarity effects.

All experiments are conducted using:

- zero-shot prompting,
- multiple-choice question formats,
- micro-F1 evaluation. 

The paper evaluates five open-source LLMs:

- Flan-T5 XL
- Llama-3.1-8B-Instruct
- Qwen2.5-7B-Instruct
- Qwen3-4B-Instruct
- Mistral-7B-Instruct-v0.3

---



# Citation

```bibtex

@misc{fewrel_inverse_2026,
  author = {Sefika Efeoglu, and Adrian Paschke},
  title = {Reversing Arrows: A Benchmark Dataset for Inverse Relation Directionality in LLMs},
  year = {2026}
}

```

---

# License

This project is released under the **MIT License**.
