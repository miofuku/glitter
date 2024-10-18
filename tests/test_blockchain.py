import pytest
from unittest.mock import AsyncMock, Mock
from src.blockchain import PersonalBlockchain, Block, TrustedNode
from src.shamir_secret_sharing import ShamirSecretSharing, PRIME
import base64
import logging

logging.basicConfig(level=logging.INFO)


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
    personal_blockchain.add_trusted_node("TestNode", "contact", "192.168.1.1")
    assert any(node.node_id == "TestNode" for node in personal_blockchain.trusted_nodes)
    personal_blockchain.remove_trusted_node("TestNode")
    assert all(node.node_id != "TestNode" for node in personal_blockchain.trusted_nodes)


@pytest.mark.asyncio
async def test_create_and_distribute_backup(personal_blockchain):
    mock_p2p_network = Mock()
    mock_p2p_network.send_backup = AsyncMock()

    n, k = 5, 3
    trusted_nodes = [TrustedNode(f"TestNode{i}", "contact", f"192.168.1.{i}") for i in range(n)]
    for node in trusted_nodes:
        personal_blockchain.add_trusted_node(node.node_id, node.node_type, node.ip_address)

    serialized_shares = personal_blockchain.backup_manager.create_backup(n, k)

    for node in trusted_nodes:
        await mock_p2p_network.send_backup(node.node_id, serialized_shares)

    assert mock_p2p_network.send_backup.call_count == n


@pytest.mark.asyncio
async def test_restore_from_backup(personal_blockchain):
    # Create a mock backup
    sss = ShamirSecretSharing(PRIME)
    mock_blockchain = PersonalBlockchain("TestUser")
    mock_blockchain.add_block({"data": "Test Block"})
    n, k = 5, 3
    shares = sss.split_secret(mock_blockchain, n, k)
    serialized_shares = sss.serialize_shares(shares)

    # Test reconstruction
    try:
        success = personal_blockchain.backup_manager.restore_from_backup(serialized_shares, k)
        assert success, "Failed to restore from backup"
        reconstructed_blockchain = personal_blockchain
        assert reconstructed_blockchain.owner == mock_blockchain.owner
        assert len(reconstructed_blockchain.chain) == len(mock_blockchain.chain)
        assert reconstructed_blockchain.chain[-1].data == mock_blockchain.chain[-1].data
    except Exception as e:
        logging.error(f"Reconstruction failed: {e}")
        pytest.fail(f"Reconstruction failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
