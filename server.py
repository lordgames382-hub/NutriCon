from flask import Flask, render_template, request
import sqlite3
import os
import shutil
from AIclient import generate_health_advice

# Initialize the Flask application
app = Flask(__name__)

# 1. Define paths for Render vs Local Environment
if os.path.exists('/data'):
    # Production Paths on Render
    DB_PATH = '/data/Nutricon.db'
    FEEDBACK_PATH = '/data/feedback.txt'
    
    # Render downloads your GitHub files into /opt/render/project/src/
    SRC_DB_PATH = '/opt/render/project/src/Nutricon.db'
    
    # AUTOMATIC INITIALIZATION: If the database doesn't exist on the persistent disk yet,
    # copy the original seeded database file from your repository over to /data/
    if not os.path.exists(DB_PATH) and os.path.exists(SRC_DB_PATH):
        print(f"Initializing persistent storage: Copying {SRC_DB_PATH} to {DB_PATH}")
        shutil.copy2(SRC_DB_PATH, DB_PATH)
else:
    # Local Paths on your PC
    DB_PATH = 'Nutricon.db'
    FEEDBACK_PATH = 'feedback.txt'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html', conditions=get_all_conditions())

@app.route('/get_report', methods=['POST'])
def get_report():
    selected_conditions = request.form.getlist('conditions')
    
    # Backend safety cap
    if len(selected_conditions) > 3:
        return "Error: Maximum 3 conditions allowed for safety reasons. Please see a doctor.", 400
    
    if not selected_conditions:
        return "Please select at least one condition.", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    final_results = {}

    # Existing conflict resolution logic (Prioritizing higher IDs)
    for condition in selected_conditions:
        cursor.execute("""
            SELECT f.foodname, o.role, o.priority 
            FROM FoodOverrides o
            JOIN Foods f ON o.foodID = f.foodID
            JOIN Conditions c ON o.conditionID = c.ConditionID
            WHERE c.name = ?
        """, (condition,))
        
        for foodname, role, priority in cursor.fetchall():
            # If food is already in results, only update if new priority is HIGHER
            if foodname not in final_results or priority > final_results[foodname]['priority']:
                final_results[foodname] = {'role': role, 'priority': priority}
            # If priorities are equal but roles conflict, default to 'Irritant' for safety
            elif priority == final_results[foodname]['priority'] and role != final_results[foodname]['role']:
                final_results[foodname]['role'] = 'Irritant'

    conn.close()
    
    # Separate lists and call SLM
    avoid = [name for name, data in final_results.items() if data['role'] == 'Irritant']
    prioritize = [name for name, data in final_results.items() if data['role'] == 'Coolant']
    
    conditions_str = ", ".join(selected_conditions)
    personal_advice = generate_health_advice(conditions_str, ", ".join(prioritize), "Combined Profile")

    return render_template('report.html', avoid=avoid, prioritize=prioritize, advice=personal_advice)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback = request.form.get('feedback_text')
    
    with open(FEEDBACK_PATH, "a") as f:
        f.write(f"Feedback received: {feedback}\n---\n")
    
    return render_template('thank_you.html')

def get_all_conditions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Conditions ORDER BY name ASC")
    conditions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return conditions

# The "Run" block required to start the server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
