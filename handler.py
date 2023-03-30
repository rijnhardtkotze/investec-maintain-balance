import json
import requests
from requests.auth import HTTPBasicAuth
import os

primary_account_id = os.environ['PRIMARY_ACCOUNT_ID']
savings_account_id = os.environ['SAVINGS_ACCOUNT_ID']
primary_account_min_balance = int(os.environ['PRIMARY_ACCOUNT_MIN_BALANCE'])

def get_auth_token(client_id, client_secret):
    url = 'https://openapi.investec.com/identity/v2/oauth2/token'
    data = {'grant_type': 'client_credentials'}
    headers = {
        'x-api-key': os.environ['API_KEY'],
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, data=data, auth=HTTPBasicAuth(client_id, client_secret), headers=headers)

    return response.json()['access_token']

def make_get_request(url, token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None


def get_accounts(token):
    url = 'https://openapi.investec.com/za/pb/v1/accounts'
    response = make_get_request(url, token)
    if response is not None:
        return response['data']['accounts']
    else:
        return NotImplementedError
    

def get_account_balance(account_id, token):
    url = f'https://openapi.investec.com/za/pb/v1/accounts/{account_id}/balance'
    response = make_get_request(url, token)
    print(response)
    return response['data']['availableBalance'] if response is not None else NotImplementedError


def transfer(from_account_id, to_account_id, amount, token):
    url = f'https://openapi.investec.com/za/pb/v1/accounts/{from_account_id}/transfermultiple'
    data =  { 
        'transferList': [
            {
            "beneficiaryAccountId": f"{to_account_id}",
            "amount": f"{amount}",
            "myReference": "API transfer",
            "theirReference": "API transfer"
            }
        ] 
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=data, headers=headers)
    print(response.json() if response.status_code == 200 else None)

def maintain_balance(event, context):
    token = get_auth_token(os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'])

    primary_account_balance = get_account_balance(primary_account_id, token)
    savings_account_balance = get_account_balance(savings_account_id, token)

    # Handle errors on getting account balances
    if primary_account_balance is NotImplementedError or savings_account_balance is NotImplementedError:
        return {"statusCode": 500, "body": 'Error getting account balances'}
    
    print('=================================================================')
    print(f'Primary Account Balance: {primary_account_balance}')
    print(f'Savings Account Balance: {savings_account_balance}')
    print('=================================================================')

    if primary_account_balance < primary_account_min_balance:
        if savings_account_balance > primary_account_min_balance - primary_account_balance:
            print(f'Primary account balance: {primary_account_balance}, transferring funds from savings account: {primary_account_min_balance - primary_account_balance}')
            transfer(savings_account_id, primary_account_id, primary_account_min_balance - primary_account_balance, token)
            print(f'Funds transferred from savings account to primary account. Savings account balance: {get_account_balance(savings_account_id, token)}')
            return {"statusCode": 200, "body": f'Primary account balance: {primary_account_balance}, transferring funds from savings account: {primary_account_min_balance - primary_account_balance}'}
        else:
            print('Insufficient funds in savings account')
            return {"statusCode": 200, "body": 'Insufficient funds in savings account'}
    else:
        if primary_account_balance > primary_account_min_balance:
            print(f'Primary account balance: {primary_account_balance}, transferring funds to savings account: {primary_account_balance - primary_account_min_balance}')
            transfer(primary_account_id, savings_account_id, primary_account_balance - primary_account_min_balance, token)
            print(f'Funds transferred from primary account to savings account. Savings account balance: {get_account_balance(savings_account_id, token)}')
            return {"statusCode": 200, "body": f'Primary account balance: {primary_account_balance}, transferring funds to savings account: {primary_account_balance - primary_account_min_balance}'}
        else:
            print('Primary account balance is within the minimum threshold')
            return {"statusCode": 200, "body": 'Primary account balance is within the minimum threshold'}