import pytest
from src.backup_manager import BackupManager
from src.blockchain import PersonalBlockchain, TrustedNode
import base64
import json


@pytest.fixture
def personal_blockchain():
    return PersonalBlockchain("TestUser")


@pytest.fixture
def backup_manager(personal_blockchain):
    return BackupManager(personal_blockchain)


@pytest.mark.asyncio
async def test_distribute_and_restore_backup(backup_manager):
    class MockP2PNetwork:
        def __init__(self):
            self.backups = {}

        async def send_backup(self, node_id, data):
            self.backups[node_id] = data

        async def request_backup(self, node_id):
            return self.backups.get(node_id)

    p2p_network = MockP2PNetwork()
    n, k = 5, 3
    trusted_nodes = [TrustedNode(f"node{i}", "contact", f"192.168.1.{i}") for i in range(n)]

    # Distribute backup
    serialized_shares = backup_manager.create_backup(n, k)
    for i, node in enumerate(trusted_nodes):
        await p2p_network.send_backup(node.node_id, serialized_shares)

    # Verify that backups were sent to all nodes
    assert len(p2p_network.backups) == n

    # Clear the blockchain
    original_chain = backup_manager.personal_blockchain.chain
    backup_manager.personal_blockchain.chain = []

    # Restore from backup
    retrieved_shares = await p2p_network.request_backup(trusted_nodes[0].node_id)
    success = backup_manager.restore_from_backup(retrieved_shares, k)
    assert success, "Failed to restore backup"

    restored_chain = backup_manager.personal_blockchain.chain
    assert len(restored_chain) == len(original_chain)
    for original, restored in zip(original_chain, restored_chain):
        assert original.index == restored.index
        assert original.data == restored.data

    # Try to restore with insufficient nodes
    backup_manager.personal_blockchain.chain = []
    insufficient_shares = backup_manager.sss.deserialize_shares(retrieved_shares)
    insufficient_shares = [shares[:k - 1] for shares in insufficient_shares]
    insufficient_serialized = backup_manager.sss.serialize_shares(insufficient_shares)
    success = backup_manager.restore_from_backup(insufficient_serialized, k)
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

        async def send_backup(self, node_id, data):
            self.backups[node_id] = data

        async def request_backup(self, node_id):
            return self.backups.get(node_id)

    p2p_network = MockP2PNetwork()
    n, k = 5, 3
    trusted_nodes = [TrustedNode(f"node{i}", "contact", f"192.168.1.{i}") for i in range(n)]

    # Distribute backup
    serialized_shares = backup_manager.create_backup(n, k)
    for node in trusted_nodes:
        await p2p_network.send_backup(node.node_id, serialized_shares)

    # Verify that backups were sent to all nodes
    assert len(p2p_network.backups) == n

    # Clear the blockchain
    original_chain = backup_manager.personal_blockchain.chain
    backup_manager.personal_blockchain.chain = []

    # Restore from backup
    retrieved_shares = await p2p_network.request_backup(trusted_nodes[0].node_id)
    success = backup_manager.restore_from_backup(retrieved_shares, k)
    assert success, "Failed to restore backup"

    restored_chain = backup_manager.personal_blockchain.chain
    assert len(restored_chain) == len(original_chain)
    for original, restored in zip(original_chain, restored_chain):
        assert original.index == restored.index
        assert original.data == restored.data

    # Verify that the complex data was correctly restored
    assert restored_chain[-1].data == complex_data

if __name__ == "__main__":
    pytest.main([__file__])
