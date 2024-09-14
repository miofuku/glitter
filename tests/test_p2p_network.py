import pytest

from src.p2p_network import P2PNetwork
from src.social_network import SocialNetwork

@pytest.fixture
def p2p_network():
    social_network = SocialNetwork()
    return P2PNetwork(social_network)

def test_add_node(p2p_network):
    p2p_network.add_node("Alice", "192.168.1.1")
    assert "Alice" in p2p_network.nodes
    assert p2p_network.nodes["Alice"] == "192.168.1.1"

@pytest.mark.asyncio
async def test_send_backup(p2p_network):
    p2p_network.add_node("Alice", "192.168.1.1")
    await p2p_network.send_backup("Alice", b"Test backup data")
    assert "Alice" in p2p_network.backups
    assert p2p_network.backups["Alice"] == b"Test backup data"

@pytest.mark.asyncio
async def test_request_backup(p2p_network):
    p2p_network.add_node("Alice", "192.168.1.1")
    p2p_network.backups["Alice"] = b"Test backup data"
    backup_data = await p2p_network.request_backup("Alice")
    assert backup_data == b"Test backup data"

@pytest.mark.asyncio
async def test_broadcast(p2p_network):
    p2p_network.add_node("Alice", "192.168.1.1")
    p2p_network.add_node("Bob", "192.168.1.2")
    await p2p_network.broadcast("Charlie", "Test message")
    # In a real test, we would assert on the effects of the broadcast
    # For now, we're just checking that it doesn't raise an exception
    assert True