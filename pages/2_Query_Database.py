from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# ---------------- Streamlit Setup ----------------
st.set_page_config(page_title="Query Database")
st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)

# ---------------- API Key ----------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ---------------- Prompt Base ----------------
base_prompt = """
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
"""

# ---------------- Gemini Model Call ----------------
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content([prompt, question])
    sql_query = response.text.strip()
    if sql_query.startswith("```"):
        sql_query = sql_query.replace("```sqlite", "").replace("```", "").strip()
    sql_query = sql_query.replace('\n', ' ').strip()
    return sql_query

# ---------------- Execute SQL Query ----------------
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

# ---------------- RAG: Get Similar Examples ----------------
def get_similar_examples(question):
    conn = sqlite3.connect("data/examples.db")
    cur = conn.cursor()
    cur.execute("SELECT question, query FROM examples")
    rows = cur.fetchall()
    conn.close()

    question_words = set(question.lower().split())
    similar = []
    for q, query in rows:
        overlap = len(set(q.lower().split()) & question_words)
        if overlap > 0:
            formatted = f"-- {q}\n{query}"
            similar.append((overlap, formatted, q, query))

    similar.sort(reverse=True)
    return similar[:3]  # Return top 3 with raw data for debugging

# ---------------- UI ----------------
st.header("💡 Natural Language SQL Query")
question = st.text_input("Ask a question about the student database:", key="input")
submit = st.button("Submit")

# ---------------- Submit Handler ----------------
if submit and question.strip():
    # Get similar examples using RAG
    similar_examples = get_similar_examples(question)
    examples_prompt = "\n\n".join([ex[1] for ex in similar_examples])

    # Combine base prompt + examples
    full_prompt = base_prompt + "\n\nHere are some examples:\n" + examples_prompt if examples_prompt else base_prompt

    # Show RAG examples used
    if similar_examples:
        st.subheader("📚 Similar Examples Used (RAG):")
        for _, _, q_text, sql_text in similar_examples:
            st.markdown(f"**Q:** {q_text}")
            st.code(sql_text, language="sql")

    # Get SQL from Gemini
    sql_query = get_gemini_response(question, full_prompt)

    # Store in session_state
    st.session_state["last_question"] = question
    st.session_state["last_sql_query"] = sql_query

    st.subheader("🛠️ Generated SQL Query:")
    st.code(sql_query, language="sql")

    # Execute query on students.db
    result = read_sql_query(sql_query, "students.db")
    st.session_state["last_result"] = result

    st.subheader("📋 Query Results:")
    if result:
        for row in result:
            st.write(row)
    else:
        st.write("No results found.")

# ---------------- Save Button (Works after Submit) ----------------
if "last_result" in st.session_state and st.session_state["last_result"]:
    if st.button("✅ Save this as a good example for future (RAG)"):
        conn = sqlite3.connect("data/examples.db")
        cur = conn.cursor()
        question = st.session_state["last_question"]
        sql_query = st.session_state["last_sql_query"]

        # Avoid duplicates
        cur.execute("SELECT * FROM examples WHERE question = ? AND query = ?", (question, sql_query))
        exists = cur.fetchone()

        if not exists:
            cur.execute("INSERT INTO examples (question, query) VALUES (?, ?)", (question, sql_query))
            conn.commit()
            st.success("Example saved successfully! 🎉")
        else:
            st.info("This example already exists in the database.")

        conn.close()