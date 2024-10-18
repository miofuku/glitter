import logging
from src.block import Block
from src.shamir_secret_sharing import ShamirSecretSharing, PRIME


class BackupManager:
    def __init__(self, personal_blockchain):
        self.personal_blockchain = personal_blockchain
        self.sss = ShamirSecretSharing(PRIME)

    def create_backup(self, n, k):
        try:
            shares = self.sss.split_secret(self.personal_blockchain, n, k)
            logging.info(f"Created backup with {len(shares)} share lists")
            logging.debug(f"First share list length: {len(shares[0])}")
            return shares
        except Exception as e:
            logging.error(f"Failed to create backup: {e}")
            raise

    def restore_from_backup(self, shares):
        try:
            logging.debug(f"Restoring from {len(shares)} share lists")
            logging.debug(f"First share list length: {len(shares[0])}")
            reconstructed_data = self.sss.reconstruct_secret(shares, len(shares[0]))
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
            logging.error(f"Shares: {shares}")
            return False
