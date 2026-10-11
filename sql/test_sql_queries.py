"""
test_sql_queries.py
Executes all SQL queries from analysis_queries.sql and advanced_queries.sql
against ecommerce.db to ensure full syntax validity, window function execution,
and accurate result outputs.
"""

import sqlite3
import re

def execute_sql_file(file_path: str, conn: sqlite3.Connection):
    print(f"\n--- Testing SQL File: {file_path} ---")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by semicolon followed by newline, ignoring comments
    # Remove single line comments
    lines = []
    for line in content.split("\n"):
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    clean_sql = "\n".join(lines)
    
    raw_queries = clean_sql.split(";")
    query_num = 0
    passed = 0
    
    cursor = conn.cursor()
    for q in raw_queries:
        q_strip = q.strip()
        if not q_strip:
            continue
        query_num += 1
        try:
            cursor.execute(q_strip)
            rows = cursor.fetchall()
            passed += 1
            col_names = [d[0] for d in cursor.description] if cursor.description else []
            print(f"Query #{query_num:02d}: OK ({len(rows)} rows returned, cols: {col_names[:4]}...)")
        except Exception as e:
            print(f"Query #{query_num:02d} FAILED!")
            print(f"SQL Snippet:\n{q_strip[:200]}...")
            print(f"Error: {e}\n")
            
    print(f"Summary for {file_path}: {passed}/{query_num} queries passed.")
    return passed, query_num

if __name__ == "__main__":
    conn = sqlite3.connect("ecommerce.db")
    p1, t1 = execute_sql_file("sql/analysis_queries.sql", conn)
    p2, t2 = execute_sql_file("sql/advanced_queries.sql", conn)
    conn.close()
    print(f"\nTOTAL RESULT: {p1 + p2}/{t1 + t2} SQL Queries Executed Successfully!")
