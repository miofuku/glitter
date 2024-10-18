import random
from typing import List, Tuple
import base64
import json
import math
import logging


class ShamirSecretSharing:
    def __init__(self, prime: int):
        self.prime = prime
        self.chunk_size = (prime.bit_length() - 1) // 8  # Maximum bytes that fit in the prime

    def split_secret(self, personal_blockchain, n: int, k: int) -> List[List[Tuple[int, int]]]:
        if not isinstance(n, int) or not isinstance(k, int):
            raise TypeError("n and k must be integers")
        if n < 2:
            raise ValueError("n must be at least 2")
        if k < 2:
            raise ValueError("k must be at least 2")
        if k > n:
            raise ValueError("k must be less than or equal to n")

        # Serialize the PersonalBlockchain object
        try:
            serialized_data = json.dumps({
                "owner": personal_blockchain.owner,
                "chain": [{
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "data": block.data,
                    "previous_hash": block.previous_hash,
                    "hash": block.hash
                } for block in personal_blockchain.chain]
            })
            # Encode the entire serialized data as base64
            encoded_data = base64.b64encode(serialized_data.encode('utf-8'))
            logging.debug(f"Original encoded data length: {len(encoded_data)}")
        except (TypeError, ValueError) as e:
            logging.error(f"Failed to serialize blockchain: {e}")
            raise

        # Split the encoded data into chunks
        chunks = [encoded_data[i:i + self.chunk_size] for i in range(0, len(encoded_data), self.chunk_size)]
        logging.debug(f"Number of chunks: {len(chunks)}")

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

        logging.debug(f"Number of share lists: {len(shares_list)}")
        return shares_list

    def reconstruct_secret(self, shares_list: List[List[Tuple[int, int]]], k: int) -> dict:
        if not shares_list or not all(shares_list):
            raise ValueError("Invalid shares_list")
        if not isinstance(k, int) or k < 2:
            raise ValueError("k must be an integer greater than or equal to 2")

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

        # Combine chunks and remove any padding
        reconstructed_data = b''.join(reconstructed_chunks).rstrip(b'\x00')
        logging.debug(f"Reconstructed data length: {len(reconstructed_data)} bytes")

        # Ensure the data length is divisible by 3 for proper base64 encoding
        padding_length = (3 - len(reconstructed_data) % 3) % 3
        padded_data = reconstructed_data + b'\x00' * padding_length
        logging.debug(f"Padded data length: {len(padded_data)} bytes")

        try:
            base64_encoded = base64.b64encode(padded_data).decode('utf-8')
            json_data = json.loads(base64.b64decode(base64_encoded).decode('utf-8').rstrip('\x00'))
            logging.debug(f"Parsed JSON data keys: {list(json_data.keys())}")
            return json_data
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing reconstructed data: {e}")
            logging.error(f"Problematic data (first 200 chars): {padded_data[:200]}...")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during reconstruction: {e}")
            raise

    def _mod_inverse(self, x: int) -> int:
        return pow(x, self.prime - 2, self.prime)


# Use a smaller prime for each chunk, but still large enough for security
PRIME = 2 ** 256 - 189  # This is a 256-bit prime number
