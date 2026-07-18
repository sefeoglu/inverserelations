#!/usr/bin/env bash
set -euo pipefail

# Run from anywhere by resolving project root relative to this script.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

PYTHON_BIN="${PYTHON_BIN:-python}"
TEKGEN_RELATIONS="data/ablation-tekgen/tekgen_relations.json"
TEKGEN_OUTPUT_DIR="data/mqa/tekgen"
FEWREL_OUTPUT_DIR="data/mqa/fewrel"

# Optional FewRel inputs (can be overridden via environment variables).
FEWREL_DATA_ORIGINAL="${FEWREL_DATA_ORIGINAL:-data/ablation-tekgen/original_fewrel_inverse.json}"
FEWREL_DATA_SYNTHETIC="${FEWREL_DATA_SYNTHETIC:-data/mqa/fewrel/synthetic_templates_with_desc.json}"
FEWREL_DATA_MT="${FEWREL_DATA_MT:-data/ablation-tekgen/original_fewrel_inverse.json}"
FEWREL_RELATIONS="${FEWREL_RELATIONS:-${FEWREL_OUTPUT_DIR}/pid2name_fewrel.json}"

echo "[1/5] Regenerating TekGen AI prompts (with/without desc, negative in option C)..."
"${PYTHON_BIN}" src/question_generation/template_tekgen.py \
  --data "${TEKGEN_OUTPUT_DIR}/artificial_tekgen_negative_with_desc.json" \
  --relations "${TEKGEN_RELATIONS}" \
  --output "${TEKGEN_OUTPUT_DIR}/artificial_tekgen_negative.json" \
  --type-ent AI \
  --include-nodesc \
  --include-negative

echo "[2/5] Regenerating TekGen original-entity prompts (with/without desc, negative in option C)..."
"${PYTHON_BIN}" src/question_generation/template_tekgen.py \
  --data "${TEKGEN_OUTPUT_DIR}/artificial_tekgen_negative_with_desc.json" \
  --relations "${TEKGEN_RELATIONS}" \
  --output "${TEKGEN_OUTPUT_DIR}/artificial_templates_negative.json" \
  --type-ent TEKGEN \
  --include-nodesc \
  --include-negative

echo "[3/5] Regenerating TekGen mathematical-variable prompts (with/without desc, negative in option C)..."
"${PYTHON_BIN}" src/question_generation/template_tekgen.py \
  --data "${TEKGEN_OUTPUT_DIR}/artificial_tekgen_negative_with_desc.json" \
  --relations "${TEKGEN_RELATIONS}" \
  --output "${TEKGEN_OUTPUT_DIR}/mathematical_variable_negative.json" \
  --type-ent MT \
  --include-nodesc \
  --include-negative

echo "[4/5] Regenerating TekGen test prompts (with/without desc, negative in option C)..."
"${PYTHON_BIN}" src/question_generation/template_tekgen.py \
  --data "${TEKGEN_OUTPUT_DIR}/tekgen_negative_test_with_desc.json" \
  --relations "${TEKGEN_RELATIONS}" \
  --output "${TEKGEN_OUTPUT_DIR}/tekgen_negative_test.json" \
  --type-ent TEKGEN \
  --include-nodesc \
  --include-negative

echo "[5/5] Regenerating FewRel prompts in a separate folder tree..."
if [[ -f "${FEWREL_RELATIONS}" && -f "${FEWREL_DATA_ORIGINAL}" && -f "${FEWREL_DATA_SYNTHETIC}" && -f "${FEWREL_DATA_MT}" ]]; then
  "${PYTHON_BIN}" src/question_generation/template.py \
    --mode fewrel \
    --data "${FEWREL_DATA_ORIGINAL}" \
    --relations "${FEWREL_RELATIONS}" \
    --output "${FEWREL_OUTPUT_DIR}/original_templates.json"

  "${PYTHON_BIN}" src/question_generation/template.py \
    --mode ai \
    --data "${FEWREL_DATA_SYNTHETIC}" \
    --relations "${FEWREL_RELATIONS}" \
    --output "${FEWREL_OUTPUT_DIR}/synthetic_templates.json"

  "${PYTHON_BIN}" src/question_generation/template.py \
    --mode mt \
    --data "${FEWREL_DATA_MT}" \
    --relations "${FEWREL_RELATIONS}" \
    --output "${FEWREL_OUTPUT_DIR}/mathematical_variable_templates.json"
else
  echo "Skipping FewRel regeneration because one or more FewRel-only inputs are missing."
  echo "Expected: ${FEWREL_RELATIONS} ${FEWREL_DATA_ORIGINAL} ${FEWREL_DATA_SYNTHETIC} ${FEWREL_DATA_MT}"
fi

echo "Done. Prompt generation complete."
