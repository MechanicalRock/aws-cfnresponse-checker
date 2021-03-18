Feature: cfn-response-checker

Scenario: Out of date stack with inline python custom resource
  Given stack "my-stack" was last updated "2020-09-01" with template "out_of_date_stack"
  When I run cfn-response-checker
  Then the output should contain "something"

# Scenario: Out of date stack does not contain python lambdas

# Scenario: Inline custom resource uses vendored urllib

# Scenario: Custom resource references external lambda

# Scenario: Stack is not out of date, but contains vendored reference

# Scenario: Externally packaged custom resource

# Scenario: Custom resources defined using "AWS::CloudFormation::CustomResource" type
# Scenario: Custom resources defined using "Custom::" type