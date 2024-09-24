import pytest
from src.social_network import SocialNetwork
from src.p2p_network import P2PNetwork
from src.blockchain import TrustedNode
import logging

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def social_network():
    return SocialNetwork()


@pytest.fixture
def p2p_network(social_network):
    return P2PNetwork(social_network)


def test_add_user(social_network):
    social_network.add_user("TestUser")
    assert "TestUser" in social_network.users
    assert "TestUser" in social_network.connections


def test_connect_users(social_network):
    social_network.add_user("User1")
    social_network.add_user("User2")
    social_network.connect_users("User1", "User2")
    assert "User2" in social_network.connections["User1"]
    assert "User1" in social_network.connections["User2"]


def test_post_data(social_network):
    social_network.add_user("TestUser")
    social_network.post_data("TestUser", "Test Post")
    assert len(social_network.users["TestUser"].chain) == 2  # Genesis block + new post
    assert social_network.users["TestUser"].chain[-1].data["data"] == "Test Post"


@pytest.mark.asyncio
async def test_propagate_data(social_network):
    social_network.add_user("User1")
    social_network.add_user("User2")
    social_network.connect_users("User1", "User2")
    await social_network.propagate_data("User1", "Test Data")
    assert len(social_network.pending_transactions) == 1
    assert social_network.pending_transactions[0]["data"] == "Test Data"


def test_consensus(social_network):
    social_network.add_user("User1")
    social_network.add_user("User2")
    social_network.pending_transactions.append({"sender": "User1", "receiver": "User2", "data": "Test Data"})
    social_network.consensus()
    assert len(social_network.pending_transactions) == 0
    assert len(social_network.users["User2"].chain) == 2  # Genesis block + new data


def test_generate_and_verify_zk_proof(social_network):
    social_network.add_user("TestUser")
    claim = "I have made a post"
    proof = social_network.generate_zk_proof("TestUser", claim)
    assert social_network.verify_zk_proof(proof, claim)


def test_add_trusted_connection(social_network, p2p_network):
    social_network.p2p_network = p2p_network
    social_network.add_user("User1")
    social_network.add_user("User2")
    p2p_network.add_node("User1", "192.168.1.1", "user1_id")
    p2p_network.add_node("User2", "192.168.1.2", "user2_id")

    social_network.add_trusted_connection("User1", "User2", "contact")

    user1_blockchain = social_network.users["User1"]
    user2_blockchain = social_network.users["User2"]

    assert any(node.node_id == "User2_to_User1" for node in user1_blockchain.trusted_nodes)
    assert any(node.node_id == "User1_to_User2" for node in user2_blockchain.trusted_nodes)


def test_add_device_as_trusted_node(social_network, p2p_network):
    social_network.p2p_network = p2p_network
    social_network.add_user("User1")
    p2p_network.add_node("User1", "192.168.1.1", "user1_id")

    device_id = "user1_device"
    device_ip = "192.168.2.1"
    social_network.users["User1"].add_trusted_node(device_id, "device", device_ip)
    p2p_network.add_node(f"User1_device", device_ip, device_id)

    user1_blockchain = social_network.users["User1"]
    assert any(node.node_id == device_id and node.node_type == "device" for node in user1_blockchain.trusted_nodes)


@pytest.mark.asyncio
async def test_create_and_distribute_backup(social_network, p2p_network):
    social_network.p2p_network = p2p_network
    social_network.add_user("TestUser")
    p2p_network.add_node("TestUser", "192.168.1.1", "testuser_id")

    # Add trusted nodes
    for i in range(social_network.total_shares):
        node_id = f"TrustedNode{i}"
        social_network.users["TestUser"].add_trusted_node(node_id, "contact", f"192.168.1.{i + 2}")
        p2p_network.add_node(f"TrustedNode{i}", f"192.168.1.{i + 2}", node_id)

    await social_network.create_and_distribute_backup("TestUser")

    # Check if backups were created for all trusted nodes
    assert len(p2p_network.backups) == social_network.total_shares


@pytest.mark.asyncio
async def test_restore_from_backup(social_network, p2p_network):
    social_network.p2p_network = p2p_network
    social_network.add_user("TestUser")
    p2p_network.add_node("TestUser", "192.168.1.1", "testuser_id")

    # Add trusted nodes
    for i in range(social_network.total_shares):
        node_id = f"TrustedNode{i}"
        social_network.users["TestUser"].add_trusted_node(node_id, "contact", f"192.168.1.{i + 2}")
        p2p_network.add_node(f"TrustedNode{i}", f"192.168.1.{i + 2}", node_id)

    # Create some data to backup
    social_network.post_data("TestUser", "Test data for backup")

    # Create and distribute backup
    await social_network.create_and_distribute_backup("TestUser")

    # Clear the user's blockchain to simulate data loss
    original_chain = social_network.users["TestUser"].chain
    social_network.users["TestUser"].chain = []

    # Attempt to restore from backup
    success = await social_network.restore_from_backup("TestUser")

    assert success, "Failed to restore from backup"
    restored_chain = social_network.users["TestUser"].chain
    assert len(restored_chain) == len(original_chain), "Restored chain length doesn't match original"

    # Log the contents of the original and restored chains for debugging
    logging.debug(f"Original chain last block data: {original_chain[-1].data}")
    logging.debug(f"Restored chain last block data: {restored_chain[-1].data}")

    # Compare the data directly
    assert restored_chain[-1].data == original_chain[-1].data, "Restored data doesn't match original"

    # Test with insufficient trusted nodes
    social_network.users["TestUser"].trusted_nodes.clear()
    success = await social_network.restore_from_backup("TestUser")
    assert not success, "Unexpectedly succeeded with insufficient trusted nodes"


if __name__ == "__main__":
    pytest.main([__file__])