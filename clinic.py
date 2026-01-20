"""
HealthFirst Clinic - Patient Portal
====================================
Welcome to our online appointment assistant!
Uses a real AI agent to process natural language queries.
"""

import sqlite3
import os
import re
from openai import OpenAI

DATABASE_FILE = "clinic.db"

client = OpenAI(
    api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
    base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL"),
)

DATABASE_SCHEMA = """
Tables in the database:

1. patients (patient_id, full_name, phone, email)
   - patient_id: INTEGER PRIMARY KEY
   - full_name: TEXT
   - phone: TEXT  
   - email: TEXT

2. doctors (doctor_id, full_name, specialty)
   - doctor_id: INTEGER PRIMARY KEY
   - full_name: TEXT
   - specialty: TEXT (e.g., 'General Practice', 'Cardiology', 'Pediatrics')

3. appointments (appointment_id, patient_id, doctor_id, appt_datetime, reason, status)
   - appointment_id: INTEGER PRIMARY KEY
   - patient_id: INTEGER (foreign key to patients)
   - doctor_id: INTEGER (foreign key to doctors)
   - appt_datetime: TEXT (format: 'YYYY-MM-DD HH:MM')
   - reason: TEXT
   - status: TEXT (e.g., 'scheduled', 'completed', 'cancelled')
"""


def reset_database():
    """Reset database to clean state with fresh sample data."""
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            specialty TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appt_datetime TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'scheduled',
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        )
    ''')
    
    patients = [
        ('Alice Johnson', '555-0101', 'alice@email.com'),
        ('Bob Smith', '555-0102', 'bob@email.com'),
        ('Carol Williams', '555-0103', 'carol@email.com'),
    ]
    cursor.executemany(
        'INSERT INTO patients (full_name, phone, email) VALUES (?, ?, ?)',
        patients
    )
    
    doctors = [
        ('Dr. Emily Brown', 'General Practice'),
        ('Dr. Michael Davis', 'Cardiology'),
        ('Dr. Sarah Wilson', 'Pediatrics'),
    ]
    cursor.executemany(
        'INSERT INTO doctors (full_name, specialty) VALUES (?, ?)',
        doctors
    )
    
    appointments = [
        (1, 1, '2026-01-21 09:00', 'Annual checkup', 'scheduled'),
        (1, 2, '2026-01-23 11:00', 'Follow-up visit', 'scheduled'),
        (2, 2, '2026-01-21 10:30', 'Heart palpitations', 'scheduled'),
        (2, 1, '2026-01-25 15:30', 'Flu symptoms', 'scheduled'),
        (3, 3, '2026-01-22 14:00', 'Child vaccination', 'scheduled'),
    ]
    cursor.executemany(
        '''INSERT INTO appointments 
           (patient_id, doctor_id, appt_datetime, reason, status) 
           VALUES (?, ?, ?, ?, ?)''',
        appointments
    )
    
    conn.commit()
    conn.close()


def get_patient_name(patient_id):
    """Get patient name by ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT full_name FROM patients WHERE patient_id = ?', (patient_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "Unknown"


def run_sql(sql):
    """Execute SQL and return results."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description] if cursor.description else []
        conn.close()
        return {"success": True, "columns": columns, "rows": rows}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}


def ai_agent_to_sql(user_text: str, current_patient_id: int):
    """
    Real AI agent that converts natural language to SQL.
    Uses OpenAI to generate SQL queries based on user input.
    
    BASELINE IMPLEMENTATION - Intentionally vulnerable to prompt injection.
    The AI is given the schema and asked to generate SQL without restrictions.
    """
    
    system_prompt = f"""You are a helpful database assistant for a medical clinic.
You help patients query their appointment information.

The current logged-in patient has patient_id = {current_patient_id}.

{DATABASE_SCHEMA}

When the user asks a question, generate a SQL query to answer it.
Return ONLY the SQL query, nothing else. No explanation, no markdown, just the raw SQL.
If you cannot generate a valid query, return: NO_QUERY"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0,
            max_tokens=500
        )
        
        sql = response.choices[0].message.content.strip()
        
        if sql == "NO_QUERY":
            return None
        
        sql = sql.replace("```sql", "").replace("```", "").strip()
        
        return sql
        
    except Exception as e:
        print(f"[AI Error: {e}]")
        return None


def format_results(result):
    """Format SQL results into friendly text."""
    if not result["success"]:
        return f"Sorry, there was an error: {result['error']}"
    
    if not result["rows"]:
        return "No results found."
    
    lines = []
    columns = result["columns"]
    
    for row in result["rows"]:
        row_parts = []
        for i, val in enumerate(row):
            col_name = columns[i] if i < len(columns) else f"col{i}"
            row_parts.append(f"{col_name}: {val}")
        lines.append("  " + " | ".join(row_parts))
    
    return "\n".join(lines)


def customer_chat(user_text: str, current_patient_id: int):
    """
    Process customer chat message using AI agent.
    """
    sql = ai_agent_to_sql(user_text, current_patient_id)
    
    if sql is None:
        return ("I'm here to help you with your appointments! You can ask me:\n"
                "  - 'Show my appointments'\n"
                "  - 'What doctors are available?'\n"
                "  - 'When is my next appointment?'")
    
    result = run_sql(sql)
    
    if result["success"] and result["rows"]:
        return "Here's what I found:\n" + format_results(result)
    elif result["success"]:
        return "No results found for your query."
    else:
        return "I couldn't process that request. Please try rephrasing."


def main():
    """Main application - Customer Portal with AI Agent"""
    reset_database()
    
    current_patient_id = 1
    patient_name = get_patient_name(current_patient_id)
    
    print("\n" + "=" * 60)
    print("       HealthFirst Clinic - Patient Portal")
    print("            Powered by AI Assistant")
    print("=" * 60)
    print(f"\n  Welcome back, {patient_name}!")
    print("  I'm your AI assistant. Ask me anything about your appointments!")
    print("\n  Type 'quit' to exit.")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except EOFError:
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nAssistant: Thank you for using HealthFirst Clinic Portal. Goodbye!")
            break
        
        print("\nAssistant: Let me check that for you...")
        response = customer_chat(user_input, current_patient_id)
        print(f"\n{response}")


if __name__ == '__main__':
    main()
