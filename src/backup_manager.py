import logging
import asyncio
from src.block import Block
from src.shamir_secret_sharing import ShamirSecretSharing, PRIME


class BackupManager:
    def __init__(self, personal_blockchain):
        self.personal_blockchain = personal_blockchain
        self.sss = ShamirSecretSharing(PRIME)

    async def distribute_backup(self, p2p_network, trusted_nodes, n, k):
        shares_list = self.sss.split_secret(self.personal_blockchain, n, k)
        tasks = [p2p_network.send_backup(node.node_id, share) for node, share in zip(trusted_nodes, zip(*shares_list))]
        await asyncio.gather(*tasks)

    async def request_backup_restoration(self, p2p_network, trusted_nodes, k):
        logging.info(f"Starting backup restoration. Required shares: {k}")
        shares_list = []
        for node in trusted_nodes:
            share = await p2p_network.request_backup(node.node_id)
            if share:
                shares_list.append(share)
                logging.info(f"Received share from node {node.node_id}")
            if len(shares_list) >= k:
                break

        logging.info(f"Collected {len(shares_list)} shares out of {k} required")

        if len(shares_list) >= k:
            try:
                logging.debug(f"Attempting reconstruction with {len(shares_list)} share lists")
                reconstructed_data = self.sss.reconstruct_secret(list(zip(*shares_list)), k)
                logging.debug(f"Reconstructed data keys: {list(reconstructed_data.keys())}")
                if reconstructed_data:
                    self.restore_from_backup(reconstructed_data)
                    logging.info("Successfully reconstructed and restored the backup")
                    return True
            except Exception as e:
                logging.error(f"Failed to reconstruct the backup: {e}")
                logging.error(f"Number of shares: {len(shares_list)}, First share: {shares_list[0][:2]}...")
                return False

        logging.error("Failed to reconstruct the backup. Insufficient shares collected.")
        return False

    def restore_from_backup(self, data: dict):
        self.personal_blockchain.owner = data['owner']
        self.personal_blockchain.chain = [
            Block(
                block['index'],
                block['timestamp'],
                block['data'],  # Now this should already be decoded
                block['previous_hash']
            )
            for block in data['chain']
        ]
        for block in self.personal_blockchain.chain:
            block.hash = block.calculate_hash()
        logging.info(f"Restored data for user {data['owner']}")
        logging.info(f"Chain length: {len(self.personal_blockchain.chain)}")
