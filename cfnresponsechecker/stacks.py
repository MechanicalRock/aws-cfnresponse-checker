from datetime import datetime

import botocore
from dateutil import tz

from cfnresponsechecker.utils import paginator

OLD_RESOURCE_DATETIME = datetime(2020, 11, 23, tzinfo=tz.tzutc())


class Stacks:
    def __init__(self, client, old_resource_datetime=OLD_RESOURCE_DATETIME):
        self.client = client
        self.old_resource_datetime = old_resource_datetime

    def _get_stack_ids(self, stack_summaries):
        return [
            stack["StackId"]
            for stack in stack_summaries
            if stack["StackStatus"] != "DELETE_COMPLETE"
        ]

    def _has_custom_resource(self, resource):
        return (
            "::CustomResource" in resource["ResourceType"]
            or "Custom::" in resource["ResourceType"]
        )

    def _get_template(self, stack_id):
        return self.client.get_template(StackName=stack_id)

    def _old_resource(self, resource):
        old = resource["LastUpdatedTimestamp"] <= self.old_resource_datetime
        deleted = resource["ResourceStatus"] == "DELETE_COMPLETE"
        function = resource["ResourceType"] == "AWS::Lambda::Function"
        return old and function and not deleted

    def _get_stack_resources(self, stack_id):
        try:
            return paginator(
                self.client,
                "list_stack_resources",
                "StackResourceSummaries",
                {"StackName": stack_id},
            )
        except botocore.exceptions.ClientError as e:
            print(e)

    def _get_stack_summaries(self):
        try:
            return paginator(self.client, "list_stacks", "StackSummaries")
        except botocore.exceptions.ClientError as e:
            print(e)

    def test_stack(self, stack_id):
        stack_resources = self._get_stack_resources(stack_id)
        if stack_resources == None:
            return

        custom_resources = [
            resource
            for resource in stack_resources
            if self._has_custom_resource(resource)
        ]
        if len(custom_resources) == 0:
            return False

        old_stack_resources = [
            resource for resource in stack_resources if self._old_resource(resource)
        ]
        templates = [
            self._get_template(stack_id)["TemplateBody"]
            for resource in old_stack_resources
        ]

        for template in templates:
            if "python" in template:
                return True
        return False

    def get_problem_stacks(self):
        stack_summaries = self._get_stack_summaries()
        if stack_summaries == None:
            return
        stack_ids = self._get_stack_ids(stack_summaries)
        return [stack for stack in stack_ids if self.test_stack(stack)]
