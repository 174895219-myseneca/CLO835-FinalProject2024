from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from botocore.exceptions import NoCredentialsError
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))

# AWS S3 configuration
S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

# Group and slogan configuration
GROUP_NAME = os.environ.get("GROUP_NAME", "InnovateMax")
SLOGAN = os.environ.get("SLOGAN", "Innovation at its peak!")

# MySQL database connection
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

# Download image from S3
def download_image_from_s3():
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    try:
        local_filename = "/tmp/background.jpg"
        # Assuming the S3_BUCKET_URL is a full path to the file including the bucket name
        bucket_name = S3_BUCKET_URL.split('/')[2]
        key = '/'.join(S3_BUCKET_URL.split('/')[3:])
        s3_client.download_file(bucket_name, key, local_filename)
        print("Background image downloaded: " + local_filename)
        return local_filename
    except NoCredentialsError:
        print("Credentials not available")
        return None

@app.route("/", methods=['GET', 'POST'])
def home():
    background_image = download_image_from_s3()
    return render_template('addemp.html', background_image=background_image, group_name=GROUP_NAME, slogan=SLOGAN)

@app.route("/about", methods=['GET', 'POST'])
def about():
    background_image = download_image_from_s3()
    return render_template('about.html', background_image=background_image, group_name=GROUP_NAME, slogan=SLOGAN)

@app.route("/addemp", methods=['POST'])
def add_emp():
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
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    background_image = download_image_from_s3()
    return render_template('addempoutput.html', name=emp_name, background_image=background_image, group_name=GROUP_NAME, slogan=SLOGAN)

@app.route("/getemp", methods=['GET', 'POST'])
def get_emp():
    emp_id = request.form.get('emp_id')
    cursor = db_conn.cursor()
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id = %s"
    cursor.execute(select_sql, (emp_id,))
    result = cursor.fetchone()
    cursor.close()

    employee = {
        "emp_id": result[0],
        "first_name": result[1],
        "last_name": result[2],
        "primary_skills": result[3],
        "location": result[4]
    } if result else None

    background_image = download_image_from_s3()
    return render_template("getempoutput.html", employee=employee, background_image=background_image, group_name=GROUP_NAME, slogan=SLOGAN)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=81, help='Port to run the application on')
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=True)
