import collections
import logging
import botocore

from datetime import datetime
from dateutil import tz
from cfn_flip import to_json, load, dump_json

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

    def _adapt_template(self, stack_id):
        """
        Adapter: query AWS for the template body for the given stack.
        @returns The parsed template body as a dict ({key:value})
        """
        # https://github.com/boto/botocore/issues/1889
        # Ensure that the TemplateBody is parsed.
        # Difference in behaviour between YAML and JSON :(
        template_response = self.client.get_template(StackName=stack_id)
        try:
            parsed_template, _ = load(template_response["TemplateBody"])
            template_response["TemplateBody"] = parsed_template
        except TypeError as _:
            logging.debug(
                "Ignoring TypeError parsing TemplateBody - assuming it is already parsed JSON"
            )
        return template_response

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
            return []

    def get_resources_for_stack_ids(self, stack_ids):
        resources = [
            {"stackId": stack_id, "resources": self._get_stack_resources(stack_id)}
            for stack_id in stack_ids
        ]
        return resources

    def _adapt_templates_for_stack_ids(self, stack_ids):
        """
        Adapter: query AWS for templates for the given stack ids
        """
        templates = [
            {"stackId": stack_id, "template": self._adapt_template(stack_id)}
            for stack_id in stack_ids
        ]
        return templates

    def _adapt_stack_summaries_from_aws(self):
        """
        Adapter: query stack summaries from AWS
        """
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

    def _adapt_stack_ids_from_aws(self):
        """
        Adapter: query AWS for active Stacks
        """
        stack_summaries = self._adapt_stack_summaries_from_aws()
        if stack_summaries == None:
            return
        stack_ids = self._get_stack_ids(stack_summaries)
        return stack_ids

    # def test_functions(self, stack_info):
    #     stack_id = stack_info["stackId"]
    #     stack_resources = stack_info["resources"]
    #     template_body = stack_info["templateBody"]

    #     if stack_resources == None:
    #         logging.debug(f"No resources found for {stack_id}")
    #         return

    #     custom_resources = [
    #         resource
    #         for resource in stack_resources
    #         if self._has_custom_resource(resource)
    #     ]
    #     if len(custom_resources) == 0:
    #         return False

    #     old_stack_resources = [
    #         resource
    #         for resource in stack_resources
    #         if self._is_lambda_function(resource)
    #     ]

    #     if len(old_stack_resources) == 0:
    #         return False

    #     # is python mentioned at all in the template
    #     # This may return false positives
    #     return "python" in template_body

    def _port_stack_info_from_aws(self):
        """
        Port: Return stack information from the running AWS environment for all active stacks.

        This could be refactored into a true Port/Adapter pattern using classes.
        The current method calls would become implementation detail of the AWS Adapter

        returns a structure like:
        [
          {
            "stackId": "id of an active stack",
            "resources": [logical resources for the stack]
            "templateBody": "JSON structure of the template used to create the stack"
          },
        ...]
        """

        stack_ids = self._adapt_stack_ids_from_aws()
        stacks_with_resources = self.get_resources_for_stack_ids(stack_ids)
        stacks_with_templates = self._adapt_templates_for_stack_ids(stack_ids)

        combined = list(zip(stack_ids, stacks_with_resources, stacks_with_templates))

        cleaned = [
            {
                "stackId": stack_id,
                "resources": resources["resources"],
                "templateBody": template["template"]["TemplateBody"],
            }
            for (stack_id, resources, template) in combined
        ]

        return cleaned

    def _lambda_code_for_resource(self, lambda_code_resource):
        """
        Parameters:
        @lambda_code_resource - The Code property for an AWS::Lambda::Function
        @see https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html
        """
        if "ZipFile" in lambda_code_resource:
            return "<inline>"
        if "ImageUri" in lambda_code_resource:
            return lambda_code_resource["ImageUri"]
        if "S3Bucket" in lambda_code_resource:
            bucket = lambda_code_resource["S3Bucket"]
            key = lambda_code_resource["S3Key"]
            return f"s3://{bucket}/{key}"

    def _get_external_lambdas(self, stack_resources, template_body):
        external_lambdas = []
        template_resources = template_body["Resources"]
        for resource in stack_resources:
            resource_id = resource["LogicalResourceId"]
            
            if not "Properties" in template_resources[resource_id]:
                continue
            if not "ServiceToken" in template_resources[resource_id]["Properties"]:
                continue
            
            if ":lambda:" in template_resources[resource_id]["Properties"]["ServiceToken"]:
                external_lambdas.append({"logicalId":resource_id, "code": "external"})
        
        return external_lambdas

    def _filter_for_lambda_function(self, stack_info):
        stack_resources = stack_info["resources"]
        template_body = stack_info["templateBody"]

        external_lambdas = self._get_external_lambdas(stack_resources, template_body)
        lambda_functions = [
            resource
            for resource in stack_resources
            if (self._is_lambda_function(resource))
        ]

        logical_id_of = lambda resource: resource["LogicalResourceId"]
        code_for_lambda = lambda resource_id: template_body["Resources"][resource_id][
            "Properties"
        ]["Code"]
        is_python_lambda = (
            lambda resource_id: "python"
            in template_body["Resources"][resource_id]["Properties"]["Runtime"]
        )

        internal_lambdas = [
            {
                "logicalId": logical_id_of(lambda_resource),
                "code": self._lambda_code_for_resource(
                    code_for_lambda(logical_id_of(lambda_resource))
                ),
            }
            for lambda_resource in lambda_functions
            if is_python_lambda(logical_id_of(lambda_resource))
        ]
        return internal_lambdas + external_lambdas

    def _template_body_has_inline_vendored_usage(self, template_body_dict):
        template_body = dump_json(template_body_dict)
        return "botocore.vendored" in template_body

    def create_function_report(self, stack_details):

        unfiltered_stacks_with_functions = [
            {
                "stack": stack_info["stackId"],
                "functions": self._filter_for_lambda_function(stack_info),
            }
            for stack_info in stack_details
        ]
        return [
            stack
            for stack in unfiltered_stacks_with_functions
            if len(stack["functions"]) > 0
        ]

    def create_inline_vendored_usage_report(self, stack_details):

        return [
            stack_info["stackId"]
            for stack_info in stack_details
            if self._template_body_has_inline_vendored_usage(stack_info["templateBody"])
        ]

    def _stack_has_out_of_date_lambdas(self,function_report_row, stack_details):
        if len(function_report_row["functions"]) == 0:
            return False

        stack_id = function_report_row["stack"]
        stack_resources = [stack_info["resources"] for stack_info in stack_details if stack_info["stackId"] == stack_id][0]
        if stack_resources == None:
            logging.debug(f"No resources found for {stack_id}")
            return False

        # custom_resources = [
        #     resource
        #     for resource in stack_resources
        #     if self._has_custom_resource(resource)
        # ]
        # if len(custom_resources) == 0:
        #     return False

        old_stack_resources = [
            resource
            for resource in stack_resources
            if self._out_of_date_lambda_function(resource)]

        return len(old_stack_resources) > 0

    def _stacks_with_out_of_date_lambdas(self, function_report, stack_details):
        return [stack["stack"] for stack in function_report if self._stack_has_out_of_date_lambdas(stack, stack_details)]
        # stack_resources = stack_info["resources"]
        # template_body = stack_info["templateBody"]

        # lambda_functions = [
        #     resource
        #     for resource in stack_resources
        #     if (self._is_lambda_function(resource))
        # ]


        # stack_ids = collections.OrderedDict(
        #     {report["stack"]: "" for report in function_report}
        # ).keys()
        # # _out_of_date_lambda_function
        # return [stack_id for stack_id in stack_ids]

    def get_problem_report(self):
        stack_info = self._port_stack_info_from_aws()
        function_report = self.create_function_report(stack_info)
        # maintain an ordered list of stack IDs for consistency
        
        stack_report = self._stacks_with_out_of_date_lambdas(function_report, stack_info)

        inline_vendored_usage = self.create_inline_vendored_usage_report(stack_info)
        return {
            "stacks": stack_report,
            "function_report": function_report,
            "inline_vendored_usage": inline_vendored_usage,
        }
