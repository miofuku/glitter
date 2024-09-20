import hashlib
import base64
import json



class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = self.preprocess_data(data)
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.serialize_data(self.data)}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    @staticmethod
    def serialize_data(data):
        if isinstance(data, bytes):
            return base64.b64encode(data).decode('utf-8')
        elif isinstance(data, dict):
            return json.dumps({k: Block.serialize_data(v) for k, v in data.items()}, sort_keys=True)
        else:
            return str(data)

    @staticmethod
    def preprocess_data(data):
        if isinstance(data, dict):
            return {k: Block.preprocess_data(v) for k, v in data.items()}
        elif isinstance(data, bytes):
            return base64.b64encode(data).decode('utf-8')
        else:
            return data