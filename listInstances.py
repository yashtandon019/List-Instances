import time
import json
from multiprocessing import Process, Pipe
import boto3
from botocore.config import Config

regionClient = boto3.client('ec2')

def get_region():
    regions = [region['RegionName'] for region in regionClient.describe_regions()['Regions']]
    return regions

def lambda_handler(event, context):
    data=[]
    regions = get_region()
    for region in regions:
        my_config = Config(region_name=region)
        client = boto3.client("ec2", config=my_config)
        response = client.describe_instances()
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                my_json_string = {'instance-id': instance["InstanceId"], 'region': region, 'instance-type':instance["InstanceType"],'state':instance["State"]["Name"]}
                data.append(my_json_string)
    
    return {
        "statusCode" : 200,
        "body": json.dumps(data)
    }