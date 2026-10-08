import boto3
import cloud_watch


def create_sns_resource(region: str):
    return boto3.resource('sns', region_name=region)


def create_sns_topic(sns_resource):
    topic = sns_resource.create_topic(Name='alarmnotification')
    topic_arn = topic.arn

    sms_subscription = topic.subscribe(Protocol='sms',
                                       Endpoint='2016922721')
    email_subscription = topic.subscribe(Protocol='email',
                                         Endpoint='user@server.com')
    print("Check your sms or email and confirm subscription.")


def subscribe_to_topic(
        protocol,
        subscriber: list
):
    metric = cloudwatch.Metric('AWS/EC2', 'CPUUtilization')
    alarm = metric.put_alarm(
        AlarmName='my-alarm',
        AlarmDescription='Alarm when CPU utilization exceeds 90%',
        ActionsEnabled=True,
        AlarmActions=[
            'arn:aws:automate:us-east-1:ec2:stop',
            topic_arn
        ],
        Dimensions=[{'Name': 'InstanceId', 'Value': 'i-02d7782ef7a3034a9'}],
        Period=60,
        Unit='Seconds',
        EvaluationPeriods=3,
        Statistic='Average',
        Threshold=90.0,
        ComparisonOperator='GreaterThanThreshold',
    )


def publish_message(
        protocol,
        subscribers: list,
        message: str
):
    sns.publish(TopicArn=topic_arn,
                Message="message text",
                Subject="subject used in emails only")

    # Send a single SMS (no topic, no subscription needed)
    sns.publish(PhoneNumber="2016922421",
                Message="message text")


def delete_sns_topic(topic_arn):
    topic = sns.Topic(arn=topic_arn)
    topic.delete()
