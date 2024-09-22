import pytest
from unittest.mock import AsyncMock, Mock
from src.blockchain import PersonalBlockchain, Block
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
    personal_blockchain.add_trusted_node("TestNode")
    assert "TestNode" in personal_blockchain.trusted_nodes
    personal_blockchain.remove_trusted_node("TestNode")
    assert "TestNode" not in personal_blockchain.trusted_nodes


@pytest.mark.asyncio
async def test_create_and_distribute_backup(personal_blockchain):
    mock_p2p_network = Mock()
    mock_p2p_network.send_backup = AsyncMock()

    n, k = 5, 3
    trusted_nodes = [f"TestNode{i}" for i in range(n)]
    for node in trusted_nodes:
        personal_blockchain.add_trusted_node(node)

    await personal_blockchain.create_and_distribute_backup(mock_p2p_network, trusted_nodes, n, k)

    assert mock_p2p_network.send_backup.call_count == n


@pytest.mark.asyncio
async def test_restore_from_backup(personal_blockchain):
    # Create a mock backup
    sss = ShamirSecretSharing(PRIME)
    mock_blockchain = PersonalBlockchain("TestUser")
    mock_blockchain.add_block({"data": "Test Block"})
    n, k = 5, 3
    shares_list = sss.split_secret(mock_blockchain, n, k)

    logging.debug(f"Number of share lists: {len(shares_list)}")
    logging.debug(f"Number of shares in first list: {len(shares_list[0])}")

    # Test reconstruction immediately after splitting
    try:
        reconstructed_data = sss.reconstruct_secret(shares_list, k)
        logging.debug(f"Immediate reconstruction successful. Keys: {list(reconstructed_data.keys())}")
        assert reconstructed_data['owner'] == mock_blockchain.owner
        assert len(reconstructed_data['chain']) == len(mock_blockchain.chain)
    except Exception as e:
        logging.error(f"Immediate reconstruction failed: {e}")
        pytest.fail(f"Immediate reconstruction failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
