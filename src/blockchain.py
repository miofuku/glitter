import hashlib
import time
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from backup_manager import BackupManager


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()


class PersonalBlockchain:
    def __init__(self, owner):
        self.chain = [self.create_genesis_block()]
        self.owner = owner
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self.backup_manager = BackupManager(self)
        self.trusted_nodes = set()

    def create_genesis_block(self):
        return Block(0, time.time(), {"data": "Genesis Block", "signature": None}, "0")

    def add_block(self, data):
        previous_block = self.chain[-1]
        signed_data = self.sign_data(data)
        new_block = Block(len(self.chain), time.time(), {"data": data, "signature": signed_data}, previous_block.hash)
        self.chain.append(new_block)

    def sign_data(self, data):
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, data, signature):
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        try:
            self.public_key.verify(
                signature,
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

    def add_trusted_node(self, node):
        self.trusted_nodes.add(node)

    def remove_trusted_node(self, node):
        self.trusted_nodes.discard(node)

    async def create_and_distribute_backup(self, p2p_network):
        await self.backup_manager.distribute_backup(p2p_network, self.trusted_nodes)

    async def restore_from_backup(self, p2p_network):
        success = await self.backup_manager.request_backup_restoration(p2p_network, self.trusted_nodes)
        return success
