import pytest
from src.blockchain import PersonalBlockchain
from src.backup_manager import BackupManager
from src.p2p_network import P2PNetwork


@pytest.fixture
def personal_blockchain():
    return PersonalBlockchain("TestUser")


@pytest.fixture
def backup_manager(personal_blockchain):
    return BackupManager(personal_blockchain)


@pytest.fixture
def p2p_network():
    return P2PNetwork(None)  # We don't need a real social network for these tests


def test_create_backup(backup_manager):
    backup_data = backup_manager.create_backup()
    assert isinstance(backup_data, bytes)
    assert len(backup_data) > 0


def test_restore_from_backup(backup_manager, capsys):
    backup_data = backup_manager.create_backup()
    backup_manager.restore_from_backup(backup_data)
    captured = capsys.readouterr()
    assert "Restored data for user TestUser" in captured.out
    assert "Chain length: 1" in captured.out  # Assuming only genesis block


def test_split_and_reconstruct_secret(backup_manager):
    secret = b"This is a test secret" * 10  # Make sure it's long enough
    n, k = 5, 3
    shares = backup_manager.split_secret(secret, n, k)
    reconstructed = backup_manager.reconstruct_secret(shares[:k], k)
    assert reconstructed == secret


@pytest.mark.asyncio
async def test_distribute_and_restore_backup(backup_manager, p2p_network):
    trusted_nodes = ["node1", "node2", "node3", "node4", "node5"]
    await backup_manager.distribute_backup(p2p_network, trusted_nodes)
    success = await backup_manager.request_backup_restoration(p2p_network, trusted_nodes)
    assert success


@pytest.mark.asyncio
async def test_partial_backup_restoration(backup_manager, p2p_network):
    trusted_nodes = ["node1", "node2", "node3", "node4", "node5"]
    await backup_manager.distribute_backup(p2p_network, trusted_nodes)

    # Try with just enough nodes to reconstruct
    available_nodes = trusted_nodes[:3]
    success = await backup_manager.request_backup_restoration(p2p_network, available_nodes)
    assert success

    # Try with fewer nodes than required
    not_enough_nodes = trusted_nodes[:2]
    success = await backup_manager.request_backup_restoration(p2p_network, not_enough_nodes)
    assert not success