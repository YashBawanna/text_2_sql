from dotenv import load_dotenv
import os
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
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

Reply with ONLY one word:
- bar (for comparisons)
- line (for trends over time)
- pie (for percentages)
- scatter (for correlations)"""
        }]
    )
    return response.choices[0].message.content.strip().lower()

def run_query(sql):
    conn = sqlite3.connect('sales.db')
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def generate_chart(df, question, chart_type):
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
        fig = px.pie(df, names=x_col, values=y_col,
                     title=question, template="plotly_dark")
    else:
        fig = px.scatter(df, x=x_col, y=y_col, title=question,
                         template="plotly_dark")

    fig.update_layout(title_font_size=16)
    return fig

# ===== STREAMLIT UI =====
st.set_page_config(
    page_title="Text to SQL",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Text to SQL — AI Business Intelligence")
st.markdown("*Ask any business question in plain English — get instant charts*")

# Sidebar with demo questions
st.sidebar.title("💡 Try these questions")
demo_questions = [
    "Which region has the highest total revenue?",
    "What are the top 5 best selling products?",
    "How many orders are completed vs pending vs cancelled?",
    "Which customer segment generates the most revenue?",
    "What is the monthly revenue trend?",
    "Which product category has the highest average order value?"
]

selected_demo = st.sidebar.radio("Quick select:", demo_questions)

if st.sidebar.button("▶ Run this question"):
    st.session_state.question = selected_demo

# Main input
st.subheader("🔍 Ask a Question")
question = st.text_input(
    "Type your business question:",
    value=st.session_state.get("question", ""),
    placeholder="e.g. Which region has the highest revenue?"
)

if st.button("🚀 Generate Answer", type="primary"):
    if question:
        with st.spinner("🤖 AI is thinking..."):

            # Step 1: Generate SQL
            sql = get_sql(question)

            # Step 2: Run query
            try:
                df = run_query(sql)

                # Step 3: Get chart type
                chart_type = get_chart_type(
                    question, list(df.columns)
                )

                # Step 4: Generate chart
                fig = generate_chart(df, question, chart_type)

                # Display results
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.subheader("📋 Data Results")
                    st.dataframe(df, use_container_width=True)

                    st.subheader("🔍 Generated SQL")
                    st.code(sql, language="sql")

                with col2:
                    st.subheader("📊 Visualization")
                    st.plotly_chart(fig, use_container_width=True)

                # Success metrics
                st.success(
                    f"✅ Found {len(df)} rows | "
                    f"Chart: {chart_type} | "
                    f"Powered by Groq + LLaMA"
                )

            except Exception as e:
                st.error(f"❌ Query failed: {str(e)}")
                st.code(sql, language="sql")
                st.info("Try rephrasing your question!")
    else:
        st.warning("Please enter a question first!")

# Footer
st.markdown("---")
st.markdown(
    "Built with Streamlit · Groq AI · "
    "LLaMA 3.3 · SQLite · Plotly"
)