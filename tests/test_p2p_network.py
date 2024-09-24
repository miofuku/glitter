import pytest
from src.p2p_network import P2PNetwork
from src.social_network import SocialNetwork

@pytest.fixture
def p2p_network():
    return P2PNetwork(SocialNetwork())

def test_add_node(p2p_network):
    p2p_network.add_node("TestUser", "192.168.1.1", "test_user_id")
    assert "TestUser" in p2p_network.nodes
    assert p2p_network.nodes["TestUser"] == "192.168.1.1"
    assert "test_user_id" in p2p_network.node_ids
    assert p2p_network.node_ids["test_user_id"] == "TestUser"

@pytest.mark.asyncio
async def test_broadcast(p2p_network, capsys):
    p2p_network.add_node("User1", "192.168.1.1", "user1_id")
    p2p_network.add_node("User2", "192.168.1.2", "user2_id")
    await p2p_network.broadcast("Sender", "Test Message")
    captured = capsys.readouterr()
    assert "Sent message to 192.168.1.1: Test Message" in captured.out
    assert "Sent message to 192.168.1.2: Test Message" in captured.out

@pytest.mark.asyncio
async def test_send_message(p2p_network, capsys):
    await p2p_network.send_message("192.168.1.1", "Test Message")
    captured = capsys.readouterr()
    assert "Sent message to 192.168.1.1: Test Message" in captured.out

@pytest.mark.asyncio
async def test_send_and_request_backup(p2p_network):
    p2p_network.add_node("TestUser", "192.168.1.1", "test_node_id")
    test_backup_data = "Test Backup Data"
    await p2p_network.send_backup("test_node_id", test_backup_data)
    backup = await p2p_network.request_backup("test_node_id")
    assert backup == test_backup_data

@pytest.mark.asyncio
async def test_request_nonexistent_backup(p2p_network):
    backup = await p2p_network.request_backup("nonexistent_node_id")
    assert backup is None

if __name__ == "__main__":
    pytest.main([__file__])