import json
import base64
from uuid import uuid4
import sys
from pip._internal import main
main(['install', '-I', '-q', 'boto3', '--target', '/tmp/', '--no-cache-dir', '--disable-pip-version-check'])
sys.path.insert(0,'/tmp/')
import boto3

print(boto3.__version__)

S3 = boto3.client('s3', region_name='us-east-1')
iot_client = boto3.client('iot-data', region_name='us-east-1')
rek = boto3.client('rekognition')

need_found = [
    "FACE" 
]
need_feature = {
    "FACE" : [
        "FACE_COVER"
    ]
}

def detect_labels(image, bucket):
    response = rek.detect_protective_equipment(
        Image = {
            'S3Object':{
                'Bucket':bucket,
                'Name': image
            }
        }
    )

    return response

def lambda_handler(event, context):

    image = event['ObjectName']
    bucket = event['Bucket']

    data = json.dumps(detect_labels(image, bucket))
    data = json.loads(data)
    person_data = data["Persons"]
    message = "not found anything in the picture."
    if len(person_data) == 0:
        return{
            "statusCode":200,
            'headers':{
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({
                "success": False,
                "message": message
            })
        }
    for i in person_data:
        found = []
        feature = []
        for k in i["BodyParts"]:
            found.append(k["Name"])
            for equipment in k["EquipmentDetections"]:
                feature.append(equipment["Type"])
        # Check Every Item System need to found.
        for item in need_found:
            if item not in found:
                # iot_client.publish(
                #     topic="access_control/topic",
                #     qos=1,
                #     payload=json.dumps({
                #         "message": "{} not found in the picture.".format(item)
                #     })
                # )
                message = "{} not found in the picture.".format(item)
                return{
                    "statusCode":200,
                    'headers':{
                        'Access-Control-Allow-Origin': '*'
                    },
                    "body": json.dumps({
                        "success": False,
                        "message": message
                    })
                }
        for item in need_feature:
            for equipment in need_feature[item]:
                if equipment not in feature:
                    # iot_client.publish(
                    #     topic="access_control/topic",
                    #     qos=1,
                    #     payload=json.dumps({
                    #         "success": False,
                    #         "message": "{} not found, please check it.".format(equipment)
                    #     })
                    # )
                    message = "{} not found, please check it.".format(equipment)
                    return{
                        "statusCode":200,
                        'headers':{
                            'Access-Control-Allow-Origin': '*'
                        },
                        "body": json.dumps({
                            "success": False,
                            "message": message
                        })
                    }
    # iot_client.publish(
    #     topic="access_control/topic",
    #     qos=1,
    #     payload=json.dumps({
    #         "message": "Door is opened."
    #     })
    # )
    message = "Passed!"
    return{
        "statusCode":200,
        'headers':{
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps({
            "success": True,
            "message": message
        })
    }
