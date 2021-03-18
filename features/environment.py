import botocore.session
from cfnresponsechecker.stacks import Stacks

from io import StringIO
import sys


def before_all(context):
  context.real_stdout = sys.stdout
  context.log_spy = StringIO()
  sys.stdout = context.log_spy

  cfn = botocore.session.get_session().create_client("cloudformation")
  print('before all')

  
  context.stacks =  Stacks(cfn)
  context.cfn_client = cfn
  # context.log_spy = log_spy

def after_all(context):
  sys.stdout = context.real_stdout