# Investec API - Maintain Balance on Account

## Description
This lamdba fires every five minutes, where it balances your primary account (specified through an environment variable) to an amount you specify (also in an environment variable) (best results is to equal it to your overdraft limit). 

This ensures that all your funds are in a secondary account - this assumes it is your PrimeSaver account through the naming conventions. (it can be any account that allows transfers, specified in an environment variable) which earns / reduces your interest automatically. 

## Usage
- Make a Serverless Platform Account
- Configure your AWS Account on Serverless
- Deploy using the CLI (remember to pass the environment variables into the deploy command)
- Profit (a.k.a. more / less interest!)

## Enhancements (To-Do List)
- Add error handling on the API
- Handle timeouts on the API (happens every now and then)
- Handle better error logging