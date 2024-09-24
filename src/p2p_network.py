import asyncio


class P2PNetwork:
    def __init__(self, social_network):
        self.social_network = social_network
        self.nodes = {}  # username: ip_address
        self.node_ids = {}  # node_id: username
        self.backups = {}  # node_id: backup_data

    def add_node(self, username, ip_address, node_id):
        self.nodes[username] = ip_address
        self.node_ids[node_id] = username

    def update_node_ip(self, node_id, new_ip):
        if node_id in self.node_ids:
            username = self.node_ids[node_id]
            self.nodes[username] = new_ip

    async def send_backup(self, node_id, backup_data):
        await asyncio.sleep(0.1)  # Simulate network delay
        self.backups[node_id] = backup_data
        print(f"Backup sent to node: {node_id}")
        return True

    async def request_backup(self, node_id):
        await asyncio.sleep(0.1)  # Simulate network delay
        if node_id in self.backups:
            print(f"Backup requested from node: {node_id}")
            return self.backups[node_id]
        return None

    async def broadcast(self, sender, message):
        tasks = []
        for username, ip_address in self.nodes.items():
            if username != sender:
                tasks.append(self.send_message(ip_address, message))
        await asyncio.gather(*tasks)

    async def send_message(self, ip_address, message):
        # Simulate sending a message over the network
        await asyncio.sleep(0.1)
        print(f"Sent message to {ip_address}: {message}")
