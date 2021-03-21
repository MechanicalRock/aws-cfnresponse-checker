from datetime import datetime
import deprecation
import logging

import botocore
from dateutil import tz

from cfnresponsechecker.utils import paginator
import json

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

    def _is_lambda_function(self, resource):
        deleted = resource["ResourceStatus"] == "DELETE_COMPLETE"
        function = resource["ResourceType"] == "AWS::Lambda::Function"
        return function and not deleted

    def _out_of_date_lambda_function(self, resource):
        old = resource["LastUpdatedTimestamp"] <= self.old_resource_datetime
        return old and self._is_lambda_function(resource)

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

    def get_resources_for_stack_ids(self, stack_ids):
        resources = [
            {"stackId": stack_id, "resources": self._get_stack_resources(stack_id)}
            for stack_id in stack_ids
        ]
        return resources

    def get_templates_for_stack_ids(self, stack_ids):
        templates = [
            {"stackId": stack_id, "template": self._get_template(stack_id)}
            for stack_id in stack_ids
        ]
        return templates

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

    def _has_outdated_custom_resources(self,stack_info):
        stack_id = stack_info["stackId"]
        stack_resources = stack_info["resources"]
        # backward compatability
        template_body = json.dumps(stack_info["templateBody"])

        if stack_resources == None:
            logging.debug(f"No resources found for {stack_id}")
            return 

        custom_resources = [
            resource
            for resource in stack_resources
            if self._has_custom_resource(resource)
        ]
        if len(custom_resources) == 0:
            return False

        old_stack_resources = [
            resource for resource in stack_resources if self._out_of_date_lambda_function(resource)
        ]

        if len(old_stack_resources) == 0:
            return False

        # is python mentioned at all in the template
        # This may return false positives
        return "python" in template_body
        # templates = [
        #     self._get_template(stack_id)["TemplateBody"]
        #     for resource in old_stack_resources
        # ]

        # for template in templates:
        #     if "python" in template:
        #         return True
        # return False

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
            resource for resource in stack_resources if self._out_of_date_lambda_function(resource)
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

    def _get_problem_stacks(self, stack_ids):
        return [stack for stack in stack_ids if self.test_stack(stack)]

    def _get_problem_stacks_new(self,stack_details):
        return [stack_info["stackId"] for stack_info in stack_details if(self._has_outdated_custom_resources(stack_info))]

    @deprecation.deprecated(
        details="This function has been replaced by get_problem_report() and shall be removed."
    )
    def get_problem_stacks(self):
        stack_ids = self._get_stack_ids_from_lookup()
        return self._get_problem_stacks(stack_ids)

    def test_functions(self, stack_info):
        stack_id = stack_info["stackId"]
        stack_resources = stack_info["resources"]
        template_body = stack_info["templateBody"]

        if stack_resources == None:
            logging.debug(f"No resources found for {stack_id}")
            return 

        custom_resources = [
            resource
            for resource in stack_resources
            if self._has_custom_resource(resource)
        ]
        if len(custom_resources) == 0:
            return False

        old_stack_resources = [
            resource for resource in stack_resources if self._is_lambda_function(resource)
        ]

        if len(old_stack_resources) == 0:
            return False

        # is python mentioned at all in the template
        # This may return false positives
        return "python" in template_body

    def _get_stack_info(self):
        # Build structure like
        # [
        #   {
        #     "stackId": "blah",
        #     "resources": [...]
        #     "templateBody": "..."
        #   },
        # ...]

        stack_ids = self._get_stack_ids_from_lookup()
        stacks_with_resources = self.get_resources_for_stack_ids(stack_ids)
        stacks_with_templates = self.get_templates_for_stack_ids(stack_ids)

        combined = list(zip(stack_ids, stacks_with_resources, stacks_with_templates))

        cleaned = [
            {
                "stackId": stack_id,
                "resources": resources['resources'],
                "templateBody": json.loads(template['template']['TemplateBody'])
            }
            for (stack_id, resources, template) in combined
        ]

        return cleaned

    def _lambda_code_for_resource(self,lambda_code_resource):
        """
        Parameters:
        @lambda_code_resource - The Code property for an AWS::Lambda::Function
        @see https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html
        """
        if(lambda_code_resource["ZipFile"]):
            return "<inline>"
        if(lambda_code_resource["ImageUri"]):
            return lambda_code_resource["ImageUri"]
        if(lambda_code_resource["S3Bucket"]):
            bucket = lambda_code_resource["S3Bucket"]
            key = lambda_code_resource['S3Key']
            return f's3://{bucket}/{key}'

    def _filter_for_lambda_function(self,stack_info):
        # stack_id = stack_info["stackId"]
        stack_resources = stack_info["resources"]
        template_body = stack_info["templateBody"]

        lambda_functions = [resource for resource in stack_resources if(self._is_lambda_function(resource))]

        logical_id_of = lambda resource: resource["LogicalResourceId"]
        code_for_lambda = lambda resource_id: template_body["Resources"][resource_id]["Properties"]["Code"]
        is_python_lambda = lambda resource_id: 'python' in template_body["Resources"][resource_id]["Properties"]["Runtime"]

        return [{
            "logicalId": logical_id_of(lambda_resource),
            "code": self._lambda_code_for_resource(code_for_lambda(logical_id_of(lambda_resource)))
        } for lambda_resource in lambda_functions if is_python_lambda(logical_id_of(lambda_resource))
        ]

    # def _has_lambda_function(self, stack_details):


    def get_problem_functions(self, stack_details):
        
        unfiltered_stacks_with_functions =  [{
            "stack": stack_info["stackId"],
            "functions": self._filter_for_lambda_function(stack_info)
        } for stack_info in stack_details]
        # filter for lambda functions

        return [stack for stack in unfiltered_stacks_with_functions if len(stack["functions"]) > 0 ]

    def get_problem_report(self):
        stack_info = self._get_stack_info()
        # stack_ids = self._get_stack_ids_from_lookup()
        return {
            "stacks": self._get_problem_stacks_new(stack_info),
            "functions": self.get_problem_functions(stack_info),
        }
