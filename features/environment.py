import botocore.session
from cfnresponsechecker.stacks import Stacks

def before_all(context):
  create_stacks(context)
  context.cfn_response_report = {}

def create_stacks(context):
  cfn = botocore.session.get_session().create_client("cloudformation")
  context.stacks =  Stacks(cfn)
  context.cfn_client = cfn