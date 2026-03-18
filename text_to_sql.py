from dotenv import load_dotenv
import os
import sqlite3
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Database schema - tells Claude what tables exist
SCHEMA = """
Tables in the database:

customers (customer_id, name, email, region, segment)
products (product_id, name, category, price)
orders (order_id, customer_id, product_id, quantity, order_date, total_amount, status)

regions: North, South, East, West
segments: Enterprise, SMB, Startup
categories: Software, Hardware, Services, Consulting
statuses: Completed, Pending, Cancelled
"""

def get_sql_from_claude(user_question):
    """Send question to Claude, get SQL back"""
    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""You are a SQL expert. Given this database schema:
{SCHEMA}

Convert this question to a valid SQLite SQL query:
"{user_question}"

Rules:
- Return ONLY the SQL query, nothing else
- No explanations, no markdown, no backticks
- Use proper SQLite syntax
- Always use JOIN when combining tables
"""
        }]
    )
    return response.choices[0].message.content.strip()

def run_query(sql):
    """Execute SQL on the database"""
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    conn.close()
    return columns, results

def ask(question):
    """Full pipeline: question → SQL → results"""
    print(f"\n❓ Question: {question}")
    
    # Get SQL from Claude
    sql = get_sql_from_claude(question)
    print(f"🔍 SQL Generated:\n{sql}")
    
    # Run the query
    columns, results = run_query(sql)
    
    # Print results
    print(f"\n📊 Results:")
    print(" | ".join(columns))
    print("-" * 50)
    for row in results:
        print(" | ".join(str(val) for val in row))
    print(f"\n✅ {len(results)} rows returned")

# Test with 3 questions
ask("Which region has the highest total revenue?")
ask("What are the top 3 best selling products?")
ask("How many orders were completed vs cancelled?")