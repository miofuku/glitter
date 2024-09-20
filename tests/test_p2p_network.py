import pytest
from src.p2p_network import P2PNetwork


@pytest.fixture
def p2p_network():
    return P2PNetwork(None)  # We don't need a real social network for these tests


def test_add_node(p2p_network):
    p2p_network.add_node("TestUser", "192.168.1.1")
    assert "TestUser" in p2p_network.nodes
    assert p2p_network.nodes["TestUser"] == "192.168.1.1"


@pytest.mark.asyncio
async def test_broadcast(p2p_network, capsys):
    p2p_network.add_node("User1", "192.168.1.1")
    p2p_network.add_node("User2", "192.168.1.2")
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
    await p2p_network.send_backup("TestNode", (1, 12345))  # Send a sample share
    backup = await p2p_network.request_backup("TestNode")
    assert backup == (1, 12345)