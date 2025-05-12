from web3 import Web3
import json
<<<<<<< HEAD

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
=======
import os

# Load environment variables (if using a .env file, ensure to install python-dotenv and load it)
ETH_NODE_URL = os.getenv("ETH_NODE_URL", "http://127.0.0.1:7545")  # Default to Ganache
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x...")  # Replace with actual address or set via environment

# Connect to the Ethereum node
web3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))

if not web3.isConnected():
    raise ConnectionError("Failed to connect to the Ethereum node. Check the ETH_NODE_URL.")

# Load the ABI of the smart contract
abi_path = os.path.join(os.path.dirname(__file__), "../blockchain/MedicalLogABI.json")
try:
    with open(abi_path, "r") as f:
        abi = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"ABI file not found at {abi_path}. Ensure the path is correct.")

# Create a contract instance
try:
    contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
except ValueError:
    raise ValueError("Invalid contract address. Ensure CONTRACT_ADDRESS is set correctly.")

def log_event(patient_id, event_type):
    """
    Logs an event to the blockchain for a specific patient.

    :param patient_id: ID of the patient
    :param event_type: Type of event to log
    """
    try:
        # Use the first account from Ganache or the connected Ethereum node
        acct = web3.eth.accounts[0]
        tx = contract.functions.logEvent(patient_id, event_type).transact({'from': acct})
        receipt = web3.eth.wait_for_transaction_receipt(tx)
        print(f"Transaction successful: {receipt.transactionHash.hex()}")
    except IndexError:
        raise RuntimeError("No accounts available. Ensure your Ethereum node is configured correctly.")
    except Exception as e:
        raise RuntimeError(f"An error occurred while logging the event: {e}")
>>>>>>> 4de70005ada7e99a8eb21320c7e745b4696340fe
