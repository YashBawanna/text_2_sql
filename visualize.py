from dotenv import load_dotenv
import os
import sqlite3
import pandas as pd
import plotly.express as px
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

def get_sql(question):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""You are a SQL expert. Given this schema:
{SCHEMA}

Convert this to SQLite SQL:
"{question}"

Rules:
- Return ONLY the SQL query
- No explanations, no markdown, no backticks
- Use proper SQLite syntax
"""
        }]
    )
    return response.choices[0].message.content.strip()

def get_chart_type(question, columns):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Given this question: "{question}"
And these result columns: {columns}

Reply with ONLY one word - the best chart type:
- bar (for comparisons)
- line (for trends over time)
- pie (for percentages/parts of whole)
- scatter (for correlations)"""
        }]
    )
    return response.choices[0].message.content.strip().lower()

def run_query(sql):
    conn = sqlite3.connect('sales.db')
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def ask_and_visualize(question):
    print(f"\n❓ Question: {question}")

    # Step 1: Get SQL
    sql = get_sql(question)
    print(f"🔍 SQL: {sql}")

    # Step 2: Run query
    df = run_query(sql)
    print(f"📋 Results:\n{df.to_string()}")

    # Step 3: Get chart type
    chart_type = get_chart_type(question, list(df.columns))
    print(f"📊 Chart type: {chart_type}")

    # Step 4: Auto generate chart
    cols = list(df.columns)
    x_col = cols[0]
    y_col = cols[1] if len(cols) > 1 else cols[0]

    if chart_type == "bar":
        fig = px.bar(df, x=x_col, y=y_col, title=question,
                     color=x_col, template="plotly_dark")
    elif chart_type == "line":
        fig = px.line(df, x=x_col, y=y_col, title=question,
                      template="plotly_dark")
    elif chart_type == "pie":
        fig = px.pie(df, names=x_col, values=y_col, title=question,
                     template="plotly_dark")
    else:
        fig = px.scatter(df, x=x_col, y=y_col, title=question,
                         template="plotly_dark")

    fig.update_layout(title_font_size=16)
    fig.show()
    print("✅ Chart opened in browser!")

# Run 3 demo questions
ask_and_visualize("Which region has the highest total revenue?")
ask_and_visualize("What are the top 5 best selling products?")
ask_and_visualize("How many orders are completed vs pending vs cancelled?")
