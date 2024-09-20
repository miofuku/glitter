import pytest
from src.backup_manager import BackupManager
from src.blockchain import PersonalBlockchain
from unittest.mock import AsyncMock, Mock
import json

@pytest.fixture
def personal_blockchain():
    blockchain = PersonalBlockchain("TestUser")
    blockchain.add_block({"data": "Test Block 1"})
    blockchain.add_block({"data": "Test Block 2"})
    return blockchain

@pytest.fixture
def backup_manager(personal_blockchain):
    return BackupManager(personal_blockchain)

@pytest.mark.asyncio
async def test_distribute_and_restore_backup(backup_manager):
    class MockP2PNetwork:
        def __init__(self):
            self.backups = {}

        async def send_backup(self, node, data):
            self.backups[node] = data

        async def request_backup(self, node):
            return self.backups.get(node)

    p2p_network = MockP2PNetwork()
    trusted_nodes = ["node1", "node2", "node3", "node4", "node5"]

    # Distribute backup
    await backup_manager.distribute_backup(p2p_network, trusted_nodes)

    # Verify that backups were sent to all nodes
    assert len(p2p_network.backups) == len(trusted_nodes)

    # Clear the blockchain
    original_chain = backup_manager.personal_blockchain.chain
    backup_manager.personal_blockchain.chain = []

    # Restore from backup
    success = await backup_manager.request_backup_restoration(p2p_network, trusted_nodes)
    assert success, "Failed to restore backup"

    restored_chain = backup_manager.personal_blockchain.chain
    assert len(restored_chain) == len(original_chain)
    for original, restored in zip(original_chain, restored_chain):
        assert original.index == restored.index
        assert original.data == restored.data

    # Try to restore with insufficient nodes
    insufficient_nodes = trusted_nodes[:2]
    success = await backup_manager.request_backup_restoration(p2p_network, insufficient_nodes)
    assert not success, "Unexpectedly succeeded in restoring backup with insufficient nodes"

@pytest.mark.asyncio
async def test_backup_with_complex_data(backup_manager):
    complex_data = {
        "string": "test",
        "number": 42,
        "list": [1, 2, 3],
        "dict": {"key": "value"},
        "boolean": True,
        "null": None
    }
    backup_manager.personal_blockchain.add_block(complex_data)

    class MockP2PNetwork:
        def __init__(self):
            self.backups = {}

        async def send_backup(self, node, data):
            self.backups[node] = data

        async def request_backup(self, node):
            return self.backups.get(node)

    p2p_network = MockP2PNetwork()
    trusted_nodes = ["node1", "node2", "node3", "node4", "node5"]

    # Distribute backup
    await backup_manager.distribute_backup(p2p_network, trusted_nodes)

    # Clear the blockchain
    original_chain = backup_manager.personal_blockchain.chain
    backup_manager.personal_blockchain.chain = []

    # Restore from backup
    success = await backup_manager.request_backup_restoration(p2p_network, trusted_nodes)
    assert success, "Failed to restore backup"

    restored_chain = backup_manager.personal_blockchain.chain
    assert len(restored_chain) == len(original_chain)
    for original, restored in zip(original_chain, restored_chain):
        assert original.index == restored.index
        assert original.data == restored.data

if __name__ == "__main__":
    pytest.main([__file__])