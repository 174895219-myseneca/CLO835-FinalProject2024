from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from botocore.exceptions import ClientError
import argparse

app = Flask(__name__)

# Configurations directly from environment variables
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.environ.get("S3_BUCKET")
BACKGROUND_IMAGE_KEY = os.environ.get("BACKGROUND_IMAGE_KEY")

db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

def download_s3_image():
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    image_path = 'static/background_image.png'
    try:
        with open(image_path, 'wb') as f:
            s3_client.download_fileobj(S3_BUCKET, BACKGROUND_IMAGE_KEY, f)
        print(f"Successfully downloaded background image from S3 bucket {S3_BUCKET}.")
        return url_for('static', filename='background_image.png')
    except botocore.exceptions.ClientError as error:
        print(f"Error downloading image from S3: {error}")
        return url_for('static', filename='default.png')

@app.route("/")
def home():
    image_url = download_s3_image()
    return render_template('addemp.html', background_image=image_url)

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
