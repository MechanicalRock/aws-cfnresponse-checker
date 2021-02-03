import argparse
import json

import boto3
import botocore
from datetime import datetime, tzinfo
from dateutil import tz
from botocore.config import Config

OLD_RESOURCE_DATETIME = datetime(2021, 1, 1, tzinfo=tz.tzutc())

parser = argparse.ArgumentParser()
parser.add_argument("--region", action="store", type=str, required=True)

args = parser.parse_args()
region = args.region

my_config = Config(region_name=region)
client = boto3.client("cloudformation", config=my_config)


def get_stacks(stack_summaries):
    return [stack.get("StackId") for stack in stack_summaries]


def has_custom_resource(resource):
    return (
        "::CustomResource" in resource["ResourceType"]
        or "Custom::" in resource["ResourceType"]
    )


def get_template(stack_id):
    return client.get_template(StackName=stack_id)


def old_resource(resource):
    return resource["LastUpdatedTimestamp"] <= OLD_RESOURCE_DATETIME


try:
    stack_summaries = client.list_stacks().get("StackSummaries")
except botocore.exceptions.ClientError as e:
    print(e)
    exit()

stack_ids = get_stacks(stack_summaries)


for stack_id in stack_ids:
    stack_resources = client.list_stack_resources(StackName=stack_id).get(
        "StackResourceSummaries"
    )

    old_stack_resources = [
        resource for resource in stack_resources if old_resource(resource)
    ]

    templates = [
        get_template(stack_id)["TemplateBody"]
        for resource in old_stack_resources
        if has_custom_resource(resource)
    ]

    for template in templates:
        if "python" in template:
            print(f"{stack_id}")

# if __name__ == "__main__":
#     pass