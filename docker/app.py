from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse

app = Flask(__name__)

# Corrected the environment variable names
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))

db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}

COLOR = random.choice(list(color_codes.keys()))

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', color=color_codes[COLOR])

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html', color=color_codes[COLOR])

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    
    insert_sql = "INSERT INTO employee (first_name, last_name, primary_skill, location) VALUES (%s, %s, %s)"
    cursor = db_conn.cursor()
    try:
        cursor.execute(insert_sql, (first_name, last_name, primary_skill, location))  
        db_conn.commit()
        emp_name = first_name + " " + last_name
    except Exception as e:
        print("Failed to insert data:", e)
    finally:
        cursor.close()

    return render_template('addempoutput.html', name=emp_name, color=color_codes[COLOR])

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=color_codes[COLOR])

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']
    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skills, location from employee where emp_id=%s"
    cursor = db_conn.cursor()
   
   if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False, help="Set the color for the app")
    args = parser.parse_args()

    COLOR = args.color if args.color else random.choice(list(color_codes.keys()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=False)
