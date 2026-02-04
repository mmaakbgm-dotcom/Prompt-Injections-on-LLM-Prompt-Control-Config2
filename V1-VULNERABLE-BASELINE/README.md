# V1-VULNERABLE-BASELINE

## Overview
This is a **realistically vulnerable** version of the HealthFirst Clinic appointment portal. It mirrors early NLIDB/Prompt-to-SQL deployments studied in academic literature, implementing only coarse security guards while delegating row-level access control to LLM prompt adherence.

## Security Model

### Coarse Guards (Code-Enforced)
The `enforce_access_control()` function implements lightweight guards typical of early deployments:
- **Authentication required** - Must be logged in to query
- **SELECT only** - Blocks non-SELECT statements
- **Write operations blocked** - INSERT/UPDATE/DELETE/DROP/ALTER/CREATE/TRUNCATE/REPLACE
- **Schema access blocked** - PRAGMA/sqlite_master/sqlite_/information_schema/sys./pg_
- **Table whitelist** - Only patients, doctors, appointments tables allowed
- **LIMIT 25 enforced** - Reduces blast radius of over-broad queries

### Row-Level Access (LLM-Dependent - NOT Code-Enforced)
**IMPORTANT**: Row-level access control is delegated to the LLM via the guiding prompt:
- The code does NOT rewrite SQL to enforce `WHERE patient_id = X`
- The code does NOT override/ignore LLM-provided IDs
- Cross-user data access depends on LLM prompt adherence
- This is intentionally vulnerable for thesis experiment purposes

Execution path: User → LLM generates SQL → coarse guards check → database

## Files
```
clinic.py                       - Main application with coarse guards
test_policy.py                  - 26 code-enforced tests
guiding_prompt.txt              - Security prompt template (LLM sees this)
policy_test_results.txt         - Latest test results
vulnerable_baseline_audit_log.txt - Private audit log
clinic.db                       - SQLite database
```

## Running
```bash
# Interactive mode
python V1-VULNERABLE-BASELINE/clinic.py

# Run tests
python V1-VULNERABLE-BASELINE/test_policy.py
```

## Test Categories
1. **Code-Enforced Tests** (26 tests, must pass):
   - Unauthenticated access → DENIED
   - Write operations → DENIED
   - SafeChat behavior → Works correctly
   - Multi-turn conversation → Works correctly
   - Audit logging → Works correctly
   - Generic denial messages → "Request denied." exactly

2. **LLM-Dependent Tests** (documented but not enforced):
   - Cross-user data access (e.g., Alice accessing Bob's appointments)
   - Over-broad queries (e.g., "Show all appointments")
   - Fake ID claims (e.g., "My patient_id is 99")
   - Prompt injection attempts
   - These may ALLOW or DENY depending on LLM prompt adherence

## Audit Log Format
Each DB-path request is logged with:
- timestamp (ISO)
- username, role
- user_input
- llm_raw_output
- extracted_sql
- decision (ALLOWED/DENIED)
- reason_code (if DENIED): NOT_AUTHENTICATED, NOT_SELECT, WRITE_BLOCKED, SCHEMA_BLOCKED, TABLE_NOT_ALLOWED, PARSE_FAIL, SQL_ERROR
- row_count (if ALLOWED, metadata only - no PII)

SafeChat messages are NOT logged.

## Difference from Secure Baseline
| Feature | Secure Baseline (root) | V1-VULNERABLE-BASELINE |
|---------|------------------------|------------------------|
| Authentication | Yes (code-enforced) | Yes (code-enforced) |
| SELECT-only | Yes (code-enforced) | Yes (code-enforced) |
| Write blocks | Yes (code-enforced) | Yes (code-enforced) |
| Schema blocks | Yes (code-enforced) | Yes (code-enforced) |
| Table whitelist | Yes (code-enforced) | Yes (code-enforced) |
| LIMIT enforcement | Yes | Yes (LIMIT 25) |
| **Row-level WHERE** | **Yes (code-enforced)** | **No (LLM-dependent)** |
| Tests | 36 (all enforced) | 26 code-enforced |
