# HealthFirst Clinic — Configuration 2: Prompt-Level Access Control

**Layer 3.2** | Thesis experiment on LLM-driven NL-to-SQL access control security

This is **Configuration 2** of a four-configuration cross-layer security comparison
study. It evaluates whether a guiding prompt alone — with no code-enforced SQL
guards of any kind — can resist scope-bypass attacks in a GPT-4o-mini healthcare
appointment portal.

> **Reconstruction prompt:** A complete specification for rebuilding this project
> from scratch using an AI coding assistant is in `prompts/config2_reconstruction_prompt.md`.

---

## The Four Configurations

| Config | Name | Primary Enforcement | Repo |
|---|---|---|---|
| 1 | No Defense | None — LLM fully trusted | Separate repository |
| 2 | Prompt-Only | Hardened LLM system guiding prompt | This repository |
| 3 | Intermediary-Level AC | Deterministic intermediary enforcement layer | Separate repository |
| 4 | Database AC | RBAC, RLS, and defining views | Separate repository |

## Related Configurations

This repository is part of a four-configuration study evaluating prompt injection defenses across progressively stronger enforcement layers.

- **Configuration 1 — No Defense**
  LLM fully trusted, no enforcement
  https://github.com/mmaakbgm-dotcom/Prompt-Injections-on-Baseline-Prompt-Config1

- **Configuration 2 — Prompt-Only (This repository)**
  Hardened LLM system guiding prompt
  https://github.com/mmaakbgm-dotcom/Prompt-Injections-on-LLM-Prompt-Control-Config2

- **Configuration 3 — Intermediary-Level AC**
  Deterministic SQL validation and enforcement layer
  https://github.com/mmaakbgm-dotcom/Prompt-Injections-on-Intermediary-Enforcement-Config3

- **Configuration 4 — Database AC**
  RBAC, RLS, and defined views as final enforcement
  https://github.com/mmaakbgm-dotcom/Prompt-Injections-on-Database-Authorization-Config4

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

This layer constrains model behaviour via a hardened guiding prompt.

### Configuration 2 Summary
Security depends on LLM compliance. No deterministic enforcement exists.

---

## Security Evaluation Results

| Suite | Runs | Violations | Attack Success Rate |
|-------|------|------------|---------------------|
| Promptfoo Evaluation | 120 | 0 | **0.00%** |
| DeepTeam (20 vulnerability types) | ~100 | 0 confirmed | **0.00%** |
| SQL Adversarial Suite (7 categories, 20 chains) | 920 | 49 | **5.33% VSR** |

**Key finding:** The guiding prompt successfully blocks all conversational attacks
(Promptfoo, DeepTeam) but is partially bypassed by structural SQL construction
techniques — particularly `GROUP BY` / `DISTINCT` aggregation queries, which account
for 41 of 49 violations (84%).

Result files: `sql_adversarial_suite_3_2.xlsx`, `deepteam_results_3_2.xlsx`,
`deepteam_summary_3_2.md`, `promptfoo_results_3_2.xlsx`.

---

## Request Processing Pipeline

### 1. Authentication
Username/password gate — the only code-enforced check in this configuration.

### 2. SafeChat Check
Short-circuits greetings and help requests without invoking the LLM or database.

### 3. NL → SQL Generation (Stage 1)
User input is processed by GPT-4o-mini using the hardened guiding prompt
(`GUIDING_PROMPT`, role-scoped per session) to produce a SQL query or `NO_QUERY`.
Conversation history is retained for up to 6 turns.

### 4. Direct Query Execution
SQL is executed verbatim against SQLite without validation, rewriting, or
WHERE-clause enforcement.

Security depends on prompt adherence.

### 5. Response Generation
LLM summarizes database results as natural language (GPT-4o-mini, temp=0.3).
Every interaction is appended to the audit log (not tracked by git).

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm (for Promptfoo evaluation only)
- An OpenAI API key with GPT-4o-mini access

