import argparse
import json

import boto3
import botocore
from datetime import datetime, tzinfo
from dateutil import tz
from botocore.config import Config

OLD_RESOURCE_DATETIME = datetime(2021, 1, 1, tzinfo=tz.tzutc())


class Stacks:
    def __init__(self, client, old_resource_datetime=OLD_RESOURCE_DATETIME):
        self.client = client
        self.old_resource_datetime = old_resource_datetime

    def _get_stacks(self, stack_summaries):
        return [stack.get("StackId") for stack in stack_summaries]

    def _has_custom_resource(self, resource):
        return (
            "::CustomResource" in resource["ResourceType"]
            or "Custom::" in resource["ResourceType"]
        )

    def _get_template(self, stack_id):
        return self.client.get_template(StackName=stack_id)

    def _old_resource(self, resource):
        return resource["LastUpdatedTimestamp"] <= self.old_resource_datetime

    def get_stack_resources(self):
        try:
            stack_summaries = self.client.list_stacks().get("StackSummaries")
        except botocore.exceptions.ClientError as e:
            print(e)
            return

        stack_ids = self._get_stacks(stack_summaries)

        for stack_id in stack_ids:
            stack_resources = self.client.list_stack_resources(StackName=stack_id).get(
                "StackResourceSummaries"
            )

            old_stack_resources = [
                resource for resource in stack_resources if self._old_resource(resource)
            ]

            templates = [
                self._get_template(stack_id)["TemplateBody"]
                for resource in old_stack_resources
                if self._has_custom_resource(resource)
            ]

            for template in templates:
                if "python" in template:
                    print(f"{stack_id}")
