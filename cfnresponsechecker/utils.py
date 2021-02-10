import boto3


def get_accounts():
    client = boto3.client("organizations")
    accounts = client.list_accounts().get("Accounts")
    return sorted([account["Id"] for account in accounts])

def paginator(client, resource, key, request=None):
    paginator = client.get_paginator(resource)
    if request:
        pages = paginator.paginate(**request)
    else:
        pages = paginator.paginate()
    return [item for sublist in pages for item in sublist[key]]
