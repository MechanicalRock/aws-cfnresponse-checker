import botocore
from datetime import datetime
from dateutil import tz

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
            paginator = self.client.get_paginator("list_stack_resources")
            pages = paginator.paginate(StackName=stack_id)
            return [
                item for sublist in pages for item in sublist["StackResourceSummaries"]
            ]
        except botocore.exceptions.ClientError as e:
            print(e)
            return

    def _get_stack_summaries(self):
        try:
            paginator = self.client.get_paginator("list_stacks")
            pages = paginator.paginate()
            return [item for sublist in pages for item in sublist["StackSummaries"]]
        except botocore.exceptions.ClientError as e:
            print(e)
            return

    def test_stack(self, stack_id):
        stack_resources = self._get_stack_resources(stack_id)
        if stack_resources == None:
            return

        custom_resources = [
            resource
            for resource in stack_resources
            if self._has_custom_resource(resource)
        ]
        old_stack_resources = [
            resource for resource in custom_resources if self._old_resource(resource)
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
