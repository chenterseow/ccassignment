from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'candidate'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Index.html')

@app.route("/getcand", methods=['POST'])
def about():
    return render_template('JobApplyHistory.html')

@app.route("/addcand", methods=['POST'])
def AddCand():
    cand_id = request.form['cand_id']
    company_name = request.form['company_name']
    job_name = request.form['job_name']
    job_dep = request.form['job_department']
    job_location = request.form['job_location']
    cand_document_file = request.files['cand_document_file']

    insert_sql = "INSERT INTO candidate VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if cand_document_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (cand_id, company_name, job_name, job_dep, job_location))
        db_conn.commit()
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "cand-id-" + str(cand_id) + "_document_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading document to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=cand_document_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('JobApplyOutput.html', name=cand_id)

@app.route("/finddata", methods=['GET', 'POST'])
def searchCandProcess():
    cand_id = request.form['cand_id']

    search_sql = "SELECT * FROM candidates WHERE Candidates_ID=%s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, (cand_id))
    cursor.close()  

    return render_template('JobApplyHistoryOutput.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

