import botocore.session
from cfnresponsechecker.stacks import Stacks
from botocore.stub import Stubber, ANY


def before_all(context):
  create_stacks(context)
  context.cfn_response_report = {}
  context.cfn_pretty_problem_report = {}

def create_stacks(context):
  cfn = botocore.session.get_session().create_client("cloudformation")
  context.stacks =  Stacks(cfn)
  context.cfn_client = cfn
  stubber = Stubber(cfn)
  context.stubber = stubber
  stubber.activate()

def after_all(context):
  context.stubber.deactivate()