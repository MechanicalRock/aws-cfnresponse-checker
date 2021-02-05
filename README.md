# aws-cfnresponse-checker

Checks aws accounts for custom cloud formation resources that need updating.

Prints the stack id for every stack identified as an issue.

## Usage

1. Ensure that boto3 installed in a python3 environment

```
pipenv install && pipenv shell

OR

# For testing
pipenv install --pre --dev
```

2. For Single Account Checking:

```
python3 single_account.py --role-arn 'arn:aws:iam::${ROLE_ID}:role/${ROLE_NAME}' \
  --regions us-east-1,ap-southeast-2 \
  --clean-print
```

> Region is optional, default is all regions

> Remove `--clean-print` to print region

3. For Cross Account Checking

```
python3 cross_accounts.py --role-name ${ROLE_NAME} \
 --regions us-east-1,ap-southeast-2 \
 --accounts 111111111111,222222222222 \
 --clean-print
```

> Region is optional, default is all regions.

> Accounts is optional, will get all organization accounts by default.

> Remove `--clean-print` to print accounts and regions

## Testing

1. Copy your problem stack ids (full arn) into /test/stacks.txt, one line per stack.
2. export your role name to AWS_ROLE_NAME

```
export AWS_ROLE_NAME=myRoleName
```

3. Then run pytest to test your stacks programatically after you've fixed them.

```
pytest

====================== 5 failed, 1 passed in 15.54s ======================
```
