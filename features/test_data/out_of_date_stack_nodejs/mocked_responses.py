from os import path
from botocore.stub import Stubber, ANY
from datetime import date, datetime
import yaml
import json
from cfn_flip import flip, to_yaml, to_json, load, dump_json, dump_yaml
from features.test_data.cfn_mock import CfnStub


class Stub(CfnStub):
    def stack_id(self):
        return f"arn:aws:cloudformation:{self.region}:123456789012:stack/{self.stack_name()}/31b30580-87ad-11eb-8e6c-aaaab"

    def stack_summaries_response(self):
        return {
            "StackSummaries": [
                {
                    "StackId": self.stack_id(),
                    "StackName": self.stack_name(),
                    "CreationTime": self.CreationTime,
                    "LastUpdatedTime": self.CreationTime,
                    "StackStatus": "CREATE_COMPLETE",
                    "DriftInformation": {"StackDriftStatus": "NOT_CHECKED"},
                },
            ]
        }

    def stack_resource_summaries(self):
        return {
            "StackResourceSummaries": [
                {
                    "LogicalResourceId": "CustomResourceCube",
                    "PhysicalResourceId": "CustomResourcePhysicalID",
                    "ResourceType": "Custom::Multiplier",
                    "LastUpdatedTimestamp": self.CreationTime,
                    "ResourceStatus": "CREATE_COMPLETE",
                    "DriftInformation": {"StackResourceDriftStatus": "NOT_CHECKED"},
                },
                {
                    "LogicalResourceId": "MyCustomResourceLambda",
                    "PhysicalResourceId": "cfnresponsechecker-out-of-d-MyCustomResourceLambda-1KY0K077Z8AAB",
                    "ResourceType": "AWS::Lambda::Function",
                    "LastUpdatedTimestamp": self.CreationTime,
                    "ResourceStatus": "CREATE_COMPLETE",
                    "DriftInformation": {"StackResourceDriftStatus": "NOT_CHECKED"},
                },
                {
                    "LogicalResourceId": "MyCustomResourceLambdaExecutionRole",
                    "PhysicalResourceId": "cfnresponsechecker-out-of-MyCustomResourceLambdaEx-9T28G06490AC",
                    "ResourceType": "AWS::IAM::Role",
                    "LastUpdatedTimestamp": self.CreationTime,
                    "ResourceStatus": "CREATE_COMPLETE",
                    "DriftInformation": {"StackResourceDriftStatus": "NOT_CHECKED"},
                },
            ]
        }

    def stack_name(self):
        return "cfnresponsechecker-out_of_date_stack_nodejs"

    def template_file(self):
        return path.join(path.dirname(__file__), "template.yaml")
