import json
import boto3
import time
import calendar
import random
import re
rek = boto3.client('rekognition')
ddb = boto3.client('dynamodb')

def lambda_handler(event, context):
    photo = event['ObjectName']
    bucket = 'car-detect-store-yourname'
    table_name = 'your-table-name'
    

    labels = rek.detect_labels(
        Image = {
            'S3Object':{
                'Bucket':bucket,
                'Name': photo
                }
            },
            MaxLabels = 5
        )

    print('Detected labels for ' + photo) 

    detected_labels = []
    
    for label in labels['Labels']:
        detected_labels.append(label['Name'])
    print(detected_labels)
    
    if "Car" in detected_labels or "Vehicle" in detected_labels or "Sports Car" in detected_labels:
        isCar = True
    else:
        return ("There is no car in image")
    
    print("---------")
    
    text_in_pic = rek.detect_text(
        Image = {
            'S3Object':{
                'Bucket':bucket,
                'Name': photo
                }
            }
        )

    license_plate = "no detect the license plate in pic"
    
    for license in text_in_pic['TextDetections']:
        match_text = re.match(r"^[A-Z|0-9]{2,3}\-\d{4}$|^\d{4}\-[A-Z]{2}$|^[0-9|A-Z]{1}\d{5}$|^[0-9]{1}[A-Z]{1}\d{4}$|^[A-Z|0-9]{2,3}\d{4}$|^\d{4}\-\d{2}", license['DetectedText'])
        print(match_text)
        if match_text:
            license_plate = license['DetectedText']
            break

    print('---------')
    print (license_plate)

    if license_plate != "no detect the license plate in pic":
        rek_result = "There is a car in image, License Plate: " + str(license_plate)
        ava = "0"
    else:
        rek_result = "There is a car in image, But "+ license_plate
        ava = "0"

    
    now = str(calendar.timegm(time.gmtime()))
    station = ['A','B','C','D']
    item = ddb.put_item(
        TableName = table_name,
        Item={
            'Time': {
                'S': now
            },
            'Station':{
                'S': random.choice(station)
            },
            'ava':{
                'S': ava
            },
            'license_plate':{
                'S': license_plate
            }
        }
    )
    return (rek_result)

    