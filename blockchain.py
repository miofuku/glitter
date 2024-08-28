import hashlib
import time
import json

class Block:
    def __init__(self, index, previous_hash, timestamp, data, proof):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.proof = proof

    def hash_block(self):
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", time.time(), "Genesis Block", 100)
        genesis_block.hash = genesis_block.hash_block()
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data, proof):
        previous_block = self.get_latest_block()
        new_block = Block(len(self.chain), previous_block.hash, time.time(), data, proof)
        new_block.hash = new_block.hash_block()
        self.chain.append(new_block)

    def proof_of_work(self, last_proof):
        incrementor = last_proof + 1
        while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
            incrementor += 1
        return incrementor

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.previous_hash != previous_block.hash_block():
                return False
        return True

# Example usage:
blockchain = Blockchain()
print(f"Genesis Block Hash: {blockchain.get_latest
