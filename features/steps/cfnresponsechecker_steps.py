# from pytest import assert_equals

from cfnresponsechecker.stacks import Stacks
from features.test_data.cfn_mock import stub

import sys

@given(u'stack "my-stack" was last updated "2020-09-01" with template "out_of_date_stack"')
def step_impl(context):
    stub(context.cfn_client, 'out_of_date_stack', "2020-09-01")


@when(u'I run cfn-response-checker')
def step_impl(context):
    context.stacks.get_problem_stacks()


@then(u'the output should contain "something"')
def step_impl(context):
    log_output = context.log_spy.getvalue()
    print("===================")
    print(log_output)
    print("===================")
    assert "something special" in log_output