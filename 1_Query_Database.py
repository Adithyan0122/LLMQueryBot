from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

st.set_page_config(page_title="Query Database")
st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content([prompt[0], question])
    sql_query = response.text.strip()
    if sql_query.startswith("```"):
        sql_query = sql_query.replace("```sqlite", "").replace("```", "").strip()
    sql_query = sql_query.replace('\n', ' ').strip()
    return sql_query

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

prompt = ["""
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

Only return the SQL query, nothing else.
"""]

st.header("💡 Natural Language SQL Query")

question = st.text_input("Ask a question about the student database:", key="input")
submit = st.button("Submit")

if submit and question.strip():
    sql_query = get_gemini_response(question, prompt)

    st.subheader("🛠️ Generated SQL Query:")
    st.code(sql_query, language="sql")

    result = read_sql_query(sql_query, "students.db")

    st.subheader("📋 Query Results:")
    if result:
        for row in result:
            st.write(row)
    else:
        st.write("No results found.")