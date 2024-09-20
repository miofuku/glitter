import pytest
from unittest.mock import AsyncMock, Mock
from src.blockchain import PersonalBlockchain, Block
from src.shamir_secret_sharing import ShamirSecretSharing, PRIME
import base64
import json

@pytest.fixture
def personal_blockchain():
    return PersonalBlockchain("TestUser")

def test_create_genesis_block(personal_blockchain):
    assert len(personal_blockchain.chain) == 1
    assert personal_blockchain.chain[0].index == 0
    assert personal_blockchain.chain[0].previous_hash == "0"
    assert isinstance(personal_blockchain.chain[0].data["data"], dict)
    assert "owner" in personal_blockchain.chain[0].data["data"]
    assert "creation_time" in personal_blockchain.chain[0].data["data"]
    assert "blockchain_version" in personal_blockchain.chain[0].data["data"]
    assert "user_message" in personal_blockchain.chain[0].data["data"]

def test_add_block(personal_blockchain):
    personal_blockchain.add_block({"data": "Test Data"})
    assert len(personal_blockchain.chain) == 2
    assert personal_blockchain.chain[-1].data["data"] == {"data": "Test Data"}

def test_verify_signature(personal_blockchain):
    data = "Test Data"
    signature = personal_blockchain.sign_data(data)
    assert personal_blockchain.verify_signature(data, base64.b64decode(signature))

def test_add_and_remove_trusted_node(personal_blockchain):
    personal_blockchain.add_trusted_node("TestNode")
    assert "TestNode" in personal_blockchain.trusted_nodes
    personal_blockchain.remove_trusted_node("TestNode")
    assert "TestNode" not in personal_blockchain.trusted_nodes

@pytest.mark.asyncio
async def test_create_and_distribute_backup(personal_blockchain):
    mock_p2p_network = Mock()
    mock_p2p_network.send_backup = AsyncMock()

    personal_blockchain.add_trusted_node("TestNode")
    await personal_blockchain.create_and_distribute_backup(mock_p2p_network)

    mock_p2p_network.send_backup.assert_called()

@pytest.mark.asyncio
async def test_restore_from_backup(personal_blockchain):
    # Create a mock backup
    sss = ShamirSecretSharing(PRIME)
    mock_backup_data = {
        "owner": "TestUser",
        "chain": [{
            "index": 0,
            "timestamp": 1000000,
            "data": {
                "data": {
                    "owner": "TestUser",
                    "creation_time": 1000000,
                    "blockchain_version": "1.0",
                    "user_message": "Default genesis message"
                }
            },
            "previous_hash": "0",
            "hash": "mock_hash"
        }]
    }
    shares = sss.split_secret(mock_backup_data, 3, 2)  # 3 shares, 2 required for reconstruction

    mock_p2p_network = Mock()
    mock_p2p_network.request_backup = AsyncMock(side_effect=[list(share) for share in zip(*shares)])

    personal_blockchain.add_trusted_node("TestNode1")
    personal_blockchain.add_trusted_node("TestNode2")
    personal_blockchain.add_trusted_node("TestNode3")

    # Clear the blockchain
    personal_blockchain.chain = []

    success = await personal_blockchain.restore_from_backup(mock_p2p_network)

    assert success
    assert len(personal_blockchain.chain) == 1
    assert personal_blockchain.chain[0].data["data"]["owner"] == "TestUser"
    assert personal_blockchain.chain[0].data["data"]["blockchain_version"] == "1.0"
    assert personal_blockchain.chain[0].data["data"]["user_message"] == "Default genesis message"
    assert isinstance(personal_blockchain.chain[0].data["data"]["creation_time"], (int, float))

if __name__ == "__main__":
    pytest.main([__file__])