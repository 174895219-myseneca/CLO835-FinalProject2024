from flask import Flask, render_template, request, url_for
from pymysql import connections
import os
import boto3
from botocore.exceptions import ClientError
import argparse
import random

app = Flask(__name__)

# Environment Configuration
DBHOST = os.getenv("DBHOST", "localhost")
DBUSER = os.getenv("DBUSER", "root")
DBPWD = os.getenv("DBPWD", "passwors")  # Assumed to be intentionally misspelled for example purposes
DATABASE = os.getenv("DATABASE", "employees")
DBPORT = int(os.getenv("DBPORT", 3306))
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
BACKGROUND_IMAGE_KEY = os.getenv("BACKGROUND_IMAGE_KEY")
GROUP_NAME = os.getenv('GROUP_NAME', 'GROUP11')

# Supported Colors
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}
COLOR = random.choice(list(color_codes.values()))

# Database Connection
db_conn = connections.Connection(
    host=DBHOST, port=DBPORT, user=DBUSER, password=DBPWD, db=DATABASE
)

@app.route("/", methods=['GET', 'POST'])
def home():
    image_url = fetch_background_image_url()
    return render_template('addemp.html', background_image=image_url, group_name=GROUP_NAME)

def fetch_background_image_url():
    """Fetches the presigned URL of the background image from S3."""
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': S3_BUCKET, 'Key': BACKGROUND_IMAGE_KEY},
                                                    ExpiresIn=3600)
    except ClientError as e:
        print(f"Failed to get presigned URL due to: {e}")
        return url_for('static', filename='default.png')  # Fallback image
    return response

@app.route("/about", methods=['GET', 'POST'])
def about():
    image_url = fetch_background_image_url()
    return render_template('about.html', background_image=image_url, group_name=GROUP_NAME)

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
        emp_name = f"{first_name} {last_name}"
    except Exception as e:
        print(f"Error inserting employee: {e}")
        emp_name = "Error adding employee"
    finally:
        cursor.close()

    image_url = fetch_background_image_url()
    return render_template('addempoutput.html', name=emp_name, background_image=image_url, group_name=GROUP_NAME)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    image_url = fetch_background_image_url()
    return render_template("getemp.html", background_image=image_url, group_name=GROUP_NAME)

@app.route("/fetchdata", methods=['POST'])
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
        output["error"] = "Error fetching employee data"
    finally:
        cursor.close()

    image_url = fetch_background_image_url()
    return render_template("getempoutput.html", **output, background_image=image_url, group_name=GROUP_NAME)

if __name__ == '__main__':
    # Command line arguments for optional settings
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', help='Set the background color for the app', required=False)
    args = parser.parse_args()
    
    if args.color and args.color in color_codes:
        COLOR = color_codes[args.color]
    
    app.run(host='0.0.0.0', port=81, debug=True)
