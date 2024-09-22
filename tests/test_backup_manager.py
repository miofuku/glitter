import pytest
from src.backup_manager import BackupManager
from src.blockchain import PersonalBlockchain


@pytest.fixture
def personal_blockchain():
    return PersonalBlockchain("TestUser")


@pytest.fixture
def backup_manager(personal_blockchain):
    return BackupManager(personal_blockchain)


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
    n, k = 5, 3
    trusted_nodes = [f"node{i}" for i in range(n)]

    # Distribute backup
    await backup_manager.distribute_backup(p2p_network, trusted_nodes, n, k)

    # Verify that backups were sent to all nodes
    assert len(p2p_network.backups) == n

    # Clear the blockchain
    original_chain = backup_manager.personal_blockchain.chain
    backup_manager.personal_blockchain.chain = []

    # Restore from backup
    success = await backup_manager.request_backup_restoration(p2p_network, trusted_nodes, k)
    assert success, "Failed to restore backup"

    restored_chain = backup_manager.personal_blockchain.chain
    assert len(restored_chain) == len(original_chain)
    for original, restored in zip(original_chain, restored_chain):
        assert original.index == restored.index
        assert original.data == restored.data

    # Try to restore with insufficient nodes
    insufficient_nodes = trusted_nodes[:k-1]
    success = await backup_manager.request_backup_restoration(p2p_network, insufficient_nodes, k)
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
    n, k = 5, 3  # Define n and k values
    trusted_nodes = [f"node{i}" for i in range(n)]

    # Distribute backup
    await backup_manager.distribute_backup(p2p_network, trusted_nodes, n, k)

    # Verify that backups were sent to all nodes
    assert len(p2p_network.backups) == n

    # Clear the blockchain
    original_chain = backup_manager.personal_blockchain.chain
    backup_manager.personal_blockchain.chain = []

    # Restore from backup
    success = await backup_manager.request_backup_restoration(p2p_network, trusted_nodes, k)
    assert success, "Failed to restore backup"

    restored_chain = backup_manager.personal_blockchain.chain
    assert len(restored_chain) == len(original_chain)
    for original, restored in zip(original_chain, restored_chain):
        assert original.index == restored.index
        assert original.data == restored.data

    # Verify that the complex data was correctly restored
    assert restored_chain[-1].data["data"] == complex_data


if __name__ == "__main__":
    pytest.main([__file__])
