import asyncio
from typing import Dict, List
from src.blockchain import PersonalBlockchain
from src.p2p_network import P2PNetwork
import logging


class SocialNetwork:
    def __init__(self, host='localhost', start_port=8000):
        self.users: Dict[str, PersonalBlockchain] = {}
        self.connections: Dict[str, List[str]] = {}
        self.p2p_networks: Dict[str, P2PNetwork] = {}
        self.host = host
        self.start_port = start_port
        self.backup_threshold = 3  # This is 'k'
        self.total_shares = 4  # This is 'n'

    async def start(self):
        start_tasks = [p2p_network.start(self.start_port + i)
                       for i, p2p_network in enumerate(self.p2p_networks.values())]
        await asyncio.gather(*start_tasks)

    async def stop(self):
        stop_tasks = [p2p_network.stop() for p2p_network in self.p2p_networks.values()]
        await asyncio.gather(*stop_tasks)

    def add_user(self, username):
        if username not in self.users:
            self.users[username] = PersonalBlockchain(username)
            self.connections[username] = []
            new_p2p_network = P2PNetwork(self.host)
            self.p2p_networks[username] = new_p2p_network
            port = self.start_port + len(self.users) - 1
            new_p2p_network.add_node(username, port, f"{username}_id")
            logging.info(f"Added user: {username}")

    def connect_users(self, user1, user2):
        if user1 in self.users and user2 in self.users:
            if user2 not in self.connections[user1]:
                self.connections[user1].append(user2)
                self.connections[user2].append(user1)
                # Add users to each other's P2P networks
                self.p2p_networks[user1].add_node(user2, self.p2p_networks[user2].nodes[user2][0], f"{user2}_id")
                self.p2p_networks[user2].add_node(user1, self.p2p_networks[user1].nodes[user1][0], f"{user1}_id")
                # Set up trusted connections
                self.add_trusted_connection(user1, user2, "contact")
                self.add_trusted_connection(user2, user1, "contact")
                logging.info(f"Connected users {user1} and {user2}, and set up trusted connections")
            else:
                logging.info(f"Users {user1} and {user2} are already connected")

    def add_trusted_connection(self, user1, user2, node_type):
        if user1 in self.users and user2 in self.users:
            user1_blockchain = self.users[user1]
            user2_port, user2_id = self.p2p_networks[user2].nodes[user2]
            user1_blockchain.add_trusted_node(user2_id, node_type, f"{self.host}:{user2_port}")
            logging.info(f"Added trusted connection for {user1}: {user2_id} ({node_type})")

    def post_data(self, username, data):
        if username in self.users:
            blockchain = self.users[username]
            blockchain.add_block(data)
            logging.info(f"Posted data for {username}: {data}")

    async def propagate_data(self, username, data):
        if username in self.users:
            await self.p2p_networks[username].broadcast(username, data)
            logging.info(f"Propagated data from {username}")

    async def create_and_distribute_backup(self, username):
        if username in self.users:
            user_blockchain = self.users[username]
            trusted_nodes = user_blockchain.trusted_nodes

            if len(trusted_nodes) < self.total_shares:
                logging.warning(
                    f"Not enough trusted nodes for {username}. Have {len(trusted_nodes)}, need {self.total_shares}")
                return False

            try:
                serialized_shares = user_blockchain.backup_manager.create_backup(self.total_shares,
                                                                                 self.backup_threshold)
                logging.debug(f"Created serialized shares of length: {len(serialized_shares)}")

                for i, node in enumerate(trusted_nodes[:self.total_shares]):
                    await self.p2p_networks[username].send_backup(node.node_id, serialized_shares)
                    logging.debug(f"Sent backup to trusted node {i + 1}/{self.total_shares}")

                logging.info(f"Created and distributed backup for {username}")
                return True
            except Exception as e:
                logging.error(f"Error in create_and_distribute_backup: {str(e)}")
                return False

    async def restore_from_backup(self, username):
        if username in self.users:
            user_blockchain = self.users[username]
            trusted_nodes = user_blockchain.trusted_nodes

            serialized_shares = None
            for i, node in enumerate(trusted_nodes):
                try:
                    share = await self.p2p_networks[username].request_backup(node.node_id)
                    if share:
                        serialized_shares = share
                        logging.debug(f"Retrieved backup from trusted node {i + 1}")
                        break
                except Exception as e:
                    logging.error(f"Error retrieving backup from node {i + 1}: {str(e)}")

            if serialized_shares:
                logging.debug(f"Retrieved serialized shares of length: {len(serialized_shares)}")
                success = user_blockchain.backup_manager.restore_from_backup(serialized_shares, self.backup_threshold)
                if success:
                    logging.info(f"Successfully restored backup for {username}")
                else:
                    logging.error(f"Failed to restore backup for {username}")
                return success
            else:
                logging.error(f"No backup shares found for {username}")
                return False
        return False
    def get_trusted_nodes_count(self, username):
        if username in self.users:
            return len(self.users[username].trusted_nodes)
        return 0

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

