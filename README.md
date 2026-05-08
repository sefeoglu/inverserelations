# Reversing Arrows: A Benchmark Dataset for Inverse Relation Directionality in LLMs

[![Hugging Face Dataset](https://img.shields.io/badge/🤗%20Dataset-Hugging%20Face-yellow)](https://huggingface.co/datasets/Sefika/FewRel_Converse_Relations)
[![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.19650827.svg)](https://zenodo.org/records/19650827)
[![DOI](https://img.shields.io/badge/DOI-10.57967%2Fhf%2F8462-blue)](https://doi.org/10.57967/hf/8462)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> *This work is currently under review for publication.*

**Reversing Arrows** is a benchmark dataset designed to evaluate whether Large Language Models (LLMs) correctly understand the **direction-dependent semantics of inverse relations** in relation classification and text-to-knowledge-graph tasks.

Many semantic relations are inherently directional: reversing the subject and object changes the meaning of the relation entirely. For example, while:

> *Alice is the child of Bob*

represents a **Child → Parent** relation, reversing the entities produces a semantically different relation:

> *Bob is the parent of Alice*

<p align="center">
  <img src="https://github.com/sefeoglu/inverserelations/blob/master/fig/example.png" width="450"/>
</p>

---

## Motivation

Recent LLMs achieve strong performance on relation extraction and knowledge graph reasoning benchmarks. However, existing datasets rarely evaluate whether models truly capture the **directionality** of semantic relations.

**Reversing Arrows** was created to systematically measure:

- directional semantic understanding,
- inverse relation reasoning,
- robustness to entity perturbation,
- structure-sensitive relation classification.

---

## Relation Types

| Relation Pair |
|---|
| Child ↔ Mother |
| Child ↔ Father |
| Follows ↔ Followed_by |
| Has Part ↔ Part Of |
| Employer ↔ Employee |
| Owned By ↔ Owns |
| Located In ↔ Contains |

---

## Dataset Construction

The dataset is constructed using:

- **FewRel 1.0**
- **Wikidata**

Inverse relation pairs are retrieved and validated through:

- Wikidata property mappings,
- inverse-property verification,
- directional consistency checks.

---

## Dataset Statistics

| Property | Value |
|---|---|
| Total Instances | 3,401 |
| Relation Categories | 7 |
| Source Dataset | FewRel 1.0 |
| Knowledge Base | Wikidata |
| Evaluation Format | Multiple Choice |
| Prompting Setup | Zero-shot |

---

## Benchmark Variants

### Original Entities

Uses the original entity mentions from FewRel.

```text
Barack Obama was born in Honolulu.
```

### Synthetic Entities

Replaces original entities with synthetic alternatives to reduce memorization effects.

```text
Arven Malis was born in Tarevia.
```

### Mathematical Variables

Replaces entities with anonymized placeholders such as `XXX` and `YYY`.

```text
XXX was born in YYY.
```

---

## Evaluation Tasks

The benchmark supports experiments on:

- inverse relation classification,
- directional semantic understanding,
- relation-aware prompting,
- robustness under entity anonymization,
- zero-shot reasoning over inverse relations.

All evaluations are performed using **zero-shot multiple-choice prompting**.

---

## Example Task

Given the sentence:

```text
Marie Curie was born in Warsaw.
```

Determine the correct relation:

```text
A. place_of_birth
B. birthplace_of
```

Correct Answer:

```text
A. place_of_birth
```

---

## Resources

- Dataset: [Hugging Face](https://huggingface.co/datasets/Sefika/FewRel_Converse_Relations)
- Code: [GitHub Repository](https://github.com/sefeoglu/inverserelations)
- Experimental Results: [Zenodo](https://zenodo.org/records/19650827)

---

## Installation

```bash
git clone https://github.com/sefeoglu/inverserelations.git
cd inverserelations
pip install -r requirements.txt
```

---

## Python Usage

```python
from datasets import load_dataset

dataset = load_dataset("Sefika/FewRel_Converse_Relations")

print(dataset)
print(dataset["train"][0])
```

---

## Citation

```bibtex
@misc{fewrel_inverse_2026,
  author       = {Sefeoglu},
  title        = {Reversing Arrows: A Benchmark Dataset for Inverse Relation Directionality in LLMs},
  year         = {2026},
  publisher    = {GitHub and Hugging Face},
  howpublished = {\url{https://github.com/sefeoglu/inverserelations}},
  doi          = {10.57967/hf/8462}
}
```

---

## License

This project is released under the **MIT License**.
