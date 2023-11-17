"""
Question 6(vi)

CLI that demonstrates the issuing of a fractional NFT on the Algorand blockchain and distributing it among 3 accounts
"""

from algosdk.v2client import algod
from algosdk import account, transaction
import json
import os

algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
params = algod_client.suggested_params()

############################################################################################### 
# Admin controls

DEBUG               = False
CREATE_NEW_ACCOUNTS = False
ISSUE_NFT           = False
OPT_IN              = False

asset_id = 480243570 
accounts = [
  {
    "private_key": "9/uSPdOc7czkYVjQLGT3bQ5SBxW4FNB7v+xdCtT4MKZY6/N43gZWmfqCt/GX+vBZkOmwsMyGnT3cGAvQji8w2A==",
    "address": "LDV7G6G6AZLJT6UCW7YZP6XQLGIOTMFQZSDJ2PO4DAF5BDRPGDMC7CWA3Q",
	"luft" : 0.0
  },
  {
    "private_key": "YDOwZiTF7YMoKho76hf0XMpnIEPaIp8eehS2NDEAtF2JG/6d7JyPJhnRaEPxjk2coN5Jx4iDKkAJ5R3LRmY3Sw==",
    "address": "REN75HPMTSHSMGORNBB7DDSNTSQN4SOHRCBSUQAJ4UO4WRTGG5FRTC6PFY",
	"luft" : 0.0
  },
  {
    "private_key": "zzWC/j8nv8BLe1DGI7QI9PfeGnqV6oAFOC/CEqCgTPAC7u/EHsezT+P3W5qMqD9hwECcsM7xmJPxHlDdh8O4dQ==",
    "address": "ALXO7RA6Y6ZU7Y7XLONIZKB7MHAEBHFQZ3YZRE7RDZIN3B6DXB2W4WXW3Q",
	"luft" : 0.0
  }
]

if CREATE_NEW_ACCOUNTS:
	# Creates 3 new accounts and outputs the dict to be overwritten
	accounts = []
	for i in range(3):
		key, adr = account.generate_account()
		accounts.append(
			{
				'private_key' : key,
				'address' : adr
			}
		)
	print(json.dumps(accounts, indent = 2))
	# https://bank.testnet.algorand.network/

if ISSUE_NFT:
	# Issues 9.9 Luftballons to the first account
	txn = transaction.AssetConfigTxn(
		sender=accounts[0]['address'],
		sp=params,
		unit_name="LUFT",
		asset_name="Luftballons",
		total=99,
		decimals=1,
		strict_empty_address_check=False
	)

	stxn = txn.sign(accounts[0]['private_key'])
	txid = algod_client.send_transaction(stxn)
	results = transaction.wait_for_confirmation(algod_client, txid, 4)
	created_asset = results["asset-index"]
	print(f"Asset ID created: {created_asset}")

if OPT_IN:
	# Allows accounts to use Luftballons
	opt_in_txn = transaction.AssetTransferTxn(accounts[0]['address'], params, accounts[1]['address'], 0, index=asset_id)
	opt_in_txn_2 = transaction.AssetTransferTxn(accounts[0]['address'], params, accounts[2]['address'], 0, index=asset_id)
	transaction.assign_group_id([opt_in_txn, opt_in_txn_2])
	signed_group = [opt_in_txn.sign(accounts[0]['private_key']), opt_in_txn_2.sign(accounts[0]['private_key'])]

	tx_id = algod_client.send_transactions(signed_group)
	result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
	print(f"Opt-in txID: {tx_id} confirmed in round: {result.get('confirmed-round', 0)}")

###############################################################################################

def splash_screen():
	# Keeps the terminal clean
	# Logo generated using https://patorjk.com/software/taag/#p=display&f=Slant
	logo = r"""
    ______                __  _                   __   _   ______________    
   / ____/________ ______/ /_(_)___  ____  ____ _/ /  / | / / ____/_  __/____
  / /_  / ___/ __ `/ ___/ __/ / __ \/ __ \/ __ `/ /  /  |/ / /_    / / / ___/
 / __/ / /  / /_/ / /__/ /_/ / /_/ / / / / /_/ / /  / /|  / __/   / / (__  ) 
/_/   /_/   \__,_/\___/\__/_/\____/_/ /_/\__,_/_/  /_/ |_/_/     /_/ /____/  
                                                                             
"""
	os.system('cls')
	print(logo)

def main_menu():
	# Outputs menu options and prompts user for option
	splash_screen()
	print("1. View account balances\n2. Send LUFT\n3. Exit\n")
	option = int(input("> "))
	return option

def sync_balances():
	for account in accounts:
		info = algod_client.account_info(account['address'])
		if len(info['assets']) > 0:
			# Loop through ASAs and check for LUFT
			for asset in info['assets']:
				if asset['asset-id'] == asset_id and asset['amount'] > 0:
					account['luft'] = asset['amount']/10

def output_balances():
	# Outputs LUFT balances for all accounts
	splash_screen()
	for i, account in enumerate(accounts):
		info = algod_client.account_info(account['address'])

		print(f"Wallet {i+1}")
		print(f"Address: {account['address']}")

		if account['luft'] > 0:
			print(f"Balance: {account['luft']} Luftballons")
		else:
			print("User does not own any Luftballons")

		print(f"https://testnet.algoexplorer.io/address/{account['address']}\n")

def send_luft():
	# Prompts user to enter sender, receiver, and quantity of LUFT to send
	splash_screen()

	has_luft = False
	while not has_luft:
		sender = int(input("Please select sender account number (1/2/3)\n\n> "))
		if accounts[sender - 1]['luft'] > 0:
			has_luft = True
			print(f"Selected account has {accounts[sender - 1]['luft']} Luftballons\n")
		else:
			print("ERROR: Selected account has 0.0 Luftballons.\n")

	receiver = int(input("Please select receiver account number (1/2/3)\n\n> "))

	enough_luft = False
	while not enough_luft:
		amount = float(input(f"\nPlease enter amount of Luftballons to send\n\n> "))
		if accounts[sender - 1]['luft'] >= amount:
			enough_luft = True
		else:
			print(f"ERROR: Sender does not have {amount} Luftballons")
	
	splash_screen()

	# Executes the transaction
	txn = transaction.AssetTransferTxn(accounts[sender-1]['address'], params, accounts[receiver-1]['address'], int(amount * 10), index=asset_id)
	signed_tx = txn.sign(accounts[0]['private_key'])
	tx_id = algod_client.send_transaction(signed_tx)
	transaction.wait_for_confirmation(algod_client, tx_id, 4)
	
	# Output transaction summary
	print("Transaction Summary\n")
	print(f"{amount} LUFT sent from Account {sender} to Account {receiver}")
	print(f"\nhttps://testnet.algoexplorer.io/tx/{tx_id}")

if __name__ == "__main__":
	if not DEBUG:
		splash_screen()
		user_option = ""

		while (user_option != 3):
			user_option = main_menu()
			sync_balances()

			if user_option == 1:
				output_balances()
				input("\nPress ENTER to return to main menu\n> ")

			elif user_option == 2:
				send_luft()
				input("\nPress ENTER to return to main menu\n> ")