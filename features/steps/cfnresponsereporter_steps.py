import json

from cfnresponsereporter.reporter import Reporter

@given(u'the following response report')
def step_impl(context):
    context.cfn_response_report = json.loads(context.text)

@when(u'the cfn-response-reporter is run')
def step_impl(context):
    context.pretty_problem_report = Reporter().pretty_problem_report(context.cfn_response_report)

@then(u'the following report should be generated')
def step_impl(context):
    expected = context.text
    assert context.pretty_problem_report == expected, f'\nExpected: {context.text}\nActual  : {context.pretty_problem_report}'