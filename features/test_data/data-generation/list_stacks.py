import json

import pytest
from cfnresponsechecker.utils import paginator
from cfnresponsechecker.stacks import Stacks

import boto3
from botocore.config import Config

def main():

    config = Config(region_name='ap-southeast-2')
    client = boto3.client("cloudformation", config=config)
    result = paginator(client, "list_stacks", "StackSummaries", {"StackStatusFilter": [
        'CREATE_COMPLETE','UPDATE_COMPLETE', 'UPDATE_ROLLBACK_FAILED','UPDATE_ROLLBACK_COMPLETE','IMPORT_ROLLBACK_COMPLETE', 'DELETE_FAILED'
    ]})
    # result = paginator(client, "list_stacks", "StackSummaries")


    stack = Stacks(client)

    stack_summaries = stack._get_stack_summaries()
    sample_stack = [x for x in stack_summaries if x['StackName'] == 'cfnresponsechecker-out-of-date-stack'][0]

    print("list_stacks response:")
    print(json.dumps([sample_stack], default=str))
    print('=====================')

    stack_resources = stack._get_stack_resources(sample_stack['StackId'])
    print("list_stack_resources response:")
    print(json.dumps(stack_resources, default=str))
    print('=====================')

    template = stack._get_template(sample_stack['StackId'])
    print("stack_template response:")
    print(json.dumps(template, default=str))
    print('=====================')
if __name__ == "__main__":
    main()