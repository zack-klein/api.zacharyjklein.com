import boto3
import os
import requests

from datetime import datetime, date, timedelta


SLACK_URL = os.environ.get("WHATS_MY_BILL_WHOOK")


def get_bill(start, end):
    """
    Get the amount of the bill!

    :param str start: Start date (%Y-%m-%d)
    :param str end: End date (%Y-%m-%d)
    :return str: Bill amount.
    """
    client = boto3.client("ce", region_name="us-east-1")
    response = client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["AmortizedCost"],
    )
    amount = response["ResultsByTime"][0]["Total"]["AmortizedCost"]["Amount"]
    return amount


def get_this_month():
    """
    Get this month's AWS bill. If it's the first day of the month, get last
    month's bill.
    """
    today = date.today()
    first_day = today.replace(day=1)

    if today == first_day:
        yesterday = today - timedelta(days=1)
        first_day = yesterday.replace(day=1)
        start = first_day.strftime("%Y-%m-%d")
        end = yesterday.strftime("%Y-%m-%d")
    else:
        start = first_day.strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")

    return get_bill(start, end), (start, end)


def post_bill_slack():
    """
    Post the amount of last month's bill to Slack.
    """
    amount, dates = get_this_month()
    text = f"""
    Hello! AWS bill from {dates[0]} -> {dates[1]} = ${round(float(amount), 2)}
    """
    msg = {
        "channel": "#alerts",
        "attachments": [
            {
                "title": text,
                "footer": "AWS",
                "color": "#2eb886",
                "footer_icon": (
                    "https://cdn.clipart.email/"
                    "be911c4bc46159c9d2bd76a10526955"
                    "e_difference-between-azure-and-"
                    "aws-difference-between_600-600.png"
                ),
                "ts": datetime.timestamp(datetime.now()),
            }
        ],
    }
    requests.post(SLACK_URL, json=msg)
    return "You just told Zack how much his bill is!"
