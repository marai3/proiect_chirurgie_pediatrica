from web3 import Web3
import json

# Conectare la Ganache (asigură-te că Ganache rulează)
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Verificare conexiune
if not web3.is_connected():
    raise ConnectionError("Nu se poate conecta la Ganache!")

# Adresa contractului (copiază de la Remix după deploy)
contract_address = "0xEE58f124D88691ea5502BE31af283a69480C2D19"  # modifică cu adresa reală

# Încărcare ABI (exportă din Remix după deploy și salvează ca MedicalLog_abi.json)
with open(r"blockchain\MedicalLogABI.json") as f:
    abi = json.load(f)

# Inițializare contract
contract = web3.eth.contract(address=contract_address, abi=abi)

# Alegem un cont din Ganache (folosește contul 0 implicit)
account = web3.eth.accounts[0]

# Definirea variabilelor cu datele pentru log
user_role = "medic"
patient_id = "pacient123"
event_type = "modificare date"

# Trimitere tranzacție
tx_hash = contract.functions.logEvent(user_role, patient_id, event_type).transact({'from': account})

receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

print("✅ Eveniment logat cu succes!")
print(f"Tx hash: {tx_hash.hex()}")

count = contract.functions.getLogCount().call()
print(f"Număr evenimente logate: {count}")

for i in range(count):
    log = contract.functions.getLogByIndex(i).call()
    print(f"Log {i}: User: {log[0]}, Role: {log[1]}, Pacient: {log[2]}, Event: {log[3]}, Time: {log[4]}")