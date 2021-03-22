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
      ]
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
      "functions": []
    }
    """
    
Scenario: Stack does not contain any lambda functions
  Given stack "my-stack" was last updated "2020-09-01" with json template "out_of_date_stack_no_lambdas"
  When I run cfn-response-checker.get_problem_report()
  Then the problem report should return: 
    """ 
    {
      "stacks": [],
      "functions": []
    }
    """

Scenario: Strack does not report any resources (invalid role)
  Given stack "my-stack" was last updated "2020-09-01" with json template "stack_no_resources_reported"
  When I run cfn-response-checker.get_problem_report()
  Then the problem report should return: 
    """ 
    {
      "stacks": [],
      "functions": []
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
        ]
      }
      """
# Scenario: Inline custom resource uses vendored urllib

# Scenario: Custom resource references external lambda

# Scenario: Stack is not out of date, but contains vendored reference

# Scenario: Externally packaged custom resource

# Scenario: Custom resources defined using "AWS::CloudFormation::CustomResource" type
# Scenario: Custom resources defined using "Custom::" type