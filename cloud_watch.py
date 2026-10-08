import boto3


def create_cloud_watch_resource(region=None, profile=None):
    session = boto3.Session(profile_name=profile)
    return session.resource('cloudwatch', region_name=region)


def create_alarm(cloudwatch_resource, **kwargs):
    metric = cloudwatch_resource.Metric('AWS/EC2', 'StatusCheckFailed')  # [metric for metric in metrics]
    alarm = metric.put_alarm(
        AlarmName=kwargs.get('AlarmName'),
        AlarmDescription=kwargs.get('AlarmDescription'),
        ActionsEnabled=kwargs.get('ActionsEnabled'),
        AlarmActions=kwargs.get('AlarmActions'),
        Dimensions=kwargs.get('Dimensions'),
        Period=kwargs.get('Period'),
        Unit=kwargs.get('Unit'),
        EvaluationPeriods=kwargs.get('EvaluationPeriods'),
        Statistic=kwargs.get('Statistic'),
        Threshold=kwargs.get('Threshold'),
        ComparisonOperator=kwargs.get('ComparisonOperator'),
    )
    return alarm


def delete_alarm(cloudwatch_client, alarm_name):
    return cloudwatch_client.delete_alarms(AlarmNames=[alarm_name])
