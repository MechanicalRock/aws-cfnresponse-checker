from os import path
from botocore.stub import Stubber, ANY
from datetime import date, datetime
import yaml
import json
from cfn_flip import flip, to_yaml, to_json


def stub(
    stubber,
    region="ap-southeast-2",
    CreationTime=datetime.combine(date.today(), datetime.min.time()),
):
    # stubber = Stubber(cfn_client)

    stack_id = f"arn:aws:cloudformation:{region}:123456789012:stack/cfnresponsechecker-out-of-date-stack-nodejs/31b30580-87ad-11eb-8e6c-aaaab"

    # https://github.com/boto/botocore/issues/2069
    # Stubber expects queries to be made in a specific order
    # This means mocked responses can only be used for the Stacks class as a whole, and not any more granular.
    _stub_list_stacks_response(stubber, stack_id, CreationTime)
    _stub_list_stack_resources_response(stubber, stack_id, CreationTime)
    _stub_get_template(stubber, stack_id)
    # stubber.activate()
    pass


def _stub_list_stacks_response(stubber, stack_id, CreationTime):
    stack_name = "cfnresponsechecker-out-of-date-stack-nodejs"

    mock_response = {
        "StackSummaries": [
            {
                "StackId": stack_id,
                "StackName": stack_name,
                "CreationTime": CreationTime,
                "LastUpdatedTime": CreationTime,
                "StackStatus": "CREATE_COMPLETE",
                "DriftInformation": {"StackDriftStatus": "NOT_CHECKED"},
            },
        ]
    }
    # Brittle - this is dependent on the call from within utils
    expected_params = {
        "StackStatusFilter": [
            "CREATE_COMPLETE",
            "UPDATE_COMPLETE",
            "UPDATE_ROLLBACK_FAILED",
            "UPDATE_ROLLBACK_COMPLETE",
            "IMPORT_ROLLBACK_COMPLETE",
            "DELETE_FAILED",
        ]
    }
    stubber.add_response("list_stacks", mock_response, expected_params)


def _stub_list_stack_resources_response(stubber, stack_id, CreationTime):
    mock_response = {
        "StackResourceSummaries": [
            {
                "LogicalResourceId": "CustomResourceCube",
                "PhysicalResourceId": "CustomResourcePhysicalID",
                "ResourceType": "Custom::Multiplier",
                "LastUpdatedTimestamp": CreationTime,
                "ResourceStatus": "CREATE_COMPLETE",
                "DriftInformation": {"StackResourceDriftStatus": "NOT_CHECKED"},
            },
            {
                "LogicalResourceId": "MyCustomResourceLambda",
                "PhysicalResourceId": "cfnresponsechecker-out-of-d-MyCustomResourceLambda-1KY0K077Z8AAB",
                "ResourceType": "AWS::Lambda::Function",
                "LastUpdatedTimestamp": CreationTime,
                "ResourceStatus": "CREATE_COMPLETE",
                "DriftInformation": {"StackResourceDriftStatus": "NOT_CHECKED"},
            },
            {
                "LogicalResourceId": "MyCustomResourceLambdaExecutionRole",
                "PhysicalResourceId": "cfnresponsechecker-out-of-MyCustomResourceLambdaEx-9T28G06490AC",
                "ResourceType": "AWS::IAM::Role",
                "LastUpdatedTimestamp": CreationTime,
                "ResourceStatus": "CREATE_COMPLETE",
                "DriftInformation": {"StackResourceDriftStatus": "NOT_CHECKED"},
            },
        ]
    }

    expected_params = {"StackName": stack_id}
    stubber.add_response("list_stack_resources", mock_response, expected_params)


def _stub_get_template(stubber, stack_id):
    with open(path.join(path.dirname(__file__),"template.yaml"), "r") as template_file:
        template_body = to_json(template_file.read())
    template_file.close()
    # template_body_json = json.dumps(template_body)
    template_body_json = template_body


    expected_params = {"StackName": stack_id}
    mock_response = {
        "TemplateBody": json.dumps(template_body_json),
        "StagesAvailable": ["Original", "Processed"],
        "ResponseMetadata": {
            "RequestId": "a31f5380-73ad-4f7f-a440-aaaaaaaaab",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "x-amzn-requestid": "a31f5380-73ad-4f7f-a440-aaaaaaaaab",
                "content-type": "text/xml",
                "content-length": "1798",
                "date": "Thu, 18 Mar 2021 09:36:17 GMT",
            },
            "RetryAttempts": 0,
        },
    }
    stubber.add_response("get_template", mock_response, expected_params)
