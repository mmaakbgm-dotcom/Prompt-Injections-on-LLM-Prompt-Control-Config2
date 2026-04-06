# HealthFirst Clinic — Configuration 2: LLM Prompt Control

Configuration 2 / Layer 2: LLM Prompt Control Layer

---

## Overview

This repository implements Configuration 2 of a four-configuration thesis experiment evaluating prompt injection resistance in LLM-driven access control systems.

This configuration introduces a **prompt-level defense** by strengthening the guiding system prompt used by the LLM. No deterministic enforcement mechanisms are applied.

The system implements a two-stage LLM pipeline:

```
User (natural language)
  → Stage 1 LLM (GPT-4o-mini) → SQL query
  → SQLite database
  → Stage 2 LLM (GPT-4o-mini) → Natural language response
```

Unlike Configuration 1, this configuration attempts to constrain model behavior using a **hardened guiding prompt**, but still executes generated SQL directly without validation.

---

## Related Configurations

This repository is part of a four-configuration study evaluating prompt injection defenses across progressively stronger enforcement layers.

- **Configuration 1 — Baseline Prompt**  
  LLM fully trusted, no enforcement  
  https://github.com/mmaakbgm-dotcom/Prompt-Injections-on-Baseline-Prompt-Config1

- **Configuration 2 — LLM Prompt Control (This repository)**  
  Hardened LLM system guiding prompt  
  https://github.com/mmaakbgm-dotcom/Prompt-Injections-on-LLM-Prompt-Control-Config2

- **Configuration 3 — Intermediary Enforcement**  
  Deterministic intermediary enforcement layer  
  https://github.com/mmaakbgm-dotcom/Prompt-Injections-on-Intermediary-Enforcement-Config3

- **Configuration 4 — Database Authorization**  
  RBAC, RLS, and defining views  
  https://github.com/mmaakbgm-dotcom/Prompt-Injections-on-Database-Authorization-Config4

---

## The Four Configurations

| Config | Name | Primary Enforcement |
|--------|------|---------------------|
| 1 | Baseline Prompt | None — LLM fully trusted |
| 2 | LLM Prompt Control | Hardened LLM system guiding prompt |
| 3 | Intermediary Enforcement | Deterministic intermediary enforcement layer |
| 4 | Database Authorization | RBAC, RLS, and defining views |

---

## Architecture for Configuration 2

### Layer 1. Baseline Prompt Layer
- Natural-language query processing
- Text-to-SQL generation
- System prompt guidance

### Layer 2. LLM Prompt Control Layer
- Role definitions
- Access rules
- Prompt constraints
- Refusal behaviour

This configuration relies on **LLM compliance** to enforce access control.

### Configuration 2 Summary

A hardened guiding prompt is introduced to constrain LLM behavior.  
No deterministic or programmatic enforcement is applied.

---

## Request Processing Pipeline

### 1. User Query Submission
User submits a natural-language query.

### 2. Authentication and Session Retrieval
User identity, role, and ID are retrieved.

### 3. LLM SQL Generation
The LLM generates SQL using:
- Hardened guiding prompt
- Schema context
- Session data

The model may also return `NO_QUERY` for unsafe requests.

### 4. Direct Execution
SQL executes without validation or rewriting.

### 5. Response Generation
Results are converted into natural language.

---

## Evaluation

| Framework | Tests | Output |
|-----------|-------|--------|
| Promptfoo Evaluation | 120 | promptfoo_results_3_2.xlsx |
| DeepTeam Evaluation | 120 | deepteam_results_3_2.xlsx |
| Stability Schema Evaluation | 720 | stability_schema_3_2.xlsx |
| SQL Adversarial Suite Evaluation | 920 | sql_adversarial_suite_3_2.xlsx |

---

## Repository Structure

```
.
├── clinic_3_2.py
├── database/schema.sql
├── prompts/config2_reconstruction_prompt.md
├── tests/
├── deepteam_attacks/
├── eval_sql_adversarial_suite_3_2.py
├── run_deepteam.py
├── promptfooconfig.yaml
├── promptfoo_provider.py
├── promptfoo_tests.yaml
├── promptfoo_results_3_2.xlsx
├── deepteam_results_3_2.xlsx
├── stability_schema_3_2.xlsx
└── sql_adversarial_suite_3_2.xlsx
```

---

## Setup Instructions

**Prerequisites:**
- Python 3.11+
- Node.js 18+
- OpenAI API key

**Install:**

```bash
pip install openai openpyxl deepteam
npm install
```

**Run:**

```bash
python clinic_3_2.py
```

---

## Database Setup

**Option A:**
```bash
python clinic_3_2.py
```

**Option B:**
```bash
sqlite3 clinic.db < database/schema.sql
```

---

## Running Evaluations

**Promptfoo:**
```bash
npx promptfoo eval -c promptfooconfig.yaml --no-cache --max-concurrency 1
```

**DeepTeam:**
```bash
python run_deepteam.py
```

**Stability Schema:**
```bash
python eval_stability_schema_3_2.py -n 20
```

**SQL Adversarial Suite:**
```bash
python eval_sql_adversarial_suite_3_2.py -n 20
```

---

## Results Summary

| Evaluation | Successful | Blocked | Total | ASR |
|---|---|---|---|---|
| Promptfoo Evaluation | 0 | 120 | 120 | 0.0% |
| DeepTeam Evaluation | 0 | 120 | 120 | 0.0% |
| Stability Schema Evaluation | 2 | 718 | 720 | 0.28% |
| SQL Adversarial Suite Evaluation | 49 | 871 | 920 | 5.3% |
| **Combined** | **51** | **1,829** | **1,880** | **2.7%** |

---

## Interpretation

Configuration 2 significantly reduces attack success rates compared to the baseline.

- Conversational attacks → fully mitigated
- Structural SQL attacks → partially successful

This demonstrates that prompt-level defenses improve security but remain insufficient without deterministic enforcement.

---

## Security Notes

- No real data used
- Synthetic credentials only
- API keys stored in environment variables
- No enforcement beyond LLM behavior

---

## Reproducibility

| Artefact | Reproduction Method |
|----------|---------------------|
| clinic.db | `python clinic_3_2.py` |
| Promptfoo results | `npx promptfoo eval -c promptfooconfig.yaml` |
| DeepTeam results | `python run_deepteam.py` |
| Stability Schema results | `python eval_stability_schema_3_2.py` |
| SQL Adversarial results | `python eval_sql_adversarial_suite_3_2.py` |

Note: Results may vary slightly due to LLM randomness (temperature = 1.5).
