"""
Question 5(ii)

CLI that demonstrates the atomic transfer capability between 2 accounts on the Algorand testnet 
"""

from algosdk.v2client import algod
from algosdk import account, transaction
import os

algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
params = algod_client.suggested_params()

############################################################################################### 
# Admin controls

DEBUG               = False
CREATE_NEW_ACCOUNTS = False
ISSUE_ASA           = False
OPT_IN              = False

asset_id = 480185583 
accounts = [
	{
		'private_key' : 'nS2TJ0J92kqKaYc2tbeAH47KftNw94mve9ZKTTzKuZslzkpa4OVk9Azkv4hPpr9yA9zXHpz5xXEy/w8MWb0brw==',
		'address' : 'EXHEUWXA4VSPIDHEX6EE7JV7OIB5ZVY6TT44K4JS74HQYWN5DOXXBWTA5I'
	},
	{
		'private_key' : '4Q3Ulh+CnPM3wJZMb3vr78hb4sQju040P+wBafRvu8CTZP4Yx7arngPkxXFlJ8nsuq9emD1c+fhQ+DfYbQ2ZrQ==',
		'address' : 'SNSP4GGHW2VZ4A7EYVYWKJ6J5S5K6XUYHVOPT6CQ7A35Q3INTGW6J73EOY'
	},
]

if CREATE_NEW_ACCOUNTS:
	# Creates 2 new accounts and outputs private key, addresses
	print(account.generate_account())
	print(account.generate_account())
	# https://bank.testnet.algorand.network/

if ISSUE_ASA:
	# Issues 10 UCTZAR to the second account
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
	# Allows both accounts to use UCTZAR
	opt_in_txn = transaction.AssetTransferTxn(accounts[0]['address'], params, accounts[0]['address'], 0, index=asset_id)
	opt_in_txn_2 = transaction.AssetTransferTxn(accounts[1]['address'], params, accounts[1]['address'], 0, index=asset_id)
	transaction.assign_group_id([opt_in_txn, opt_in_txn_2])
	signed_group = [opt_in_txn.sign(accounts[0]['private_key']), opt_in_txn_2.sign(accounts[1]['private_key'])]

	tx_id = algod_client.send_transactions(signed_group)
	result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
	print(f"Opt-in txID: {tx_id} confirmed in round: {result.get('confirmed-round', 0)}")

###############################################################################################

currency = [ None, "Algos", "UCTZAR" ]

def splash_screen():
	# Keeps the terminal clean
	# Logo generated using https://patorjk.com/software/taag/#p=display&f=Slant
	logo = r"""
    ___   __                  _         ______                      ____         
   /   | / /_____  ____ ___  (_)____   /_  __/________ _____  _____/ __/__  _____
  / /| |/ __/ __ \/ __ `__ \/ / ___/    / / / ___/ __ `/ __ \/ ___/ /_/ _ \/ ___/
 / ___ / /_/ /_/ / / / / / / / /__     / / / /  / /_/ / / / (__  ) __/  __/ /    
/_/  |_\__/\____/_/ /_/ /_/_/\___/    /_/ /_/   \__,_/_/ /_/____/_/  \___/_/     

	"""
	os.system('cls')
	print(logo)

def main_menu():
	# Outputs menu options and prompts user for option
	splash_screen()
	print("1. View account balances\n2. Execute an atomic transfer\n3. Exit\n")
	option = int(input("> "))
	return option

def output_balances():
	# Fetches and prints Algo + UCTZAR balances for both accounts
	splash_screen()
	for i, account in enumerate(accounts):
		info = algod_client.account_info(account['address'])

		print(f"User {"A" if i == 0 else "B"} Wallet")
		print(f"Address: {account['address']}")
		print(f"Balance: {info['amount'] / 1e6} Algos  ||  {info['assets'][0]['amount']} UCTZAR")
		print(f"https://testnet.algoexplorer.io/address/{account['address']}\n")

def exec_atomic_transfer():
	# Prompts user to enter type and amount of cryptocurrency for each wallet to send
	splash_screen()
	currency_a = int(input("Select cryptocurrency for User A to send to User B\n1. Algos\n2. UCTZAR\n\n> "))
	amount_a = float(input(f"\nEnter amount of {currency[currency_a]} to send\n\n> "))
	
	splash_screen()
	currency_b = int(input("Set cryptocurrency for User B to send to User A\n1. Algos\n2. UCTZAR\n\n> "))
	amount_b = float(input(f"\nEnter amount of {currency[currency_b]} to send\n\n> "))

	# Create the transactions
	if currency_a == 1:
		txn_1 = transaction.PaymentTxn(accounts[0]['address'], params, accounts[1]['address'], int(amount_a * 1e6))
	elif currency_a == 2:
		txn_1 = transaction.AssetTransferTxn(accounts[0]['address'], params, accounts[1]['address'], int(amount_a), index=asset_id)

	if currency_b == 1:
		txn_2 = transaction.PaymentTxn(accounts[1]['address'], params, accounts[0]['address'], int(amount_b * 1e6))
	elif currency_b == 2:
		txn_2 = transaction.AssetTransferTxn(accounts[1]['address'], params, accounts[0]['address'], int(amount_b), index=asset_id)
	
	# Group transactions together, sign them, and complete 
	splash_screen()
	transaction.assign_group_id([txn_1, txn_2])
	signed_group = [txn_1.sign(accounts[0]['private_key']), txn_2.sign(accounts[1]['private_key'])]
	tx_id = algod_client.send_transactions(signed_group)
	transaction.wait_for_confirmation(algod_client, tx_id, 4)
	
	# Output transaction summary
	print("Transaction Summary\n")
	print(f"User A successfully sent {amount_a} {currency[currency_a]} to User B")
	print(f"User B successfully sent {amount_b} {currency[currency_b]} to User A")
	print(f"\nhttps://testnet.algoexplorer.io/tx/{tx_id}")

if __name__ == "__main__":
	if not DEBUG:
		splash_screen()
		user_option = ""

		while (user_option != 3):
			user_option = main_menu()

			if user_option == 1:
				output_balances()
				input("\nPress ENTER to return to main menu\n> ")

			elif user_option == 2:
				exec_atomic_transfer()
				input("\nPress ENTER to return to main menu\n> ")