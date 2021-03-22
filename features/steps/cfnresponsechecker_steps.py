from cfnresponsechecker.stacks import Stacks
from features.test_data.cfn_mock import stub

import json

@given(u'stack "my-stack" was last updated "{last_updated}" with template "{template}"')
def step_impl(context, last_updated, template):
    stub(context.stubber, template, last_updated)

@when(u'I run cfn-response-checker.get_problem_report()')
def step_impl(context):
    context.cfn_response_report = context.stacks.get_problem_report()

@then(u'the problem report should return')
def step_impl(context):

    # parse/jump json string to ignore spacing from feature file
    expected = json.dumps(json.loads(context.text))
    assert json.dumps(context.cfn_response_report) == expected, f'\nExpected: {context.text}\nActual  : {context.cfn_response_report}'