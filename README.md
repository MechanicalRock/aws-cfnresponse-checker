# aws-cfnresponse-checker

AWS announced [breaking changes to the Python SDK](https://aws.amazon.com/blogs/compute/upcoming-changes-to-the-python-sdk-in-aws-lambda/) that may require action before March 31 2021.

`aws-cfnresponse-checker` is a command line tool to check AWS accounts for custom cloud formation resources that need updating.

There are two modes:
 * Using [AssumeRole](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html) and temporary credentials: intended for [multi account](https://aws.amazon.com/blogs/industries/defining-an-aws-multi-account-strategy-for-telecommunications-companies/) environments
 * Using [environment credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html): intended for single accounts or testing purposes.

Run these scripts from an environment with the correct permissions to assume the account's role and perform read only operations on Cloudformation.

## Output

For example output, refer to [the feature file](features/cfn-response-reporter.feature).

The tool can identify three things:
- Stacks that have not been updated recently and **MUST** be updated to continue working
- Functions that use [inline](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html#cfn-lambda-function-code-zipfile) code and refer to the deprecated library.  These **MUST** be updated.
- Functions that use externally packaged lambda code.  These may/may not need to be updated - it is outside the scope of this tool to determine whether external function code needs updating.  But this tool should help to avoid things falling through the cracks.

## What does this find?
This tool locates any stacks using lambda backed Custom Resources, where the lambda function is defined in the same stack

## What does it NOT find?
If your lambda functions are defined externally (e.g. in a separate CloudFormation stack), this tool cannot identify them directly.  It identifies the custom resources, but you will need to perform additional investigation to determine whether the lambda functions themselves are affected.

If you package your lambda functions externally, opposed to [inline](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html#cfn-lambda-function-code-zipfile) then this tool cannot determine if the function has been updated

## Setup

Ensure that boto3 installed in a python3 environment

```bash
pipenv install && pipenv shell

OR

# For testing
pipenv install --pre --dev
```

## Usage

### Multi-account (AssumeRole)

#### Pre-requisites

* Cross-account trust must have been configured using [IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/tutorial_cross-account-with-roles.html)
  * The trusting account role should grant read only permissions to CloudFormation, e.g. by applying the [AWS Managed Policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html#aws-managed-policies) - `AWSCloudFormationReadOnlyAccess`: `arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess`
* The tool supports auto-discovering accounts using AWS Organizations.  **NOTE**: if you wish to use this functionality, the _trusted account_ needs to be the [root Organizations management account](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html)
* The tool should be run using appropriate [credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) from the _trusted account_
  * For Control Tower users, consider deploying as a lambda function in the [Audit Account](https://docs.aws.amazon.com/controltower/latest/userguide/how-control-tower-works.html)


#### AssumeRole - Single Account Checking:

If you want to test accounts individually:
```bash
python3 single_account.py --role-arn 'arn:aws:iam::${ROLE_ID}:role/${ROLE_NAME}' \
  --regions us-east-1,ap-southeast-2 \
  --clean-print
```

> `--regions` is optional, default is all regions
> `--role-arn` is arn of the role to assume in the _trusting account_
>
> Remove `--clean-print` to print region

### AssumeRole - Multiple Account Checking:

```bash
python3 cross_accounts.py --role-name ${ROLE_NAME} \
--regions us-east-1,ap-southeast-2 \
--accounts 111111111111,222222222222 \
--clean-print
```

> `--regions` is optional, default is all regions.
> `--accounts` is optional, will get all organization accounts by default (**NOTE**: for auto-discovery, it must be run from your [root Organization account](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html) context).
>
> Remove `--clean-print` to print accounts and regions

### Using Environment Credentials

Test a single account using your configured [SDK credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)

```bash
python3 principle_account.py \
--regions us-east-1,ap-southeast-2 \
--clean-print
```

> `--regions` is optional, default is all regions.
>
> Remove `--clean-print` to print accounts and regions

## Testing

If you are using the `AssumeRole` mechanism, you can configure a test to identify issues and validate that you have fixed any problems

1. Create a `accounts.json` file like so in the tests folder.

    ```json
    [
      {
        "account_id": "111111111111",
        "regions": ["us-east-1", "us-east-2", "ap-southeast-2"],
        "role_name": "MyRoleForAccount"
      },
      {
        "account_id": "222222222222",
        "regions": ["us-east-1", "us-east-2"],
        "role_name": "MyRoleForAccount"
      }
    ]
    ```

2. Then run pytest to test your accounts programatically before and after you've resolved them.

    ```bash
    pytest

    ====================== 5 failed, 1 passed in 15.54s ============
    ```

## Resolving problem stacks

There's two main methods to update the cfn-response module in your lambda functions:

### Add a comment to the inline code in your CloudFormation template.

```yaml
ZipFile: |
          import cfnresponse
          def handler(event, context):
+             # This comment was added to force an update on this function's code
              responseData = {'Message': 'Hello {}!'.format(event['ResourceProperties']['Name'])}
              cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, "CustomResourcePhysicalID")
```

### Update the ```Runtime``` Property for the function in your CloudFormation template.

```yaml
Handler: index.handler
  Role: !GetAtt MyRole.Arn
- Runtime: python3.6
+ Runtime: python3.7
  Code:
    ZipFile: |
      import cfnresponse
      def handler(event, context):
        responseData = {'Message': 'Hello {}!'.format(event['ResourceProperties']['Name'])}
        cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, "CustomResourcePhysicalID")
```

Then after updating your templates, run the tests again to see if your account still has stale inline CloudFormation response lambdas.

```bash
pytest

====================== 5 passed in 22.86s ======================
```

## References

- [Upcoming changes to the Python SDK in AWS Lambda](https://aws.amazon.com/blogs/compute/upcoming-changes-to-the-python-sdk-in-aws-lambda/)
- [Removing  the vendored version of requests from Botocore](https://aws.amazon.com/blogs/developer/removing-the-vendored-version-of-requests-from-botocore/)
- [CloudFormation cfn-response module](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html)
- [How do I update the AWS CloudFormation cfn-response module for AWS Lambda functions running on Python 2.7/3.6/3.7?](https://aws.amazon.com/premiumsupport/knowledge-center/cloudformation-cfn-response-lambda/)
