from flask import Flask, render_template, request, url_for
import os
import boto3
import botocore
from pymysql import connections

app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT") or 3306)
BACKGROUND_IMAGE = os.environ.get("BACKGROUND_IMAGE")
GROUP_NAME = os.environ.get('GROUP_NAME') or "Group11"

def download_image_from_s3(image_url):
    bucket = image_url.split('//')[1].split('.')[0]
    object_name = '/'.join(image_url.split('//')[1].split('/')[1:])
    s3 = boto3.resource('s3')
    output = "static/background_image.png"
    s3.Bucket(bucket).download_file(object_name, output)
    return output

db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

@app.route("/", methods=['GET', 'POST'])
def home():
    image_url = download_image_from_s3(BACKGROUND_IMAGE)
    return render_template('addemp.html', background_image=image_url, group_name=GROUP_NAME)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True) 