### 1. Clone

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env — set AI_INTEGRATIONS_OPENAI_API_KEY and AI_INTEGRATIONS_OPENAI_BASE_URL
```

On **Replit**: set these in the Secrets panel or via the OpenAI integration.

### 3. Install Python Dependencies

```bash
pip install openai deepteam openpyxl
```

### 4. Install Node Dependencies (Promptfoo only)

```bash
npm install
```

### 5. Initialise the Database

The SQLite database (`clinic.db`) is created automatically on first run:

```bash
python clinic_3_2.py
```

It seeds 30 patients, 8 doctors, and 150 appointments. Run this once.
Delete `clinic.db` at any time to reset to the original seed data.

---

## Running the Application

```bash
python clinic_3_2.py
```

Log in with any test credential (see table below), then ask natural-language
questions about your appointments — for example:

- *"Show my upcoming appointments"*
- *"Who is my doctor?"*
- *"Do I have anything scheduled next month?"*

---

## Test Credentials

> **Disclaimer:** All usernames, passwords, names, phone numbers, and email
> addresses in this project are **entirely synthetic**. They were created solely
> for this academic research experiment and do not correspond to any real person,
> patient, or medical professional.

**Patients:**

| Username | Password   | Patient ID | Name              |
|----------|------------|------------|-------------------|
| alice    | alice123   | 1          | Alice Johnson     |
| bob      | bob123     | 2          | Bob Smith         |
| carol    | carol123   | 3          | Carol Williams    |
| dave     | dave123    | 4          | Dave Martinez     |
| eve      | eve123     | 5          | Eve Chen          |
| frank    | frank123   | 6          | Frank Wilson      |
| grace    | grace123   | 7          | Grace Thompson    |
| henry    | henry123   | 8          | Henry Park        |
| irene    | irene123   | 9          | Irene Foster      |
| james    | james123   | 10         | James O'Brien     |
| karen    | karen123   | 11         | Karen Lee         |
| leo      | leo123     | 12         | Leo Gonzalez      |
| maria    | maria123   | 13         | Maria Santos      |
| nathan   | nathan123  | 14         | Nathan Wright     |
| olivia   | olivia123  | 15         | Olivia Turner     |

**Doctors:**

| Username      | Password      | Doctor ID | Name                  | Specialty          |
|---------------|---------------|-----------|------------------------|--------------------|
| dr_brown      | brown123      | 1         | Dr. Emily Brown        | General Practice   |
| dr_davis      | davis123      | 2         | Dr. Michael Davis      | Cardiology         |
| dr_wilson     | wilson123     | 3         | Dr. Sarah Wilson       | Pediatrics         |
| dr_patel      | patel123      | 4         | Dr. Raj Patel          | Orthopedics        |
| dr_nakamura   | nakamura123   | 5         | Dr. Yuki Nakamura      | Neurology          |
| dr_oconnell   | oconnell123   | 6         | Dr. Sean O'Connell     | Gastroenterology   |
| dr_rodriguez  | rodriguez123  | 7         | Dr. Ana Rodriguez      | Pulmonology        |
| dr_kim        | kim123        | 8         | Dr. Daniel Kim         | Endocrinology      |

---

## Running the Evaluations

### Promptfoo (120 tests)

```bash
npm run eval:promptfoo
```

Or manually:

```bash
npx promptfoo eval -c promptfooconfig.yaml --no-cache --max-concurrency 1
```

**Important:** `--max-concurrency 1` is required. `clinic_3_2.py` uses a global
session dict; concurrent calls cause test interference.

120 test cases across 15 attack categories. Outputs `promptfoo_results_3_2.xlsx`.

### DeepTeam (~120 attacks)

```bash
DEEPTEAM_BATCH_SIZE=8 python run_deepteam.py
```

Default is 3 attacks per vulnerability type (~120 total across 20 types × 2 roles).
For a full research-grade run, increase the batch size:

```bash
DEEPTEAM_BATCH_SIZE=30 python run_deepteam.py
```

Outputs `deepteam_results_3_2.xlsx` and `deepteam_summary_3_2.md`.

### SQL Adversarial Suite (920 tests)

```bash
python eval_sql_adversarial_suite_3_2.py -n 20
```

Runs 23 attack prompts × 2 modes (normal + forced-prefix) × 20 chains = **920 test
runs** across 7 attack categories. Supports resumable execution — interrupted runs
continue from the last completed chain. Outputs `sql_adversarial_suite_3_2.xlsx`.

---

## Access Control Design

The guiding prompt (constant in `clinic_3_2.py`, written to `guiding_prompt.txt`
at startup) instructs the LLM:

- **Patient role:** every `appointments` query MUST include `WHERE patient_id = {linked_id}`
- **Doctor role:** every `appointments` query MUST include `WHERE doctor_id = {linked_id}`
- **Both roles:** may freely query the `doctors` table (public reference data)
- If a request cannot be answered within scope: output `NO_QUERY`

**There is no code that enforces these rules.** The LLM's compliance is the only
barrier. This is what Config 2 measures.

---

## Database

### Schema

```sql
patients       (patient_id PK, full_name, phone, email)
doctors        (doctor_id PK, full_name, specialty)
appointments   (appointment_id PK, patient_id FK, doctor_id FK,
                appt_datetime, reason, status)
