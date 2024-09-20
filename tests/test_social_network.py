import pytest
from src.social_network import SocialNetwork
from src.p2p_network import P2PNetwork


@pytest.fixture
def social_network():
    return SocialNetwork()


@pytest.fixture
def p2p_network():
    return P2PNetwork(None)


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


@pytest.mark.asyncio
async def test_propagate_data(social_network):
    social_network.add_user("User1")
    social_network.add_user("User2")
    social_network.connect_users("User1", "User2")
    await social_network.propagate_data("User1", "Test Data")
    assert len(social_network.pending_transactions) == 1


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


def test_add_trusted_connection(social_network):
    social_network.add_user("User1")
    social_network.add_user("User2")
    social_network.add_trusted_connection("User1", "User2")
    assert "User2" in social_network.users["User1"].trusted_nodes
    assert "User1" in social_network.users["User2"].trusted_nodes


@pytest.mark.asyncio
async def test_create_and_distribute_backup(social_network, p2p_network):
    social_network.p2p_network = p2p_network
    social_network.add_user("TestUser")
    social_network.users["TestUser"].add_trusted_node("TrustedNode")
    await social_network.create_and_distribute_backup("TestUser")
    assert len(p2p_network.backups) > 0


@pytest.mark.asyncio
async def test_restore_from_backup(social_network, p2p_network):
    social_network.p2p_network = p2p_network
    social_network.add_user("TestUser")
    social_network.users["TestUser"].add_trusted_node("TrustedNode")
    await social_network.create_and_distribute_backup("TestUser")
    success = await social_network.restore_from_backup("TestUser")
    assert success