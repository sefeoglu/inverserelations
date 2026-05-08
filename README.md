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
  <img src="https://github.com/sefeoglu/inverserelations/blob/master/fig/example.png" width="450"/>
</p>

Unlike existing benchmarks, **Reversing Arrows** explicitly evaluates:

- head-to-tail vs. tail-to-head relation interpretation,
- sentence-level inverse relation classification,
- direction-aware semantic understanding,
- and robustness under entity perturbation.

# Repository Structure
```text
.
├── LICENSE
├── README.md
├── data
│   ├── ablation-tekgen
│   └── mqa
│       ├── fewrel
│       └── tekgen
├── figure
├── notebooks
├── requirements.txt                  # Python dependencies
├── reversing_arrows_croissant.ttl    # RDF representation of the benchmark
├── src
│   ├── analysis/                     # Data analysis and visualization scripts
│   ├── data_preparation/             # Dataset construction and synthetic entity generation
│   ├── evaluation/                   # Model evaluation and metrics computation
│   ├── llms/                         # LLM prompting and response generation
│   ├── question_generation/          # Multiple-choice question generation scripts
│   │                                 # (with/without relation descriptions and
│   │                                 # mathematical variable anonymization)
│   ├── report/                       # Result visualization and report generation
│   └── utils.py                      # Utility functions for file I/O operations
```
## Usage
1. Git clone the repository and navigate to the project directory:
```bash
git clone https://github.com/sefeoglu/inverserelations.git
cd inverserelations

```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run Construction scripts to generate the dataset variants (original, synthetic, mathematical variables):
```bash
python src/data_preparation/construct_dataset.py --input_dir ./data/mqa/fewrel --output_dir ./data/mqa/fewrel/constructed
```
4. Run Question Generation scripts to create multiple-choice questions with and without relation descriptions:
```bash
python src/question_generation/generate_questions.py --input_dir ./data/mqa/fewrel/constructed --output_dir ./data/mqa/fewrel/questions
```
5. Run Evaluation scripts to evaluate model predictions against ground truth and generate reports:
```bash
python src/evaluation/evaluation.py --ground-truth ./data/mqa/fewrel/questions
```

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

# Resources

- Dataset: https://huggingface.co/datasets/Sefika/FewRel_Inverse_Relations
- Code: https://github.com/sefeoglu/inverserelations
- Experimental Results: https://zenodo.org/records/19650827

---

# Citation

```bibtex

@misc{fewrel_inverse_2025,
  author = {Sefika Efeoglu, and Adrian Paschke},
  title = { Reversing Arrows: A Benchmark Dataset for Inverse Relation Directionality in LLMs},
  year = {2026},
  publisher = {GitHub/HuggingFace},
  doi = { 10.57967/hf/8462 },
  howpublished = {https://github.com/sefeoglu/inverserelations}
}

```

---

# License

This project is released under the **MIT License**.
