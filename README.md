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

2. For Single Account Checking:

```bash
python3 single_account.py --role-arn 'arn:aws:iam::${ROLE_ID}:role/${ROLE_NAME}' \
  --regions us-east-1,ap-southeast-2 \
  --clean-print
```

> Regions is optional, default is all regions

> Remove `--clean-print` to print region

3. For Cross Account Checking

```bash
python3 cross_accounts.py --role-name ${ROLE_NAME} \
 --regions us-east-1,ap-southeast-2 \
 --accounts 111111111111,222222222222 \
 --clean-print
```

> Regions is optional, default is all regions.

> Accounts is optional, will get all organization accounts by default.

> Remove `--clean-print` to print accounts and regions

4. For Principle Account Checking

```bash
python3 principle_account.py \
 --regions us-east-1,ap-southeast-2 \
 --clean-print
```

> Regions is optional, default is all regions.

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

2. Then run pytest to test your accounts programatically before and after you've fixed them.

### Before Fixing

```bash
pytest

====================== 5 failed, 1 passed in 15.54s ============
```

### After Fixing

```bash
pytest

====================== 5 passed in 22.86s ======================
```
