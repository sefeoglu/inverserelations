#!/usr/bin/env bash
set -euo pipefail

# Run from anywhere by resolving project root relative to this script.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

PYTHON_BIN="${PYTHON_BIN:-python}"

RELATIONS_FILE="data/ablation-tekgen/tekgen_relations.json"

# 1) Original TekGen templates (with_desc + without_desc)
"${PYTHON_BIN}" src/question_generation/template_tekgen.py \
  --data data/mqa/tekgen/tekgen_without_desc.json \
  --relations "${RELATIONS_FILE}" \
  --output data/mqa/tekgen/tekgen.json \
  --type-ent TEKGEN \
  --include-nodesc

# 2) Artificial TekGen templates (with_desc + without_desc)
"${PYTHON_BIN}" src/question_generation/template_tekgen.py \
  --data data/mqa/tekgen/artificial_tekgen_without_desc.json \
  --relations "${RELATIONS_FILE}" \
  --output data/mqa/tekgen/artificial_tekgen.json \
  --type-ent AI \
  --include-nodesc

# 3) Artificial source with original entities (with_desc + without_desc)
"${PYTHON_BIN}" src/question_generation/template_tekgen.py \
  --data data/mqa/tekgen/artificial_tekgen_without_desc.json \
  --relations "${RELATIONS_FILE}" \
  --output data/mqa/tekgen/artificial_templates.json \
  --type-ent TEKGEN \
  --include-nodesc

echo "Generated template files under data/mqa/tekgen/."