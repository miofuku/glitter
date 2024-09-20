import time
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from src.block import Block
from src.backup_manager import BackupManager

class PersonalBlockchain:
    def __init__(self, owner, genesis_message=None):
        self.owner = owner
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self.chain = [self.create_genesis_block(genesis_message)]
        self.backup_manager = BackupManager(self)
        self.trusted_nodes = set()

    def create_genesis_block(self, user_message=None):
        genesis_data = {
            "owner": self.owner,
            "creation_time": time.time(),
            "blockchain_version": "1.0",
            "user_message": user_message.decode('utf-8') if isinstance(user_message, bytes) else user_message or "Default genesis message"
        }
        signed_data = self.sign_data(json.dumps(genesis_data))
        return Block(0, time.time(), {"data": genesis_data, "signature": signed_data}, "0")

    def sign_data(self, data):
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        elif isinstance(data, bytes):
            data = data.decode('utf-8')
        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    def add_block(self, data):
        previous_block = self.chain[-1]
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        signed_data = self.sign_data(data)
        new_block = Block(len(self.chain), time.time(), {"data": data, "signature": signed_data}, previous_block.hash)
        self.chain.append(new_block)

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
        await self.backup_manager.distribute_backup(p2p_network, list(self.trusted_nodes))

    async def restore_from_backup(self, p2p_network):
        success = await self.backup_manager.request_backup_restoration(p2p_network, list(self.trusted_nodes))
        return success
