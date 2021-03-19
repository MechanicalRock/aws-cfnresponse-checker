from datetime import datetime
import deprecation

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
            print("Failed to query resources for stack: " + stack_id + ": " + str(e))

    def _get_stack_summaries(self):
        try:
            return paginator(
                self.client,
                "list_stacks",
                "StackSummaries",
                {
                    "StackStatusFilter": [
                        "CREATE_COMPLETE",
                        "UPDATE_COMPLETE",
                        "UPDATE_ROLLBACK_FAILED",
                        "UPDATE_ROLLBACK_COMPLETE",
                        "IMPORT_ROLLBACK_COMPLETE",
                        "DELETE_FAILED",
                    ]
                },
            )
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

    # TODO - naming
    def _get_stack_ids_from_lookup(self):
        stack_summaries = self._get_stack_summaries()
        if stack_summaries == None:
            return
        stack_ids = self._get_stack_ids(stack_summaries)
        return stack_ids

    def _get_problem_stacks(self,stack_ids):
        return [stack for stack in stack_ids if self.test_stack(stack)]

    @deprecation.deprecated(details="This function has been replaced by get_problem_report() and shall be removed.")
    def get_problem_stacks(self):
        stack_ids = self._get_stack_ids_from_lookup()
        return self._get_problem_stacks(stack_ids)

    def test_functions(self, stack):
        return True

    def get_problem_functions(self, stack_ids):
        # TODO - DRY with above
        todo = [stack for stack in stack_ids if self.test_functions(stack)]
        # return [
        #         {
        #             "stack": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-out-of-date-stack/31b30580-87ad-11eb-8e6c-aaaaa",
        #             "functions": [
        #                 {
        #                     "logicalId": "myCustomResourceLambda",
        #                     "code": "s3://some-deployment-bucket/uuid-here.zip",
        #                 }
        #             ],
        #         }
        #     ]
        return "not implemented"

    def get_problem_report(self):
        stack_ids = self._get_stack_ids_from_lookup()
        return {
            "stacks": self._get_problem_stacks(stack_ids),
            "functions": self.get_problem_functions(stack_ids),
        }
