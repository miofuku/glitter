import logging
from src.block import Block
from src.shamir_secret_sharing import ShamirSecretSharing, PRIME


class BackupManager:
    def __init__(self, personal_blockchain):
        self.personal_blockchain = personal_blockchain
        self.sss = ShamirSecretSharing(PRIME)

    def create_backup(self, n, k):
        return self.sss.split_secret(self.personal_blockchain, n, k)

    def restore_from_backup(self, shares):
        try:
            reconstructed_data = self.sss.reconstruct_secret(shares, len(shares))
            self.personal_blockchain.owner = reconstructed_data['owner']
            self.personal_blockchain.chain = [
                Block(
                    block['index'],
                    block['timestamp'],
                    block['data'],
                    block['previous_hash']
                )
                for block in reconstructed_data['chain']
            ]
            for block in self.personal_blockchain.chain:
                block.hash = block.calculate_hash()
            logging.info(f"Restored data for user {reconstructed_data['owner']}")
            logging.info(f"Chain length: {len(self.personal_blockchain.chain)}")
            return True
        except Exception as e:
            logging.error(f"Failed to restore from backup: {e}")
            return False



