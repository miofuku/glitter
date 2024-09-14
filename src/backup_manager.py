import json
import asyncio
from cryptography.fernet import Fernet

class BackupManager:
    def __init__(self, personal_blockchain):
        self.personal_blockchain = personal_blockchain
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

    def create_backup(self):
        data = {
            "owner": self.personal_blockchain.owner,
            "chain": [block.__dict__ for block in self.personal_blockchain.chain]
        }
        json_data = json.dumps(data)
        encrypted_data = self.cipher_suite.encrypt(json_data.encode())
        return encrypted_data

    def restore_from_backup(self, encrypted_data):
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        data = json.loads(decrypted_data)
        # Here you would typically validate the data and update the blockchain
        # For simplicity, we're just printing the restored data
        print(f"Restored data for user {data['owner']}")
        print(f"Chain length: {len(data['chain'])}")

    async def distribute_backup(self, p2p_network, trusted_nodes):
        backup_data = self.create_backup()
        tasks = [p2p_network.send_backup(node, backup_data) for node in trusted_nodes]
        await asyncio.gather(*tasks)

    async def request_backup_restoration(self, p2p_network, trusted_nodes):
        for node in trusted_nodes:
            backup_data = await p2p_network.request_backup(node)
            if backup_data:
                self.restore_from_backup(backup_data)
                return True
        return False