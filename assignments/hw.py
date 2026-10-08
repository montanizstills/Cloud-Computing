import boto3

import cloud_watch
import sns
import utils
import bucket
import ec2
import os
from boto3.dynamodb.conditions import Key, Attr



def assignment_1():
    # prompt user for bucket
    bucket_name = "deziah-bucket"
    # prompt user for folder
    folder = "folder2"
    # prompt user for file

    # assignment1
    bucket.create_s3_bucket(bucket_name)
    bucket.create_s3_folder(bucket_name, folder)
    bucket.upload_s3_object_to_bucket(bucket_name, "C:\\users\\user\\battery-report.html")


def assignment_2():
    profile = "iam_root"
    region = "us-east-1"
    ec2_resource = ec2.create_ec2_resource(profile=profile, region=region)

    key_name = "my_python_key4"
    ec2.create_key_pair(
        ec2_resource,
        key_name,
        os.path.join(utils.get_absolute_directory_path('Cloud Computing'), f"{key_name}.pem")
    )

    ec2_args = {
        'ImageId': 'ami-0c7217cdde317cfec',
        'MinCount': 1,
        'MaxCount': 1,
        'InstanceType': 't2.micro',
        'KeyName': key_name,
        'SecurityGroups': ['http'],  # named security group
        'BlockDeviceMappings': [
            {
                "DeviceName": '/dev/sda1',
                "Ebs": {"VolumeSize": 10}
            }
        ]
    }
    ec2.launch_ec2_instance(ec2_resource, **ec2_args)


def assignment_3():
    profile = "iam_root"
    region = "us-east-1"
    ec2_resource = ec2.create_ec2_resource(profile=profile, region=region)

    key_name = "my_python_key6"
    ec2.create_key_pair(
        ec2_resource,
        key_name,
        os.path.join(utils.get_absolute_directory_path('Cloud Computing'), f"{key_name}.pem")
    )

    ec2_args = {
        'ImageId': 'ami-0c7217cdde317cfec',
        'MinCount': 1,
        'MaxCount': 1,
        'InstanceType': 't2.micro',
        'KeyName': key_name,
        'SecurityGroups': ['http'],
        'BlockDeviceMappings': [
            {
                "DeviceName": '/dev/sda1',
                "Ebs": {"VolumeSize": 10}
            }
        ]
    }
    instance = ec2.launch_ec2_instance(ec2_resource, **ec2_args)

    cloudwatch_resource = cloud_watch.create_cloud_watch_resource(region=region, profile=profile)
    alarm_details = {
        'AlarmName': 'my-alarm',
        'AlarmDescription': 'Reboot when StatusCheckFailed',
        'ActionsEnabled': True,
        'AlarmActions': [
            'arn:aws:automate:us-east-1:ec2:reboot',
        ],
        'Dimensions': [{'Name': 'InstanceId', 'Value': instance.instance_id}],
        'Period': 60,
        "Unit": 'Seconds',
        'EvaluationPeriods': 3,
        'Statistic': 'Average',
        'Threshold': 90.0,
        'ComparisonOperator': 'GreaterThanThreshold',
    }
    cloud_watch.create_alarm(cloudwatch_resource, **alarm_details)


