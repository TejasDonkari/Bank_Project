from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin123",
        database="bank_database"
    )

@app.route("/")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT branch_name FROM bank_master")
    branches = cursor.fetchall()

    cursor.execute("SELECT branch_name, COUNT(*) FROM bank_master GROUP BY branch_name")
    branch_counts = cursor.fetchall()

    cursor.execute("SELECT loan_type, COUNT(*) FROM bank_master GROUP BY loan_type")
    loan_counts = cursor.fetchall()

    cursor.execute("SELECT customer_name, loan_amount FROM bank_master ORDER BY loan_amount DESC LIMIT 10")
    top_customers = cursor.fetchall()

    cursor.execute("SELECT MONTH(loan_date), SUM(loan_amount) FROM bank_master GROUP BY MONTH(loan_date)")
    monthly_loan = cursor.fetchall()

    cursor.execute("SELECT branch_name, SUM(loan_amount) FROM bank_master GROUP BY branch_name")
    loan_by_branch = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        branches=branches,
        branch_counts=branch_counts,
        loan_counts=loan_counts,
        top_customers=top_customers,
        monthly_loan=monthly_loan,
        loan_by_branch=loan_by_branch
    )

@app.route("/filter")
def filter_data():
    branch = request.args.get("branch")

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Loans by branch
    cursor.execute(
        "SELECT branch_name, COUNT(*) FROM bank_master WHERE branch_name=%s GROUP BY branch_name",
        (branch,)
    )
    branch_counts = cursor.fetchall()

    # 2. Loan types
    cursor.execute(
        "SELECT loan_type, COUNT(*) FROM bank_master WHERE branch_name=%s GROUP BY loan_type",
        (branch,)
    )
    loan_counts = cursor.fetchall()

    # 3. Top customers
    cursor.execute(
        "SELECT customer_name, loan_amount FROM bank_master WHERE branch_name=%s ORDER BY loan_amount DESC LIMIT 10",
        (branch,)
    )
    top_customers = cursor.fetchall()

    # 4. Monthly loan amount
    cursor.execute(
        "SELECT MONTH(loan_date), SUM(loan_amount) FROM bank_master WHERE branch_name=%s GROUP BY MONTH(loan_date)",
        (branch,)
    )
    monthly_loan = cursor.fetchall()

    # 5. Total loan amount for branch
    cursor.execute(
        "SELECT branch_name, SUM(loan_amount) FROM bank_master WHERE branch_name=%s GROUP BY branch_name",
        (branch,)
    )
    loan_by_branch = cursor.fetchall()

    conn.close()

    return jsonify({
        "branch_counts": branch_counts,
        "loan_counts": loan_counts,
        "top_customers": top_customers,
        "monthly_loan": monthly_loan,
        "loan_by_branch": loan_by_branch
    })

if __name__ == "__main__":
    app.run(debug=True)
