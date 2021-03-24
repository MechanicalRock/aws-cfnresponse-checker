Feature: cfn-response-reporter

Scenario: Create a pretty report
  Given the following response report:
  """
  {
        "stacks": ["arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-bbbb", "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-cccc"],
        "function_report": [
          {
            "stack": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-dddd",
            "functions": [
              {
                "logicalId": "MyCustomResourceLambda",
                "code": "<inline>"
              },
              {
                "logicalId": "MyCustomResourceLambda2",
                "code": "external"
              }              
            ]
          },
          {
            "stack": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-eeee",
            "functions": [
              {
                "logicalId": "MyCustomResourceLambda3",
                "code": "<inline>"
              }
            ]
          }          
        ],
        "inline_vendored_usage": ["arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-dddd", "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-eeee"]
      }
  """
  When the cfn-response-reporter is run
  Then the following report should be generated:
  """
  The following stacks are out of date and need to be re-deployed:
  <instructions here...>
  - arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-bbbb
  - arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-cccc

  The following stacks contain the use of deprecated `botocore.vendored` and MUST be updated:
  <instructions here>
  - arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-dddd
  - arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-eeee

  The following stacks contain Python functions.  These could not be evaluated, but should be reviewed for deprecated usage:
  | Stack                                                                                                                    | Function                | Code     |
  | arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-dddd | MyCustomResourceLambda  | <inline> |
  | arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-dddd | MyCustomResourceLambda2 | external |
  | arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-eeee | MyCustomResourceLambda3 | <inline> |
  
  """