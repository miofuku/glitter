import asyncio

class P2PNetwork:
    def __init__(self, social_network):
        self.social_network = social_network
        self.nodes = {}

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