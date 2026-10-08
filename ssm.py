import boto3


def create_ssm_client(region, with_role):
    session = boto3.Session(region_name=region) if region else boto3.Session()

    if with_role:
        sts_client = session.client('sts')
        role = sts_client.assume_role(RoleArn=with_role,
                                      RoleSessionName="vcd-dr-restore-agent")
        response = role['Credentials']
        ssm_client = boto3.client('ssm',
                                  aws_access_key_id=response['AccessKeyId'],
                                  aws_secret_access_key=response['SecretAccessKey'],
                                  aws_session_token=response['SessionToken'])
    else:
        ssm_client = boto3.client('ssm')
    return ssm_client