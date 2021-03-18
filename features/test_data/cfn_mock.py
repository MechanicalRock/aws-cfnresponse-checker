import importlib
from datetime import datetime
from dateutil import tz

def stub(cfn_client, mock_data, last_update_date=None):
  """
  Dynamically stub a botocore cloudformation client based on mock responses in these subfolders.
  
  Arguments:
  cfn_client - the Boto [CloudFormation client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#client) to stub
  mock_data - the mock data to use.  This should match the name of a folder in this directory.
  last_update_date - (optional) date in format YYYY-MM-DD to indicate the last updated date of the mock data.  If not supplied the current datetime will be used.
  """
  mock = importlib.import_module(f'.{mock_data}.mocked_responses', 'test_data')

  creation_time = None
  if(last_update_date):
    creation_time = datetime.strptime(last_update_date, '%Y-%m-%d').astimezone(tz.tzutc())

  mock.stub(cfn_client, CreationTime=creation_time)
