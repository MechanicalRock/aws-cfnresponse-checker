from os import path
from botocore.stub import Stubber, ANY
from datetime import date, datetime
import yaml
import json
from cfn_flip import flip, to_yaml, to_json, load, dump_yaml, dump_json
from features.test_data.cfn_mock import CfnStub

class Stub(CfnStub):
    def stack_id(self):
        return f"arn:aws:cloudformation:{self.region}:012345678912:stack/{self.stack_name()}/cfnresponsechecker-out-of-date-stack-no-lambdas/9a6308d0-8ad9-11eb-b83c-aaaaa"

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
                "LogicalResourceId": "MySNSTopic",
                "PhysicalResourceId": "cfnresponsechecker-out-of-date-stack-no-lambdas-MySNSTopic-17LGIIW1HQSCK",
                "ResourceType": "AWS::SNS::Topic",
                "LastUpdatedTimestamp": self.CreationTime,
                "ResourceStatus": "CREATE_COMPLETE",
                "DriftInformation": {
                    "StackResourceDriftStatus": "NOT_CHECKED"
                }
            }
            ]
        }

    def stack_name(self):
        return "cfnresponsechecker-out-of-date-stack_no_lambdas"

    def template_file(self):
        return path.join(path.dirname(__file__), "template.yaml")