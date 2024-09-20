import random
from typing import List, Tuple
import base64
import json


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
                "data": base64.b64encode(block.data).decode('utf-8') if isinstance(block.data, bytes) else block.data,
                "previous_hash": block.previous_hash,
                "hash": block.hash
            } for block in personal_blockchain.chain]
        })

        # Encode the serialized data as base64
        secret_b64 = base64.b64encode(serialized_data.encode('utf-8'))

        # Split the base64 string into chunks
        chunks = [secret_b64[i:i + self.chunk_size] for i in range(0, len(secret_b64), self.chunk_size)]

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

            chunk = secret.to_bytes(self.chunk_size, 'big').rstrip(b'\x00')
            reconstructed_chunks.append(chunk)

        # Combine chunks and decode
        reconstructed_b64 = b''.join(reconstructed_chunks)
        decoded_bytes = base64.b64decode(reconstructed_b64)
        reconstructed_data = json.loads(decoded_bytes.decode('utf-8'))

        # Decode base64-encoded data in blocks
        for block in reconstructed_data['chain']:
            if isinstance(block['data'], str):
                try:
                    block['data'] = base64.b64decode(block['data'])
                except:
                    pass  # If it's not base64-encoded, leave it as is

        return reconstructed_data


# Use a smaller prime for each chunk, but still large enough for security
PRIME = 2 ** 256 - 189  # This is a 256-bit prime number