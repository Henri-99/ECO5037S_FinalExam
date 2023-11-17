"""
Question 5(ii)

Using the Algorand SDK, write a Python command-line (CLI) based application that demonstrates the atomic transfer capability between 2 accounts A and B. 

In the atomic transfer, demonstrate how account A sends 5 Algos to account B and account B sends 2 units of an Algorand Standard Asset (ASA) to account A.

Notes
Make use of the Algorand Python SDK and connect to the Algorand Testnet. You can use a public node such as https://testnet-api.algonode.cloud.  
Create 2 accounts, one for user A and another for user B. 
Issue an ASA called UCTZAR.
Fund account A with Algos (you can use a testnet dispenser if you wish e.g. https://bank.testnet.algorand.network) and make sure account B has 10 units of the UCTZAR. 
Create an atomic transfer in which account A sends 5 Algos to account B and account B sends 2 units of UCTZAR ASA to account A. 
"""
from algosdk.v2client import algod
from algosdk import account, transaction

algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)

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

account_info = algod_client.account_info(accounts[0]['address'])
print(f"Account balance: {account_info.get('amount')} microAlgos")


ISSUE_ASA = False
ATOMIC_TRANSFER = True

sp = algod_client.suggested_params()

if ISSUE_ASA:
	txn = transaction.AssetConfigTxn(
		sender=accounts[1]['address'],
		sp=sp,
		unit_name="UCTZAR",
		asset_name="UCTZAR",
		total=10,
		strict_empty_address_check=False
	)

	stxn = txn.sign(accounts[1]['private_key'])
	txid = algod_client.send_transaction(stxn)

	print(f"Sent asset create transaction with txid: {txid}")
	# Wait for the transaction to be confirmed
	results = transaction.wait_for_confirmation(algod_client, txid, 4)
	print(f"Result confirmed in round: {results['confirmed-round']}")

	created_asset = results["asset-index"]
	print(f"Asset ID created: {created_asset}")

if ATOMIC_TRANSFER:
	asset_id = 480136957 
	opt_in_txn = transaction.AssetTransferTxn(accounts[0]['address'], sp, accounts[0]['address'], 0, index=asset_id)
	opt_in_txn_2 = transaction.AssetTransferTxn(accounts[1]['address'], sp, accounts[1]['address'], 0, index=asset_id)
	transaction.assign_group_id([opt_in_txn, opt_in_txn_2])
	stxn_1 = opt_in_txn.sign(accounts[0]['private_key'])
	stxn_2 = opt_in_txn_2.sign(accounts[1]['private_key'])
	signed_group = [stxn_1, stxn_2]
	tx_id = algod_client.send_transactions(signed_group)
	result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
	print(f"Opt-in txID: {tx_id} confirmed in round: {result.get('confirmed-round', 0)}")


	asset_amount = 1
	txn_1 = transaction.PaymentTxn(accounts[1]['address'], sp, accounts[0]['address'], 100)
	txn_2 = transaction.AssetTransferTxn(accounts[0]['address'], sp, accounts[1]['address'], asset_amount, index=asset_id)

	transaction.assign_group_id([txn_1, txn_2])
	stxn_1 = txn_1.sign(accounts[1]['private_key'])
	stxn_2 = txn_2.sign(accounts[0]['private_key'])
	signed_group = [stxn_1, stxn_2]
	tx_id = algod_client.send_transactions(signed_group)
	result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
	print(f"txID: {tx_id} confirmed in round: {result.get('confirmed-round', 0)}")



