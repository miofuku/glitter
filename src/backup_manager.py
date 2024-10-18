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
            serialized_shares = self.sss.serialize_shares(shares)
            logging.info(f"Created backup with {n} shares")
            logging.debug(f"Serialized shares length: {len(serialized_shares)}")
            return serialized_shares
        except Exception as e:
            logging.error(f"Failed to create backup: {str(e)}")
            raise

    def restore_from_backup(self, serialized_shares, k):
        try:
            logging.debug(f"Restoring from serialized shares of length: {len(serialized_shares)}")
            shares = self.sss.deserialize_shares(serialized_shares)
            if len(shares[0]) < k:
                logging.error(f"Insufficient shares for restoration: {len(shares[0])} < {k}")
                return False
            reconstructed_data = self.sss.reconstruct_secret(shares, k)
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
            logging.error(f"Failed to restore from backup: {str(e)}")
            logging.error(f"Serialized shares (first 100 chars): {serialized_shares[:100]}...")
            return False