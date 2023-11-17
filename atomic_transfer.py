"""
Question 5(ii)

CLI that demonstrates the atomic transfer capability between 2 accounts on the Algorand testnet 
"""

from algosdk.v2client import algod
from algosdk import account, transaction
import json
import os

algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
params = algod_client.suggested_params()
currency = [ None, "Algos", "UCTZAR" ]
asset_id = 480136957 

# To create new accounts:
# account.generate_account()
# https://bank.testnet.algorand.network/

accounts = [
	{
		'private_key' : 'WYGSATBFpwuns7sej+93CE5hfhbXh69XGoyehokb5PnuE+GbGRDRO9COW1drY4vQRsHmI/lFSd6TXPNhlMJkiw==',
		'address' : '5YJ6DGYZCDITXUEOLNLWWY4L2BDMDZRD7FCUTXUTLTZWDFGCMSFVG45HAQ'
	},
	{
		'private_key' : '37DCDUqksnRD2GyTc0y0bibsk2bD5pl/KGDqeN1s3z6CgQF9qq6VBs0RkdTQXxEfGY1PkTjOMpd2Ba2d5GW1rQ==',
		'address' : 'QKAQC7NKV2KQNTIRSHKNAXYRD4MY2T4RHDHDFF3WAWWZ3ZDFWWWWD7PYQE'
	},
]

def splash_screen():
	# https://patorjk.com/software/taag/#p=display&f=Slant
	logo = r"""
    ___   __                  _         ______                      ____         
   /   | / /_____  ____ ___  (_)____   /_  __/________ _____  _____/ __/__  _____
  / /| |/ __/ __ \/ __ `__ \/ / ___/    / / / ___/ __ `/ __ \/ ___/ /_/ _ \/ ___/
 / ___ / /_/ /_/ / / / / / / / /__     / / / /  / /_/ / / / (__  ) __/  __/ /    
/_/  |_\__/\____/_/ /_/ /_/_/\___/    /_/ /_/   \__,_/_/ /_/____/_/  \___/_/     

	"""
	os.system('cls')
	print(logo)

menu = f"""1. View account balances
2. Execute an atomic transaction
3. Exit
"""

ISSUE_ASA = False
OPT_IN = False

if ISSUE_ASA:
	txn = transaction.AssetConfigTxn(
		sender=accounts[1]['address'],
		sp=params,
		unit_name="UCTZAR",
		asset_name="UCTZAR",
		total=10,
		strict_empty_address_check=False
	)

	stxn = txn.sign(accounts[1]['private_key'])
	txid = algod_client.send_transaction(stxn)
	results = transaction.wait_for_confirmation(algod_client, txid, 4)
	created_asset = results["asset-index"]
	print(f"Asset ID created: {created_asset}")

if OPT_IN:
	opt_in_txn = transaction.AssetTransferTxn(accounts[0]['address'], params, accounts[0]['address'], 0, index=asset_id)
	opt_in_txn_2 = transaction.AssetTransferTxn(accounts[1]['address'], params, accounts[1]['address'], 0, index=asset_id)
	transaction.assign_group_id([opt_in_txn, opt_in_txn_2])
	signed_group = [opt_in_txn.sign(accounts[0]['private_key']), opt_in_txn_2.sign(accounts[1]['private_key'])]

	tx_id = algod_client.send_transactions(signed_group)
	result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
	print(f"Opt-in txID: {tx_id} confirmed in round: {result.get('confirmed-round', 0)}")

def output_balances():
	for i, account in enumerate(accounts):
		info = algod_client.account_info(account['address'])

		print(f"\nAccount {"A" if i == 0 else "B"}")
		print(f"Address: {account['address']}")
		print(f"Balance: {info['amount'] / 1e6} Algos  ||  {info['assets'][0]['amount']} UCTZAR")
		print(f"https://testnet.algoexplorer.io/address/{account['address']}")

def exec_atomic_transaction():
	accA_currency = int(input("Select Account A cryptocurrency\n1. Algos\n2. UCTZAR\n> "))
	accA_amount = float(input(f"Enter amount of {currency[accA_currency]} to send\n> "))
	
	splash_screen()
	accB_currency = int(input("Set Account B cryptocurrency\n1. Algos\n2. UCTZAR\n> "))
	accB_amount = float(input(f"Enter amount of {currency[accB_currency]} to send\n> "))

	if accA_currency == 1:
		txn_1 = transaction.PaymentTxn(accounts[0]['address'], params, accounts[1]['address'], accA_amount * 1e6)
	elif accA_currency == 2:
		txn_1 = transaction.AssetTransferTxn(accounts[0]['address'], params, accounts[1]['address'], accA_amount, index=asset_id)

	if accB_currency == 1:
		txn_2 = transaction.PaymentTxn(accounts[1]['address'], params, accounts[0]['address'], accB_amount * 1e6)
	elif accB_currency == 2:
		txn_2 = transaction.AssetTransferTxn(accounts[1]['address'], params, accounts[0]['address'], accB_amount, index=asset_id)
	
	transaction.assign_group_id([txn_1, txn_2])
	signed_group = [txn_1.sign(accounts[1]['private_key']), txn_2.sign(accounts[0]['private_key'])]
	tx_id = algod_client.send_transactions(signed_group)
	result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
	
	print(f"txID: {tx_id} confirmed in round: {result.get('confirmed-round', 0)}")


if __name__ == "__main__":
	splash_screen()
	option = ""

	while (option != 3):
		splash_screen()
		print(menu)
		option = int(input("> "))
		splash_screen()

		if option == 1:
			output_balances()
			input("\nENTER to return to main menu\n> ")
		elif option == 2:
			exec_atomic_transaction()
			input("\nENTER to return to main menu\n> ")

		print()

