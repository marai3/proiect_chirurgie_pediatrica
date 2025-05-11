from web3 import Web3
import json

# Connect to the local Ethereum node
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Address of the deployed smart contract
contract_address = "0x..."  # Replace with the actual contract address

# Load the ABI of the smart contract
with open("blockchain/MedicalLogABI.json") as f:
    abi = json.load(f)

# Create a contract instance
contract = web3.eth.contract(address=contract_address, abi=abi)

def log_event(patient_id, event_type):
    acct = web3.eth.accounts[0]  # Use the first account from Ganache
    tx = contract.functions.logEvent(patient_id, event_type).transact({'from': acct})
    web3.eth.wait_for_transaction_receipt(tx)
    print(f"Log blockchain: {event_type} pentru {patient_id}")