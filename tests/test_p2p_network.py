import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.p2p_network import P2PNetwork
import aiohttp

@pytest.fixture
def p2p_network():
    return P2PNetwork()

def test_add_node(p2p_network):
    p2p_network.add_node("TestUser", 8000, "test_user_id")
    assert "TestUser" in p2p_network.nodes
    assert p2p_network.nodes["TestUser"] == (8000, "test_user_id")

@pytest.mark.asyncio
async def test_broadcast(p2p_network, mocker):
    # Mock the send_data method
    mock_send_data = AsyncMock()
    mocker.patch.object(p2p_network, 'send_data', mock_send_data)

    p2p_network.add_node("User1", 8001, "user1_id")
    p2p_network.add_node("User2", 8002, "user2_id")

    await p2p_network.broadcast("Sender", "Test Message")

    assert mock_send_data.call_count == 2
    mock_send_data.assert_any_call("User1", "Sender", "Test Message")
    mock_send_data.assert_any_call("User2", "Sender", "Test Message")

@pytest.mark.asyncio
async def test_send_data(p2p_network):
    # Mock the entire aiohttp module
    with patch('src.p2p_network.aiohttp.ClientSession') as mock_session:
        # Set up the mock response
        mock_response = AsyncMock()
        mock_response.status = 200

        # Set up the mock session
        mock_session_instance = AsyncMock()
        mock_session_instance.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value.__aenter__.return_value = mock_session_instance

        # Add a test node
        p2p_network.add_node("TestUser", 8000, "test_user_id")

        # Call the method we're testing
        await p2p_network.send_data("TestUser", "Sender", "Test Message")

        # Assertions
        mock_session.assert_called_once()
        mock_session_instance.post.assert_called_once_with(
            'http://localhost:8000',
            json={'sender': 'Sender', 'message': 'Test Message'}
        )

@pytest.mark.asyncio
async def test_send_and_request_backup(p2p_network):
    p2p_network.add_node("TestUser", 8000, "test_node_id")
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