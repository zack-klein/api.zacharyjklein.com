import boto3


def fetch_arn(topic_name):
    """Get the ARN of a topic from the name.
    """
    return get_topics_d().get(topic_name)


def get_topics_d(provided_prefix=False):
    """Get all available topics: {name:arn}.
    """
    sns = boto3.client("sns")
    all_topics = sns.list_topics()["Topics"]
    prefix = None if provided_prefix is False else provided_prefix
    topics = {}
    for topic in all_topics:
        arn = topic["TopicArn"]
        name = arn.split(":")[5]
        if prefix is None:
            topics[name] = arn
        else:
            if name[: len(prefix)] == prefix:
                topics[name] = arn
    return topics


def get_topics(prefix=False):
    """Get one topic.
    """
    return list(get_topics_d(provided_prefix=prefix).keys())


def get_topic(topic):
    """Get one topic.
    """
    return get_topics_d().get(topic)


def create_topic(topic_name, tags={}):
    """Creates a topic, returns the ARN.
    """
    sns = boto3.client("sns")
    sns.create_topic(Name=topic_name, Attributes={}, Tags=[tags])
    topic = get_topic(topic_name)
    return topic


def delete_topic(topic_name):
    """Delete a topic.
    """
    sns = boto3.client("sns")
    arn = fetch_arn(topic_name)
    sns.delete_topic(TopicArn=arn)
    topic = get_topic(topic_name)
    return topic


def publish(topic_name, message):
    """Publish a message to a topic.
    """
    sns = boto3.client("sns")
    arn = fetch_arn(topic_name)
    response = sns.publish(TopicArn=arn, Message=message)
    return response


def subscribe(topic_name, protocol, endpoint):
    """Subscribe contact to a topic.
    """
    sns = boto3.client("sns")
    arn = fetch_arn(topic_name)
    response = sns.subscribe(
        TopicArn=arn,
        Protocol=protocol,
        Endpoint=endpoint,
        ReturnSubscriptionArn=True,
    )
    return response["SubscriptionArn"]


def unsubscribe(arn):
    """Delete a subscription.
    """
    sns = boto3.client("sns")
    response = sns.unsubscribe(SubscriptionArn=arn)
    return response
