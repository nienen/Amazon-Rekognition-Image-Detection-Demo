import json
import boto3
rek = boto3.client('rekognition')

def lambda_handler(event, context):
    photo = '<xxx.jpg>'
    bucket = '<bucket_name>'
    
    labels = rek.detect_labels(
        Image = {
            'S3Object':{
                'Bucket':bucket,
                'Name':photo
                }
            },
            MaxLabels = 10
        )

    for label in labels['Labels']:
        print ("Label: " + label['Name'])
        print ("Confidence: " + str(label['Confidence']))
        print ("Instances:")
        for instance in label['Instances']:
            print ("  Bounding box")
            print ("    Top: " + str(instance['BoundingBox']['Top']))
            print ("    Left: " + str(instance['BoundingBox']['Left']))
            print ("    Width: " +  str(instance['BoundingBox']['Width']))
            print ("    Height: " +  str(instance['BoundingBox']['Height']))
            print ("  Confidence: " + str(instance['Confidence']))
            print()

        print ("Parents:")
        for parent in label['Parents']:
            print ("   " + parent['Name'])
        print ("----------")
        print ()

        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
