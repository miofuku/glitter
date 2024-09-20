import json
import asyncio
from typing import List
from src.block import Block
from src.shamir_secret_sharing import ShamirSecretSharing, PRIME


class BackupManager:
    def __init__(self, personal_blockchain):
        self.personal_blockchain = personal_blockchain
        self.sss = ShamirSecretSharing(PRIME)

    async def distribute_backup(self, p2p_network, trusted_nodes: List[str]):
        n = len(trusted_nodes)
        k = (n // 2) + 1  # Set threshold to majority of nodes

        shares_list = self.sss.split_secret(self.personal_blockchain, n, k)

        tasks = [p2p_network.send_backup(node, share) for node, share in zip(trusted_nodes, zip(*shares_list))]
        await asyncio.gather(*tasks)

    async def request_backup_restoration(self, p2p_network, trusted_nodes: List[str]):
        n = len(trusted_nodes)
        k = (n // 2) + 1  # Set threshold to majority of nodes

        shares_list = []
        for node in trusted_nodes:
            share = await p2p_network.request_backup(node)
            if share:
                shares_list.append(share)
            if len(shares_list) >= k:
                break

        if len(shares_list) >= k:
            try:
                reconstructed_data = self.sss.reconstruct_secret(list(zip(*shares_list)), k)
                if reconstructed_data:
                    self.restore_from_backup(reconstructed_data)
                    return True
            except Exception as e:
                print(f"Failed to reconstruct the backup: {e}")

        print("Failed to reconstruct the backup. The shares may be corrupted or insufficient.")
        return False

    def restore_from_backup(self, data: dict):
        self.personal_blockchain.owner = data['owner']
        self.personal_blockchain.chain = [
            Block(block['index'], block['timestamp'], block['data'], block['previous_hash'])
            for block in data['chain']
        ]
        for block in self.personal_blockchain.chain:
            block.hash = block.calculate_hash()
        print(f"Restored data for user {data['owner']}")
        print(f"Chain length: {len(self.personal_blockchain.chain)}")