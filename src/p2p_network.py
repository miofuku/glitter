import asyncio

class P2PNetwork:
    def __init__(self, social_network):
        self.social_network = social_network
        self.nodes = {}
        self.backups = {}

    def add_node(self, username, ip_address):
        self.nodes[username] = ip_address

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

    async def send_backup(self, node, backup_data):
        # Simulate sending a backup to another node
        await asyncio.sleep(0.1)
        self.backups[node] = backup_data
        print(f"Backup sent to node: {node}")

    async def request_backup(self, node):
        # Simulate requesting a backup from another node
        await asyncio.sleep(0.1)
        return self.backups.get(node)