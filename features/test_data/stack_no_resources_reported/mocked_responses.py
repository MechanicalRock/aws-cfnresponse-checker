from os import path
from botocore.stub import Stubber, ANY
from datetime import date, datetime
import yaml
import json
from cfn_flip import flip, to_yaml, to_json, load, dump_yaml, dump_json
from features.test_data.cfn_mock import CfnStub,CfnResponseError

class Stub(CfnStub):
    def stack_id(self):
        return f"arn:aws:cloudformation:{self.region}:123456789012:stack/{self.stack_name()}/31b30580-87ad-11eb-8e6c-aaaaa"

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
        # return {
        #     "StackResourceSummaries": []
        # }
        return CfnResponseError("ValidationError", "Role blah cannot be assumed", 401)

    def stack_name(self):
        return "cfnresponsechecker-stack_no_resources_reported"

    def template_file(self):
        return path.join(path.dirname(__file__), "template.yaml")