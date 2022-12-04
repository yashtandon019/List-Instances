import json
import concurrent.futures
import boto3
from multiprocessing import Process, Pipe
from botocore.config import Config

regionClient = boto3.client('ec2')

def list_instances(region, conn):
    # EC2_RESOURCE = boto3.resource('ec2', region_name=region)
    # instances = EC2_RESOURCE.instances.all()
    data=[]
    my_config = Config(region_name=region)
    client = boto3.client("ec2", config=my_config)
    response = client.describe_instances()
    for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                my_json_string = {'instance-id': instance["InstanceId"], 'region': region, 'instance-type':instance["InstanceType"],'state':instance["State"]["Name"]}
                data.append(my_json_string)
    print(data)
    conn.send(data)
    conn.close()
    
    
def get_region():
    regions = [region['RegionName'] for region in regionClient.describe_regions()['Regions']]
    # print(regions)
    processes = []
    parent_connections = []
    instanceresponse = []
    for region in regions:            
        # create a pipe for communication
        parent_conn, child_conn = Pipe()
        parent_connections.append(parent_conn)
        process = Process(target=list_instances, args=(region, child_conn,))
        processes.append(process)
        
    # start all processes
    for process in processes:
        process.start()

    # make sure that all processes have finished
    for process in processes:
        process.join()

    for parent_connection in parent_connections:
        instanceresponse.append(parent_connection.recv())
    return instanceresponse
    
def lambda_handler(event, context):
    
    finalresponse = get_region()
    
    return {
        "statusCode": 200,
        "body": json.dumps(finalresponse)
        }