"""
Using the Algorand SDK, write a Python command-line (CLI) based application that demonstrates the atomic transfer capability between 2 accounts A and B. 

In the atomic transfer, demonstrate how account A sends 5 Algos to account B and account B sends 2 units of an Algorand Standard Asset (ASA) to account A.

Notes
Make use of the Algorand Python SDK and connect to the Algorand Testnet. You can use a public node such as https://testnet-api.algonode.cloud.  
Create 2 accounts, one for user A and another for user B. 
Issue an ASA called UCTZAR.
Fund account A with Algos (you can use a testnet dispenser if you wish e.g. https://bank.testnet.algorand.network) and make sure account B has 10 units of the UCTZAR. 
Create an atomic transfer in which account A sends 5 Algos to account B and account B sends 2 units of UCTZAR ASA to account A. 
"""