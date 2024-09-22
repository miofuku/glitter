import asyncio
from typing import Dict, List
from src.blockchain import PersonalBlockchain


class SocialNetwork:
    def __init__(self):
        self.users: Dict[str, PersonalBlockchain] = {}
        self.connections: Dict[str, List[str]] = {}
        self.pending_transactions: List[Dict] = []
        self.p2p_network = None
        self.backup_threshold = 3  # This is 'k'
        self.total_shares = 5  # This is 'n'

    def add_user(self, username):
        if username not in self.users:
            self.users[username] = PersonalBlockchain(username)
            self.connections[username] = []

    def connect_users(self, user1, user2):
        if user1 in self.users and user2 in self.users:
            self.connections[user1].append(user2)
            self.connections[user2].append(user1)

    def post_data(self, username, data):
        if username in self.users:
            blockchain = self.users[username]
            blockchain.add_block(data)

    async def propagate_data(self, username, data):
        if username in self.users:
            connections = self.connections[username]
            await asyncio.gather(*[self.send_data(conn, username, data) for conn in connections])

    async def send_data(self, receiver, sender, data):
        # Simulate network delay
        await asyncio.sleep(0.1)
        self.receive_data(receiver, sender, data)

    def receive_data(self, receiver, sender, data):
        self.pending_transactions.append({"sender": sender, "receiver": receiver, "data": data})

    def consensus(self):
        # Simple majority consensus
        for transaction in self.pending_transactions:
            if self.validate_transaction(transaction):
                self.users[transaction["receiver"]].add_block(transaction["data"])
        self.pending_transactions.clear()

    def validate_transaction(self, transaction):
        # In a real implementation, this would involve checking with multiple nodes
        return True

    def generate_zk_proof(self, username, claim):
        # Placeholder implementation
        print(f"Generating proof for claim: {claim} by user: {username}")
        return f"Proof for claim: {claim}"

    def verify_zk_proof(self, proof, claim):
        # Placeholder implementation
        print(f"Verifying proof: {proof} for claim: {claim}")
        return True  # Always returns True in this placeholder

    def add_trusted_connection(self, user1, user2):
        if user1 in self.users and user2 in self.users:
            self.users[user1].add_trusted_node(user2)
            self.users[user2].add_trusted_node(user1)

    async def create_and_distribute_backup(self, username):
        if username in self.users and self.p2p_network:
            user_blockchain = self.users[username]
            trusted_nodes = list(user_blockchain.trusted_nodes)

            if len(trusted_nodes) < self.total_shares:
                print(f"Warning: Not enough trusted nodes. Have {len(trusted_nodes)}, need {self.total_shares}")
                return

            await user_blockchain.create_and_distribute_backup(
                self.p2p_network,
                trusted_nodes,
                self.total_shares,
                self.backup_threshold
            )
    async def restore_from_backup(self, username):
        if username in self.users and self.p2p_network:
            user_blockchain = self.users[username]
            trusted_nodes = list(user_blockchain.trusted_nodes)
            success = await user_blockchain.restore_from_backup(
                self.p2p_network,
                trusted_nodes,
                self.backup_threshold
            )
            return success
        return False
