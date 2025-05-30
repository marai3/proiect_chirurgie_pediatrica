from solcx import compile_standard, install_solc
from web3 import Web3
import json


# 1. Instalează și selectează versiunea de compilator
install_solc("0.8.0")

with open("blockchain/MedicalLog.sol", "r") as file:
    contract_source_code = file.read()

# 2. Compilează contractul
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"MedicalLog.sol": {"content": contract_source_code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

# 3. Extrage ABI și Bytecode
bytecode = compiled_sol["contracts"]["MedicalLog.sol"]["MedicalLog"]["evm"]["bytecode"]["object"]
abi = compiled_sol["contracts"]["MedicalLog.sol"]["MedicalLog"]["abi"]

# 4. Conectare la Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
assert web3.is_connected(), "Conexiune eșuată la Ganache"

# 5. Configurare cont și nonce
account = web3.eth.accounts[0]
private_key = ""

# 6. Deploy contract
MedicalLog = web3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = MedicalLog.constructor().transact({'from': account})
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

# Salvează ABI și adresa contractului într-un fișier JSON
with open("blockchain/MedicalLogABI.json", "w") as f:
    json.dump({
        "abi": abi,
        "address": tx_receipt.contractAddress
    }, f)

contract_instance = web3.eth.contract(
    address=tx_receipt.contractAddress,
    abi=abi,
)

print(f"Contractul a fost deployat la adresa: {tx_receipt.contractAddress}")

# 7. funcția logEvent
def log_event(user_name, user_role, patient_id, event_type):
    try:
        tx = contract_instance.functions.logEvent(user_name,user_role, patient_id, event_type).transact({'from': account})
        web3.eth.wait_for_transaction_receipt(tx)
        print(f"Log blockchain salvat: {user_name} - {user_role} : {event_type} pe {patient_id}")
    except Exception as e:
        print(f"Eroare blockchain: {e}")

# 8. Obține numărul de loguri
def get_log_count():
    return contract_instance.functions.getLogCount().call()

# 9. obține logul după index
def get_log_by_index(index):
    log = contract_instance.functions.getLogByIndex(index).call()
    return {
        "wallet": log[0],
        "user_name": log[1],
        "user_role": log[2],
        "patient_id": log[3],
        "event_type": log[4],
        "timestamp": log[5],
    }


# 10. Obține toate logurile
def get_all_logs():
    log_count = get_log_count()
    logs = []
    for i in range(log_count):
        logs.append(get_log_by_index(i))
    return logs

# 11. Obține loguri după ID pacient
def get_logs_by_patient_id(patient_id):
    log_count = get_log_count()
    logs = []
    for i in range(log_count):
        log = get_log_by_index(i)
        if log["patient_id"] == patient_id:
            logs.append(log)
    return logs
