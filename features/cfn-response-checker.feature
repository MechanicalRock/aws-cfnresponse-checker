Feature: cfn-response-checker

Scenario Outline: Out of date stack with inline python custom resource
  Given stack "my-stack" was last updated "2020-09-01" with <template_type> template "<template>"
  When I run cfn-response-checker.get_problem_report()
  Then the problem report should return: 
    """ 
    {
      "stacks": ["arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-out-of-date-stack/31b30580-87ad-11eb-8e6c-aaaaa"],
      "functions": [
        {
          "stack": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-out-of-date-stack/31b30580-87ad-11eb-8e6c-aaaaa",
          "functions": [
            {
              "logicalId": "MyCustomResourceLambda",
              "code": "<inline>"
            }
          ]
        }
      ],
      "inline_vendored_usage": []
    }
    """

Examples:
  | template_type | template          |
  | json          | out_of_date_stack |
  | yaml          | out_of_date_stack |

Scenario: Out of date stack does not contain python lambdas
  Given stack "my-stack" was last updated "2020-09-01" with json template "out_of_date_stack-nodejs"
  When I run cfn-response-checker.get_problem_report()
  Then the problem report should return: 
    """ 
    {
      "stacks": [],
      "functions": [],
      "inline_vendored_usage": []
    }
    """
    
Scenario: Stack does not contain any lambda functions
  Given stack "my-stack" was last updated "2020-09-01" with json template "out_of_date_stack_no_lambdas"
  When I run cfn-response-checker.get_problem_report()
  Then the problem report should return: 
    """ 
    {
      "stacks": [],
      "functions": [],
      "inline_vendored_usage": []
    }
    """

Scenario: Stack does not report any resources (invalid role)
  Given stack "my-stack" was last updated "2020-09-01" with json template "stack_no_resources_reported"
  When I run cfn-response-checker.get_problem_report()
  Then the problem report should return: 
    """ 
    {
      "stacks": [],
      "functions": [],
      "inline_vendored_usage": []
    }
    """

Scenario: External Lambda package
  Given stack "my-stack" was last updated "2020-09-01" with yaml template "external_lambda_package"
    When I run cfn-response-checker.get_problem_report()
    Then the problem report should return: 
      """ 
      {
        "stacks": ["arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-external_lambda_package/31b30580-87ad-11eb-8e6c-ccccc"],
        "functions": [
          {
            "stack": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-external_lambda_package/31b30580-87ad-11eb-8e6c-ccccc",
            "functions": [
              {
                "logicalId": "MyCustomResourceLambda",
                "code": "s3://my-bucket/some/path-to-aaa.zip"
              }
            ]
          }
        ],
        "inline_vendored_usage": []
      }
      """

Scenario: Inline custom resource uses vendored urllib
  Given stack "my-stack" was last updated "2020-09-01" with yaml template "vendored_inline"
    When I run cfn-response-checker.get_problem_report()
    Then the problem report should return: 
      """ 
      {
        "stacks": ["arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-dddd"],
        "functions": [
          {
            "stack": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-dddd",
            "functions": [
              {
                "logicalId": "MyCustomResourceLambda",
                "code": "<inline>"
              }
            ]
          }
        ],
        "inline_vendored_usage": ["arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-vendored_inline/31b30580-87ad-11eb-8e6c-dddd"]
      }
      """

Scenario: Stack was deployed recently
  Given stack "my-stack" was last updated "2021-02-01" with json template "out_of_date_stack"
  When I run cfn-response-checker.get_problem_report()
  Then the problem report should return: 
    """ 
    {
      "stacks": [],
      "functions": [
        {
          "stack": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/cfnresponsechecker-out-of-date-stack/31b30580-87ad-11eb-8e6c-aaaaa",
          "functions": [
            {
              "logicalId": "MyCustomResourceLambda",
              "code": "<inline>"
            }
          ]
        }
      ],
      "inline_vendored_usage": []
    }
    """

# Scenario: Custom resource references external lambda


# Scenario: Custom resources defined using "AWS::CloudFormation::CustomResource" type
# Scenario: Custom resources defined using "Custom::" type