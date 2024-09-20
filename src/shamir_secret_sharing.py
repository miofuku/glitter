import random
from typing import List, Tuple
import base64
import json
import math

class ShamirSecretSharing:
    def __init__(self, prime: int):
        self.prime = prime
        self.chunk_size = (prime.bit_length() - 1) // 8  # Maximum bytes that fit in the prime

    def _mod_inverse(self, x: int) -> int:
        return pow(x, self.prime - 2, self.prime)

    def split_secret(self, personal_blockchain, n: int, k: int) -> List[List[Tuple[int, int]]]:
        if k > n:
            raise ValueError("k must be less than or equal to n")

        # Serialize the PersonalBlockchain object
        serialized_data = json.dumps({
            "owner": personal_blockchain.owner,
            "chain": [{
                "index": block.index,
                "timestamp": block.timestamp,
                "data": base64.b64encode(json.dumps(block.data).encode('utf-8')).decode('utf-8'),
                "previous_hash": block.previous_hash,
                "hash": block.hash
            } for block in personal_blockchain.chain]
        }).encode('utf-8')

        # Split the serialized data into chunks
        chunks = [serialized_data[i:i + self.chunk_size] for i in range(0, len(serialized_data), self.chunk_size)]

        # Apply Shamir's Secret Sharing to each chunk
        shares_list = []
        for chunk in chunks:
            secret_int = int.from_bytes(chunk, 'big')
            coefficients = [secret_int] + [random.randint(0, self.prime - 1) for _ in range(k - 1)]
            shares = []
            for i in range(1, n + 1):
                x = i
                y = sum((coeff * pow(x, power, self.prime)) for power, coeff in enumerate(coefficients)) % self.prime
                shares.append((x, y))
            shares_list.append(shares)

        return shares_list

    def reconstruct_secret(self, shares_list: List[List[Tuple[int, int]]], k: int) -> dict:
        reconstructed_chunks = []

        for shares in shares_list:
            if len(shares) < k:
                raise ValueError("Not enough shares to reconstruct the secret")

            secret = 0
            for i, (x_i, y_i) in enumerate(shares[:k]):
                numerator, denominator = 1, 1
                for j, (x_j, _) in enumerate(shares[:k]):
                    if i != j:
                        numerator = (numerator * -x_j) % self.prime
                        denominator = (denominator * (x_i - x_j)) % self.prime

                secret += y_i * numerator * self._mod_inverse(denominator)
                secret %= self.prime

            # Convert to bytes, handling potential overflow
            byte_length = math.ceil(secret.bit_length() / 8)
            chunk = secret.to_bytes(byte_length, 'big')
            reconstructed_chunks.append(chunk)

        # Combine chunks and decode
        reconstructed_data = b''.join(reconstructed_chunks)
        json_data = json.loads(reconstructed_data.decode('utf-8'))

        # Decode base64-encoded data in blocks
        for block in json_data['chain']:
            block['data'] = json.loads(base64.b64decode(block['data']).decode('utf-8'))

        return json_data

# Use a smaller prime for each chunk, but still large enough for security
PRIME = 2 ** 256 - 189  # This is a 256-bit prime number