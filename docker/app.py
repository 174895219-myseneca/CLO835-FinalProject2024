from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from botocore.exceptions import ClientError
import argparse

app = Flask(__name__)

# Database configuration from environment variables
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")  # Corrected typo from 'passwors'
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))

# AWS S3 and ConfigMap configuration
S3_BUCKET = os.environ.get("S3_BUCKET")
BACKGROUND_IMAGE = os.environ.get("BACKGROUND_IMAGE")  # This will be the file name stored in the ConfigMap

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

def get_s3_client():
    """Create an S3 client configured from environment variables"""
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

def fetch_background_image_url():
    """Generate a presigned URL for the background image stored in S3"""
    s3_client = get_s3_client()
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': S3_BUCKET,
                                                            'Key': BACKGROUND_IMAGE},
                                                    ExpiresIn=3600)
    except ClientError as e:
        print(f"Couldn't fetch background image from S3: {e}")
        return None
    return response

@app.route("/", methods=['GET', 'POST'])
def home():
    background_image_url = fetch_background_image_url()
    return render_template('addemp.html', background_image=background_image_url)

@app.route("/about", methods=['GET','POST'])
def about():
    background_image_url = fetch_background_image_url()
    return render_template('about.html', background_image=background_image_url)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = first_name + " " + last_name
    finally:
        cursor.close()

    print(f"All modifications done. Employee {emp_name} added successfully.")
    return render_template('addempoutput.html', name=emp_name, background_image=fetch_background_image_url())

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    background_image_url = fetch_background_image_url()
    return render_template("getemp.html", background_image=background_image_url)

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id = %s"
    cursor = db_conn.cursor()
    output = {}

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        if result:
            output = {
                "emp_id": result[0],
                "first_name": result[1],
                "last_name": result[2],
                "primary_skills": result[3],
                "location": result[4]
            }
    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        cursor.close()

    return render_template("getempoutput.html", **output, background_image=fetch_background_image_url())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)  # Set to run on port 81
