import pytest
from src.blockchain import Block, PersonalBlockchain

def test_block_creation():
    block = Block(1, 123456, {"data": "Test Data", "signature": b"test_signature"}, "previous_hash")
    assert block.index == 1
    assert block.timestamp == 123456
    assert block.data == {"data": "Test Data", "signature": b"test_signature"}
    assert block.previous_hash == "previous_hash"
    assert isinstance(block.hash, str)

def test_personal_blockchain_creation():
    blockchain = PersonalBlockchain("TestUser")
    assert len(blockchain.chain) == 1
    assert blockchain.owner == "TestUser"
    assert blockchain.chain[0].data["data"] == "Genesis Block"

def test_add_block():
    blockchain = PersonalBlockchain("TestUser")
    blockchain.add_block("Test Data")
    assert len(blockchain.chain) == 2
    assert blockchain.chain[1].data["data"] == "Test Data"

def test_sign_and_verify_data():
    blockchain = PersonalBlockchain("TestUser")
    data = "Test Data"
    signature = blockchain.sign_data(data)
    assert blockchain.verify_signature(data, signature)

def test_add_and_remove_trusted_node():
    blockchain = PersonalBlockchain("TestUser")
    blockchain.add_trusted_node("TrustedUser")
    assert "TrustedUser" in blockchain.trusted_nodes
    blockchain.remove_trusted_node("TrustedUser")
    assert "TrustedUser" not in blockchain.trusted_nodes