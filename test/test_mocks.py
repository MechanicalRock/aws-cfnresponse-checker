import botocore.session

from features.test_data.out_of_date_stack.mocked_responses import stub

from cfnresponsechecker.utils import paginator
from cfnresponsechecker.stacks import Stacks
import json

def test_mocks():
  """
  This test is a sanity check for the cloudformation mocked responses.
  """
  #These have to be tested in a single run
  cfn = botocore.session.get_session().create_client("cloudformation")

  stub(cfn)
  stack = Stacks(cfn)

  stack_id = "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-out-of-date-stack/31b30580-87ad-11eb-8e6c-aaaaa"

  _test_stack_summaries(stack)
  _test_stack_resources(stack, stack_id)
  _test_template_body(stack, stack_id)

    

def _test_stack_summaries(stack):
  stack_summary = stack._get_stack_summaries()

  assert len(stack_summary) == 1
  print(stack_summary)
  assert stack_summary[0]['StackName'] == 'cfnresponsechecker-out-of-date-stack'

def _test_stack_resources(stack, stack_id):
  resources  = stack._get_stack_resources(stack_id)
  assert len(resources) == 3
  print(resources)
  assert resources[0]['LogicalResourceId'] == 'CustomResourceCube'

def _test_template_body(stack, stack_id):
  template_response = stack._get_template(stack_id)
  print(template_response)
  template_body = template_response["TemplateBody"]
  assert isinstance(template_body, str)
  assert (json.loads(template_body))['Resources']['CustomResourceCube']['Type'] == 'Custom::Multiplier' 