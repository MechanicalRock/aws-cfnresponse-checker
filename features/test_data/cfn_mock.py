import importlib
from datetime import datetime
from dateutil import tz
from botocore.stub import Stubber, ANY
from datetime import date, datetime
from cfn_flip import flip, to_yaml, to_json, load, dump_json, dump_yaml


from abc import ABC, abstractmethod


class CfnStub(ABC):
    def __init__(self):
      pass 

    def init(
        self,
        stubber,
        template_type="json",
        region="ap-southeast-2",
        CreationTime=datetime.combine(date.today(), datetime.min.time()),
    ):
        # Set these values first - there is a dependency in the abstract implementations
        self.region = region
        self.CreationTime = CreationTime

        stack_id = self.stack_id()

        # https://github.com/boto/botocore/issues/2069
        # Stubber expects queries to be made in a specific order
        # This means mocked responses can only be used for the Stacks class as a whole, and not any more granular.
        self._stub_list_stacks_response(stubber, stack_id, CreationTime)
        self._stub_list_stack_resources_response(stubber, stack_id, CreationTime)
        self._stub_get_template(stubber, stack_id, template_type=template_type)

    def _stub_list_stacks_response(self, stubber, stack_id, CreationTime):
        stack_name = self.stack_name()

        mock_response = self.stack_summaries_response()
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

    def _stub_list_stack_resources_response(self, stubber, stack_id, CreationTime):
        mock_response = self.stack_resource_summaries()

        expected_params = {"StackName": self.stack_id()}
        stubber.add_response("list_stack_resources", mock_response, expected_params)

    def _stub_get_template(self, stubber, stack_id, template_type="json"):
        with open(self.template_file(), "r") as template_file:
            template_body_raw, _ = load(template_file.read())
        template_file.close()
        if template_type == "yaml":
            template_body = dump_yaml(template_body_raw)
        else:
            template_body = dump_json(template_body_raw)

        expected_params = {"StackName": self.stack_id()}
        mock_response = {
            "TemplateBody": template_body,
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

    @abstractmethod
    def stack_id(self):
        return None

    @abstractmethod
    def stack_summaries_response(self):
        return None

    @abstractmethod
    def stack_resource_summaries(self):
        return None

    @abstractmethod
    def stack_name(self):
        return None

    def template_file(self):
      return None


def stub(stubber, mock_data, template_type="json", last_update_date=None):
    """
    Dynamically stub a botocore cloudformation client based on mock responses in these subfolders.

    Arguments:
    cfn_client - the Boto [CloudFormation client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#client) to stub
    mock_data - the mock data to use.  This should match the name of a folder in this directory.
    last_update_date - (optional) date in format YYYY-MM-DD to indicate the last updated date of the mock data.  If not supplied the current datetime will be used.
    """
    mock = importlib.import_module(f".{mock_data}.mocked_responses", "test_data")

    creation_time = None
    if last_update_date:
        creation_time = datetime.strptime(last_update_date, "%Y-%m-%d").astimezone(
            tz.tzutc()
        )

    stub = mock.Stub()
    stub.init(stubber, template_type = template_type, CreationTime = last_update_date)
