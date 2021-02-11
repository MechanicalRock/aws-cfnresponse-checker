# aws-cfnresponse-checker

Checks aws accounts for custom cloud formation resources that need updating.

Run these scripts from an environment with the correct permissions to assume the account's role and perform read only operations on Cloudformation.

Prints the stack id for every stack identified as an issue.

## Usage

1. Ensure that boto3 installed in a python3 environment

    ```bash
    pipenv install && pipenv shell

    OR

    # For testing
    pipenv install --pre --dev
    ```

1. For Single Account Checking:

    ```bash
    python3 single_account.py --role-arn 'arn:aws:iam::${ROLE_ID}:role/${ROLE_NAME}' \
      --regions us-east-1,ap-southeast-2 \
      --clean-print
    ```

    > Regions is optional, default is all regions
    >
    > Remove `--clean-print` to print region

1. For Cross Account Checking

    ```bash
    python3 cross_accounts.py --role-name ${ROLE_NAME} \
    --regions us-east-1,ap-southeast-2 \
    --accounts 111111111111,222222222222 \
    --clean-print
    ```

    > Regions is optional, default is all regions.
    >
    > Accounts is optional, will get all organization accounts by default.
    >
    > Remove `--clean-print` to print accounts and regions

1. For Principle Account Checking

    ```bash
    python3 principle_account.py \
    --regions us-east-1,ap-southeast-2 \
    --clean-print
    ```

    > Regions is optional, default is all regions.
    >
    > Remove `--clean-print` to print accounts and regions

## Testing

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

There's two main methods to update the cfn-response module in your lambda functions.

- Add a comment to the inline code in your CloudFormation template.
    ```yaml
    ZipFile: |
              import cfnresponse
              def handler(event, context):
    +             # This comment was added to force an update on this function's code
                  responseData = {'Message': 'Hello {}!'.format(event['ResourceProperties']['Name'])}
                  cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, "CustomResourcePhysicalID")
    ```

- Update the ```Runtime``` Property for the function in your CloudFormation template.
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
