from solcx import compile_standard, install_solc
from web3 import Web3
import json
import os


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
ganache_url = "http://127.0.0.1:8545"  # sau 8545, în funcție de Ganache
web3 = Web3(Web3.HTTPProvider(ganache_url))
assert web3.is_connected(), "Conexiune eșuată la Ganache"

# 5. Configurare cont și nonce
account = web3.eth.accounts[0]
private_key = ""  # Dacă vrei să folosești trimitere semnată, altfel lasă gol

# 6. Deploy contract
MedicalLog = web3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = MedicalLog.constructor().transact({'from': account})
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

contract_instance = web3.eth.contract(
    address=tx_receipt.contractAddress,
    abi=abi,
)

print(f"Contractul a fost deployat la adresa: {tx_receipt.contractAddress}")

# 7. Apelează funcția logEvent
tx = contract_instance.functions.logEvent(
    "doctor", "PAT-1234", "view"
).transact({'from': account})
web3.eth.wait_for_transaction_receipt(tx)

# 8. Obține numărul de loguri
count = contract_instance.functions.getLogCount().call()
print("Număr loguri:", count)

# 9. Afișează primul log
log = contract_instance.functions.getLogByIndex(0).call()
print("\nPrimul log:")
print(f" - user: {log[0]}")
print(f" - role: {log[1]}")
print(f" - patientId: {log[2]}")
print(f" - eventType: {log[3]}")
print(f" - timestamp: {log[4]}")
