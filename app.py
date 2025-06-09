from dotenv import load_dotenv
load_dotenv()  # Load environment variables

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Configure GenAI with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Gemini model and get SQL query from natural language
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content([prompt[0], question])
    sql_query = response.text.strip()

    # Debug: Print raw response for troubleshooting
    print("RAW Gemini Output:", repr(sql_query))

    # Clean up code block formatting (```sql ... ```)
    if sql_query.startswith("```"):
        sql_query = sql_query.replace("```sqlite", "").replace("```", "").strip()

    # Remove line breaks and leading/trailing whitespace
    sql_query = sql_query.replace('\n', ' ').strip()

    return sql_query

# Function to execute SQL query on SQLite database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except sqlite3.Error as e:
        rows = [(f"SQL Error: {str(e)}",)]
    finally:
        conn.commit()
        conn.close()
    return rows

# Prompt for Gemini
prompt = [
    """
You are an expert SQL assistant. Given a natural language request, convert it into a valid SQLite SQL query that works with the following table:

Table Name: students
Columns:
- id (INTEGER, primary key)
- name (TEXT)
- cgpa (REAL)
- location (TEXT)
- email (TEXT)
- phone_number (TEXT)
- preferred_work_location (TEXT)
- specialization (TEXT)

Example Instructions:
"Show all students with a CGPA above 8.5"
"List students from Bangalore who specialize in Data Science"
"Get the email and phone number of students who prefer to work in Hyderabad"
"Count how many students are from Mumbai"

Output Format:
Just return the SQL query, nothing else.
    """
]

# Streamlit UI
st.set_page_config(page_title="SQL Query from Natural Language")
st.header("Gemini App to Query SQLite Database")

# Input box
question = st.text_input("Enter your question:", key="input")

# Button
submit = st.button("Submit")

# On submit
if submit and question.strip():
    sql_query = get_gemini_response(question, prompt)

    # Show generated SQL query
    st.subheader("Generated SQL Query:")
    st.code(sql_query, language="sql")

    # Execute and show results
    result = read_sql_query(sql_query, "students.db")

    st.subheader("Query Results:")
    if result:
        for row in result:
            st.write(row)
    else:
        st.write("No results found.")
