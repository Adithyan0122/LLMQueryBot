import pandas as pd

# Sample data
data = {
    "Name": ["Alice Johnson", "Bob Smith", "Carol Lee"],
    "CGPA": [8.5, 7.9, 9.2],
    "Location": ["New Delhi", "Mumbai", "Bangalore"],
    "Email": ["alice@example.com", "bob@example.com", "carol@example.com"],
    "Phone Number": ["9876543210", "9123456780", "9988776655"],
    "Preferred Work Location": ["Bangalore", "Pune", "Hyderabad"],
    "Specialization in degree": ["AI", "Cybersecurity", "Data Science"]
}

# Create DataFrame
df = pd.DataFrame(data)

# Write to Excel
excel_file = "students.xlsx"
df.to_excel(excel_file, index=False)

print(f"'{excel_file}' created with sample data.")