def assignment_4():
    # choose profile
    profile = "iam_root"
    region = "us-east-1"

    session = boto3.Session(profile_name=profile)
    ec2_resource = session.resource('ec2', region_name=region)
    ec2_client = boto3.client('ec2')

    # get security group id
    security_group_id = [security_group.id for security_group in ec2_resource.security_groups.all() if
                         security_group.group_name == 'WebApp_SSH&HTTPS'][0]

    # create EC2 Launch template
    ec2_client.create_launch_template(
        LaunchTemplateData={
            'ImageId': 'ami-0e1d30f2c40c4c701',
            'InstanceType': 't2.micro',
            'KeyName': 'AutoScale_T2_Micro_AWS-AMI',
            'SecurityGroupIds': [security_group_id],
        },
        LaunchTemplateName='my-template',
    )

    # create auto scaling group
    as_client = boto3.client('autoscaling', region_name='us-east-1')

    as_group = as_client.create_auto_scaling_group(
        AutoScalingGroupName='my-group',
        LaunchTemplate={
            'LaunchTemplateName': 'my-template',
        },
        MinSize=0,
        MaxSize=3,
        DesiredCapacity=0,
        AvailabilityZones=['us-east-1a', 'us-east-1b']
    )

    # create scale up policy
    response = as_client.put_scaling_policy(
        AutoScalingGroupName='my-group',
        PolicyName='my-simple-scale',
        PolicyType='SimpleScaling',
        AdjustmentType='ChangeInCapacity',
        ScalingAdjustment=1,
        Cooldown=150,
        Enabled=True
    )
    simple_scale_arn = response['PolicyARN']
    cloudwatch = boto3.resource('cloudwatch', region_name='us-east-1')
    metric = cloudwatch.Metric('AWS/EC2', 'CPUUtilization')

    # create alarm to monitor cpu utilization above 70%
    alarm = metric.create_alarm(
        AlarmName='cpu-alarm',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        ActionsEnabled=True,
        AlarmActions=[simple_scale_arn],
        AlarmDescription='Alarm when CPU exceeds 70%',
        Unit='Percent'
    )


def assignment_5():
    ec2 = boto3.resource('ec2', region_name='us-east-1')

    # create VPC
    vpc = ec2.create_vpc(CidrBlock='192.168.0.0/16')
    vpc.wait_until_available()

    # create internet gateway and attach it to the VPC
    internet_gateway = ec2.create_internet_gateway()
    vpc.attach_internet_gateway(InternetGatewayId=internet_gateway.id)
    print(internet_gateway.id)

    # create a route table and a public route
    route_table = vpc.create_route_table()
    route = route_table.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=internet_gateway.id
    )
    print(route_table.id)
    # create a public subnet
    subnet = ec2.create_subnet(
        CidrBlock='192.168.1.16/28',
        AvailabilityZone='us-east-1a',
        VpcId=vpc.id
    )
    subnet.create_tags(
        Tags=[
            {
                "Key": "Name",
                "Value": "my-public-subnet-1a"
            }
        ]
    )
    subnetName = subnet.tags[0]['Value']
    print(subnetName + ' ' + subnet.id + ' ' + subnet.availability_zone)
    route_table.associate_with_subnet(SubnetId=subnet.id)

    # create a private subnet
    subnet = ec2.create_subnet(
        CidrBlock='',
        AvailabilityZone='us-east-1a',
        VpcId=vpc.id
    )
    subnet.create_tags(
        Tags=[
            {
                "Key": "Name",
                "Value": "my-private-subnet-1a"
            }
        ]
    )
    # find the subnets associated with the route table
    route_table = ec2.RouteTable(route_table.id)
    associations = route_table.associations_attribute
    for i in range(len(associations)):
        if i == 0:
            subnets = associations[0]['SubnetId']
        else:
            subnets = subnets + ', ' + associations[i]['SubnetId']

    print(subnets)
    # create two security groups for these two subnets.
    private_security_group = ec2.create_security_group(
        GroupName='my-vpc-private-subnet-security-group',
        Description='my vpc private subnet security group',
        VpcId=vpc.id)

    private_security_group.authorize_ingress(
        CidrIp=vpc.cidr_block,  # allowing traffic from internal of vpc
        IpProtocol='-1'  # allowing all protocol and all ports
    )

    print(private_security_group.id)

    public_security_group = ec2.create_security_group(
        GroupName='my-vpc-public-subnet-security-group',
        Description='my vpc public subnet security group',
        VpcId=vpc.id)

    public_security_group.authorize_ingress(
        CidrIp='',  # allowing traffic from anywhere
        IpProtocol='tcp',
        FromPort=80,
        ToPort=80
    )

    # Launch two instances into these two subnets.
    instances = ec2.create_instances(
        ImageId='ami-038f1ca1bd58a5790',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='ec2keypair',
        NetworkInterfaces=[{
            'SubnetId': subnet.id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [public_security_group.id]
        }],
    )


