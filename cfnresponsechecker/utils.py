import boto3


def get_accounts():
    client = boto3.client("organizations")
    accounts = client.list_accounts().get("Accounts")
    return sorted([account["Id"] for account in accounts])