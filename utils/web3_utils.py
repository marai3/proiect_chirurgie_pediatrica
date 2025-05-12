from web3 import Web3
import json

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

contract_address = Web3.to_checksum_address("0x1234567890abcdef1234567890abcdef12345678") 

with open("blockchain/MedicalLogABI.json") as f:
    abi = json.load(f)

contract = web3.eth.contract(address=contract_address, abi=abi)

def log_event(patient_id, event_type, user_role="unknown"):
    acct = web3.eth.accounts[0]  # primul cont Ganache
    try:
        tx = contract.functions.logEvent(user_role, patient_id, event_type).transact({'from': acct})
        receipt = web3.eth.wait_for_transaction_receipt(tx)
        print(f"[Blockchain] Logat: {event_type} pentru {patient_id} de {user_role} | TX: {receipt.transactionHash.hex()}")
    except Exception as e:
        print(f"[Eroare Blockchain] {str(e)}")