def assignment_6():
    # create vpc
    ec2 = boto3.resource('ec2', region_name='us-east-1')
    vpc = ec2.create_vpc()
    vpc.wait_until_available()

    # create two public subnets in vpc
    subnet1 = ec2.create_subnet()
    subnet2 = ec2.create_subnet()

    # Create a security group allowing SSH (TCP port 22).
    security_group = ec2.create_security_group(
        GroupName='my-security-group',
        Description='my security group',
        VpcId=vpc.id
    )

    # Create a target group with target type as instance and protocol with TCP port 22.
    elbv2 = boto3.client('elbv2', region_name='us-east-1')

    target_group = elbv2.create_target_group(
        Name='my-target-group',
        Protocol='TCP',
        Port=22,
        VpcId=vpc.id,
        TargetType='instance'
    )

    # Create an internet facing network load balancer to listen to SSH requests (TCP port 22) and forward requests to this target group.
    iflb = elbv2.create_load_balancer(
        Name='my-internet-facing-load-balancer',
        Subnets=[subnet1.id, subnet2.id],
        SecurityGroups=[security_group.id],
        Scheme='internet-facing'
    )
    # Create a launch template with Linux server image.
    ec2_client = boto3.client('ec2')
    ec2_client.create_launch_template(
        LaunchTemplateName='my-launch-template',
        LaunchTemplateData={
            'ImageId': 'ami-0c55b159cbfafe1f0',
            'InstanceType': 't2.micro',
            'KeyName': 'my-key-pair',
            'SecurityGroupIds': [security_group.id]
        }
    )

    # Create an auto scaling group based on this launch template, and link the auto scaling group with the above network load balancer target group.
    as_client = boto3.client('autoscaling', region_name='us-east-1')
    as_group = as_client.create_auto_scaling_group(
        AutoScalingGroupName='my-auto-scaling-group',
        LaunchTemplate={
            'LaunchTemplateName': 'my-launch-template',
        },
        MinSize=1,
        MaxSize=3,
        DesiredCapacity=1,
        TargetGroupARNs=[target_group['TargetGroups'][0]['TargetGroupArn']]
    )


def assignment_7():
    # Create a DynamoDB resource
    session = boto3.Session(profile_name='iam_root')
    ddb = session.resource('dynamodb', region_name='us-east-1')

    print("Creating table")

    # Create the DynamoDB table.
    table = ddb.create_table(
        TableName='student_table',
        KeySchema=[
            {'AttributeName': 'student_id', 'KeyType': 'HASH'},  # Partition key
            {'AttributeName': 'student_name', 'KeyType': 'RANGE'}  # Sort key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'student_id', 'AttributeType': 'N'},  # N for number
            {'AttributeName': 'student_name', 'AttributeType': 'S'},  # S for string
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10
        }
    )
    # wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName='student_table')

    print("Table created")

    # Update item with new attribute
    students = [
        {"student_id": 123, "student_name": "John Doe", "student_major": "Computer Science"},
        {"student_id": 124, "student_name": "Jane Doe", "student_major": "Mathematics"},
        {"student_id": 125, "student_name": "John Smith", "student_major": "Physics"},
        {"student_id": 126, "student_name": "Jane Smith", "student_major": "Biology"},
        {"student_id": 127, "student_name": "John Brown", "student_major": "Chemistry"},
    ]

    print("Updating items")

    attribute_to_update = 'student_major'
    [
        table.update_item(
            Key={
                'student_id': student['student_id'],
                'student_name': student['student_name']
            },
            UpdateExpression='SET #attribute_to_update = :v',
            ExpressionAttributeNames={'#attribute_to_update': attribute_to_update},
            ExpressionAttributeValues={':v': student['student_major']}
        )
        for student in students
    ]

    print("Items updated")

    print("Querying and scanning items")

    # Query the table for all students with a specific major.
    response = table.query(
        KeyConditionExpression=Key('student_id').eq(123),
        # FilterExpression=Attr('student_name').begins_with('J') # filter can only contain non-primary key attributes
    )
    print(f"Query response: {response['Items']}")

    # Scan the table for all students.
    response = table.scan(
        FilterExpression=Attr('student_id').gt(124)
    )
    print(f"Scan response: {response['Items']}")


    # Delete the table
    print("Deleting table")
    table.delete()
    table.meta.client.get_waiter('table_not_exists').wait(TableName='student_table')
    print("Table deleted")


if __name__ == "__main__":
    assignment_7()
