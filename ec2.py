import boto3


def create_ec2_resource(region: str = None, profile: str = None, with_role: str = None):
    session = boto3.Session()

    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)

    # if with_role:
    #     sts_client = session.client('sts')
    #     role = sts_client.assume_role(RoleArn=with_role,
    #                                   RoleSessionName="vcd-dr-restore-agent")
    #     response = role['Credentials']
    #     ec2_resource = boto3.resource('ec2',
    #                                   aws_access_key_id=response['AccessKeyId'],
    #                                   aws_secret_access_key=response['SecretAccessKey'],
    #                                   aws_session_token=response['SessionToken'],
    #                                   region_name=region)

    ec2_resource = session.resource('ec2')
    return ec2_resource


def create_key_pair(ec2_resource, key_name: str, save_file_path: str = None):
    key_pair = ec2_resource.create_key_pair(KeyName=key_name)

    if save_file_path:
        with open(save_file_path, 'x') as out_file:
            out_file.write(key_pair.key_material)

    return key_pair


def launch_ec2_instance(
        actor,
        **kwargs
):
    instances = actor.create_instances(
        ImageId=kwargs.get('ImageId'),
        MinCount=kwargs.get('MinCount'),
        MaxCount=kwargs.get('MaxCount'),
        InstanceType=kwargs.get('InstanceType'),
        KeyName=kwargs.get('KeyName'),
        SecurityGroups=kwargs.get('SecurityGroups'),
        BlockDeviceMappings=kwargs.get('BlockDeviceMappings')
    )
    i = instances[0]
    print('instance', i.id, 'is created')
    i.wait_until_running()
    print('instance', i.id, 'is running')
    return i


def stop_ec2_instance(actor, instance_id: str):
    i = actor.Instance(instance_id)
    i.stop()
    i.wait_until_stopped()


def start_ec2_instance(actor, instance_id: str):
    i = actor.Instance(instance_id)
    i.start()
    i.wait_until_running()


def reboot_ec2_instance(actor, instance_id: str):
    return actor.Instance(instance_id).reboot()


def terminate_ec2_instance(actor, instance_id: str):
    i = actor.Instance(instance_id)
    i.terminate()
    i.wait_until_terminated()


def connect_ec2(instance_id: str):
    pass


def create_security_group(self):
    mysg = ec2.create_security_group(
        GroupName='http',
        Description='security group allowing http')

    mysg.authorize_ingress(
        IpProtocol='tcp',
        CidrIp='0.0.0.0/0',
        FromPort=80,
        ToPort=80)


def create_ebs_volume():
    pass


def attach_ebs_volume_to_ec2_instance():
    pass


def detach_ebs_volume_from_ec2_instance():
    pass


def delete_ebs_volume():
    pass


def create_elastic_ip_address():
    pass


def allocate_elastic_ip_address():
    pass


def release_elastic_ip_address(vpc):
    pass

# Enable detailed monitoring
# find ec2
# click actions
# monitor and troubleshoot
