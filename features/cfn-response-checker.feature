Feature: cfn-response-checker

Scenario: Out of date stack with inline python custom resource
  Given stack "my-stack" was last updated "2020-09-01" with template "out_of_date_stack"
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
              "logicalId": "myCustomResourceLambda",
              "code": "s3://some-deployment-bucket/uuid-here.zip"
            }
          ]
        }
      ]
    }
    """

# Scenario: Out of date stack does not contain python lambdas

# Scenario: Inline custom resource uses vendored urllib

# Scenario: Custom resource references external lambda

# Scenario: Stack is not out of date, but contains vendored reference

# Scenario: Externally packaged custom resource

# Scenario: Custom resources defined using "AWS::CloudFormation::CustomResource" type
# Scenario: Custom resources defined using "Custom::" type