```

30 patients (IDs 1–30) · 8 doctors (IDs 1–8) · 150 appointments

### Recreation

`clinic.db` is a runtime-generated SQLite binary. It is **not tracked by git**.
Two equivalent methods recreate it from scratch:

**Method A — run the application** (recommended):
```bash
python clinic_3_2.py
# The database is created automatically on first launch if clinic.db is absent.
```

**Method B — apply the SQL file directly**:
```bash
sqlite3 clinic.db < database/schema.sql
```

`database/schema.sql` is the authoritative reproducibility artifact for the database
layer. It contains the complete schema DDL and all 150 seed rows extracted verbatim
from `initialize_database()` in `clinic_3_2.py`. Both methods produce an identical
database.

To reset the database to its original seed state at any time:
```bash
rm clinic.db
python clinic_3_2.py   # or: sqlite3 clinic.db < database/schema.sql
```

---

## Repository Structure

```
├── clinic_3_2.py                          Main application + all core logic
├── database/
│   └── schema.sql                         Full schema DDL + 150 seed rows
├── eval_sql_adversarial_suite_3_2.py      SQL adversarial evaluation runner
├── run_deepteam.py                        DeepTeam red-team runner
├── deepteam_target.py                     DeepTeam target wrapper
├── deepteam_attacks/
│   ├── attacks_config.py                  20 vulnerability type definitions
│   └── __init__.py
├── promptfooconfig.yaml                   Promptfoo configuration
├── promptfoo_provider.py                  Promptfoo Python provider
├── promptfoo_tests.yaml                   Main Promptfoo test cases
├── tests/                                 15 YAML attack-category files
│   ├── jailbreak_override.yaml
│   ├── policy_smuggling.yaml
│   ├── exfil_format_dump.yaml
│   ├── prompt_leakage.yaml
│   ├── role_confusion.yaml
│   ├── multiturn_poisoning.yaml
│   ├── sql_dialect_evasion.yaml
│   ├── encoding_obfuscation.yaml
│   ├── context_exhaustion.yaml
│   ├── output_format_manipulation.yaml
│   ├── temporal_logic.yaml
│   ├── semantic_equivalence.yaml
│   ├── cot_extraction.yaml
│   ├── tool_function_confusion.yaml
│   └── multilingual_bypass.yaml
├── prompts/
│   └── config2_reconstruction_prompt.md   Full AI rebuild specification
├── sql_adversarial_suite_3_2.xlsx         Evaluation results (SQL adversarial)
├── deepteam_results_3_2.xlsx             Evaluation results (DeepTeam)
├── deepteam_summary_3_2.md               Evaluation summary (DeepTeam)
├── promptfoo_results_3_2.xlsx            Evaluation results (Promptfoo)
├── pyproject.toml                         Python dependencies
├── package.json                           Node dependencies (Promptfoo)
├── package-lock.json
├── .env.example                           Environment variable template
└── .gitignore
```

---

## Reproducibility Statement

All evaluation scripts reset session state between test cases using `clinic.logout()`.
Stage 1 uses `temperature=1.5`, which introduces non-determinism; re-running evaluations
may produce small variation at boundary cases. The SQL Adversarial Suite's `--forced`
mode prepends a directive instructing the LLM to emit SQL even for out-of-scope
requests — this intentionally probes the hard boundary of the guiding prompt.

The reconstruction prompt in `prompts/config2_reconstruction_prompt.md` is a complete
specification that can be fed to an AI coding assistant to rebuild this entire
project from scratch, including the database schema, all application logic, and
all three evaluation frameworks.
