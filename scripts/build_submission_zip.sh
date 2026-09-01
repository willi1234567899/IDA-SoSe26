#!/usr/bin/env bash
# Build ISIS submission zip for Group 38 (Submission Requirements.pdf).
set -euo pipefail

GROUP=38
ROOT_NAME="SoSe26_Case_Study_Group_${GROUP}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT_DIR="${1:-${REPO_ROOT}/..}"
STAGE="${OUT_DIR}/${ROOT_NAME}"
ZIP_PATH="${OUT_DIR}/${ROOT_NAME}.zip"

echo "Staging submission folder: ${STAGE}"
rm -rf "${STAGE}"
mkdir -p "${STAGE}/Data" "${STAGE}/Additional_files" "${STAGE}/www" "${STAGE}/.streamlit"

# --- Required notebooks, HTML, app ---
cp "${REPO_ROOT}/SoSe26_General_Tasks_Group_${GROUP}.ipynb" "${STAGE}/"
cp "${REPO_ROOT}/SoSe26_General_Tasks_Group_${GROUP}.html" "${STAGE}/"
cp "${REPO_ROOT}/SoSe26_Case_Study_Group_${GROUP}.ipynb" "${STAGE}/"
cp "${REPO_ROOT}/SoSe26_Case_Study_Group_${GROUP}.html" "${STAGE}/"
cp "${REPO_ROOT}/SoSe26_Case_Study_App_Group_${GROUP}.py" "${STAGE}/"

# --- Defect pipeline (notebook reproducibility) ---
cp "${REPO_ROOT}/defect_pipeline.py" "${STAGE}/"
cp "${REPO_ROOT}/rebuild_final_with_defects.py" "${STAGE}/"

# --- Run support ---
cp "${REPO_ROOT}/requirements.txt" "${STAGE}/"
cp "${REPO_ROOT}/.streamlit/config.toml" "${STAGE}/.streamlit/"

# --- Data: final CSV only (no tubCloud originals, no intermediate cache) ---
cp "${REPO_ROOT}/Data/SoSe26_Case_Study_finalData_Group_${GROUP}.csv" "${STAGE}/Data/"

# --- Additional_files: screenshots ---
cp "${REPO_ROOT}/Additional_files/"*.png "${STAGE}/Additional_files/" 2>/dev/null || true

# --- www: app static assets ---
cp "${REPO_ROOT}/www/style.css" "${STAGE}/www/"
cp -R "${REPO_ROOT}/www/fonts" "${STAGE}/www/"
cp -R "${REPO_ROOT}/www/img" "${STAGE}/www/"

# --- Zip ---
rm -f "${ZIP_PATH}"
(
  cd "${OUT_DIR}"
  zip -r "${ZIP_PATH##*/}" "${ROOT_NAME}" \
    -x "*.DS_Store" -x "*__pycache__*"
)

echo ""
echo "Created: ${ZIP_PATH}"
echo "Contents:"
find "${STAGE}" -type f | sort | sed "s|${STAGE}/|  |"
