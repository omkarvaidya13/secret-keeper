from flask import Flask, request, jsonify
import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

my_config = Config(
    region_name='us-east-1'
)
rds_data = boto3.client('rds-data', config=my_config,
                        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

# Database Configuration Items
aurora_db_name = os.environ.get('AURORA_DB_NAME')
aurora_cluster_arn = os.environ.get('AURORA_CLUSTER_ARN')
aurora_secret_arn = os.environ.get('AURORA_SECRET_ARN')


@app.route('/getPerson')
def getPerson():
    personId = request.args.get('personId')
    response = callDbWithStatement(
        "SELECT * FROM Persons WHERE personId='" + str(personId) + "'")
    person = {}
    records = response['records']
    for record in records:
        person['personId'] = record[0]['longValue']
        person['firstName'] = record[1]['stringValue']
        person['lastName'] = record[2]['stringValue']
    print(person)
    return jsonify(person)


@app.route('/createPerson',  methods=['POST'])
def createPerson():
    request_data = request.get_json()
    personId = str(request_data['personId'])
    firstName = request_data['firstName']
    lastName = request_data['lastName']
    callDbWithStatement("INSERT INTO Persons(personId, firstName, lastName) VALUES ('"
                        + personId + "', '" + firstName + "', '" + lastName + "');")
    return ""


def callDbWithStatement(statement):
    response = rds_data.execute_statement(
        database=aurora_db_name,
        resourceArn=aurora_cluster_arn,
        secretArn=aurora_secret_arn,
        sql=statement,
        includeResultMetadata=True
    )
    print("Making Call " + statement)
    return response


if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=8081)
