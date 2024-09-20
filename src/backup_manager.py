import json
import asyncio
from cryptography.fernet import Fernet
import base64
from typing import List, Tuple
from secrets import randbelow
from functools import reduce
import struct


class BackupManager:
    def __init__(self, personal_blockchain):
        self.personal_blockchain = personal_blockchain

    def create_backup(self) -> bytes:
        data = {
            "owner": self.personal_blockchain.owner,
            "chain": [{
                "index": block.index,
                "timestamp": block.timestamp,
                "data": {
                    "data": block.data["data"],
                    "signature": base64.b64encode(block.data["signature"]).decode('utf-8') if block.data.get(
                        "signature") else None
                },
                "previous_hash": block.previous_hash,
                "hash": block.hash
            } for block in self.personal_blockchain.chain]
        }
        return json.dumps(data).encode()

    def restore_from_backup(self, backup_data: bytes):
        data = json.loads(backup_data.decode())
        print(f"Restored data for user {data['owner']}")
        print(f"Chain length: {len(data['chain'])}")
        # Here you would typically validate the data and update the blockchain
        # For simplicity, we're just printing the restored data

    def split_secret(self, secret: bytes, n: int, k: int) -> List[Tuple[int, bytes]]:
        """Split a secret into n shares, where k shares are required to reconstruct the secret."""
        if k > n:
            raise ValueError("k must be less than or equal to n")

        prime = 2 ** 256 - 189  # A large prime number
        secret_int = int.from_bytes(secret, 'big')
        coefficients = [secret_int] + [randbelow(prime) for _ in range(k - 1)]
        shares = []
        for i in range(1, n + 1):
            share = reduce(lambda acc, coef: (acc * i + coef) % prime, coefficients, 0)
            shares.append((i, share.to_bytes(32, 'big')))
        return shares

    def reconstruct_secret(self, shares: List[Tuple[int, bytes]], k: int) -> bytes:
        """Reconstruct the secret from k shares."""
        prime = 2 ** 256 - 189  # The same large prime number used in split_secret

        def lagrange_interpolation(x, x_s, y_s):
            def pi(vals, var, j):
                acc = 1
                for i, val in enumerate(vals):
                    if i != j:
                        acc *= (var - val) * pow(vals[j] - val, -1, prime)
                return acc % prime

            return sum(y * pi(x_s, x, j) for j, y in enumerate(y_s)) % prime

        x_s = [share[0] for share in shares[:k]]
        y_s = [int.from_bytes(share[1], 'big') for share in shares[:k]]
        secret = lagrange_interpolation(0, x_s, y_s)

        # Convert the secret back to bytes, removing any leading zero bytes
        secret_bytes = secret.to_bytes((secret.bit_length() + 7) // 8, 'big')
        return secret_bytes.lstrip(b'\x00')

    async def distribute_backup(self, p2p_network, trusted_nodes: List[str]):
        backup_data = self.create_backup()
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        encrypted_data = cipher_suite.encrypt(backup_data)

        # Combine key and encrypted data
        combined_data = key + struct.pack('>Q', len(encrypted_data)) + encrypted_data

        shares = self.split_secret(combined_data, len(trusted_nodes), (len(trusted_nodes) // 2) + 1)
        tasks = [p2p_network.send_backup(node, share) for node, share in zip(trusted_nodes, shares)]
        await asyncio.gather(*tasks)

    async def request_backup_restoration(self, p2p_network, trusted_nodes: List[str]):
        shares = []
        for node in trusted_nodes:
            share = await p2p_network.request_backup(node)
            if share:
                shares.append(share)
            if len(shares) > len(trusted_nodes) // 2:
                break
        if shares:
            reconstructed_secret = self.reconstruct_secret(shares, (len(trusted_nodes) // 2) + 1)

            key = reconstructed_secret[:32]  # Fernet key is 32 bytes
            data_length = struct.unpack('>Q', reconstructed_secret[32:40])[0]
            encrypted_data = reconstructed_secret[40:40 + data_length]

            cipher_suite = Fernet(key)
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            self.restore_from_backup(decrypted_data)
            return True
        return False