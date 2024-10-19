import asyncio
import aiohttp
from aiohttp import web
import json
import logging


class P2PNetwork:
    def __init__(self, host='localhost'):
        self.host = host
        self.nodes = {}  # username: (port, node_id)
        self.app = web.Application()
        self.app.router.add_post('/', self.receive_data)
        self.app.router.add_get('/backup', self.handle_backup_request)
        self.runner = None
        self.backups = {}  # node_id: backup_data

    async def start(self, port):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, port)
        await site.start()
        logging.info(f"P2P network node started on {self.host}:{port}")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()

    def add_node(self, username, port, node_id):
        self.nodes[username] = (port, node_id)

    async def receive_data(self, request):
        data = await request.json()
        sender = data.get('sender')
        message = data.get('message')
        logging.info(f"Received data from {sender}: {message}")
        return web.Response(text="Data received")

    async def send_data(self, receiver_username, sender_username, data):
        if receiver_username not in self.nodes:
            raise ValueError(f"Unknown receiver: {receiver_username}")

        receiver_port, _ = self.nodes[receiver_username]
        message = {
            'sender': sender_username,
            'message': data
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f'http://{self.host}:{receiver_port}', json=message) as response:
                    if response.status == 200:
                        logging.info(f"Data sent to {receiver_username} successfully")
                    else:
                        logging.error(f"Failed to send data to {receiver_username}. Status: {response.status}")
        except Exception as e:
            logging.error(f"Network error when sending data to {receiver_username}: {str(e)}")

    async def broadcast(self, sender_username, data):
        tasks = []
        for username in self.nodes:
            if username != sender_username:
                tasks.append(self.send_data(username, sender_username, data))
        await asyncio.gather(*tasks)

    async def send_backup(self, node_id, backup_data):
        self.backups[node_id] = backup_data
        logging.info(f"Backup sent to node: {node_id}")
        return True

    async def request_backup(self, node_id):
        if node_id in self.backups:
            logging.info(f"Backup found for node: {node_id}")
            return self.backups[node_id]
        logging.warning(f"No backup found for node: {node_id}")
        return None

    async def handle_backup_request(self, request):
        node_id = request.query.get('node_id')
        if node_id in self.backups:
            logging.info(f"Serving backup for node: {node_id}")
            return web.json_response(self.backups[node_id])
        logging.warning(f"Backup not found for node: {node_id}")
        return web.Response(status=404, text="Backup not found")