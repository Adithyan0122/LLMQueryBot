import sqlite3
import pandas as pd

# Load Excel file
excel_file = 'students.xlsx'
df = pd.read_excel(excel_file)

df.columns = df.columns.str.strip()

# Database setup
db_name = 'students.db'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cgpa REAL,
        location TEXT,
        email TEXT,
        phone_number TEXT,
        preferred_work_location TEXT,
        specialization TEXT
    )
''')

# Insert data
for index, row in df.iterrows():
    cursor.execute('''
        INSERT INTO students (
            name, cgpa, location, email, phone_number, preferred_work_location, specialization
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        row['Name'],
        row['CGPA'],
        row['Location'],
        row['Email'],
        row['Phone Number'],
        row['Preferred Work Location'],
        row['Specialization in Degree']
    ))

# Commit changes
conn.commit()

# Fetch and display all data
print("\nContents of the 'students' table:")
cursor.execute("SELECT * FROM students")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close connection
conn.close()
