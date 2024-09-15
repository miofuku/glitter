import pytest

from src.backup_manager import BackupManager
from src.blockchain import PersonalBlockchain
from src.p2p_network import P2PNetwork


@pytest.fixture
def backup_manager():
    blockchain = PersonalBlockchain("TestUser")
    return BackupManager(blockchain)


def test_create_backup(backup_manager):
    backup_data = backup_manager.create_backup()
    assert isinstance(backup_data, bytes)


def test_restore_from_backup(backup_manager, capsys):
    backup_data = backup_manager.create_backup()
    backup_manager.restore_from_backup(backup_data)
    captured = capsys.readouterr()
    assert "Restored data for user TestUser" in captured.out
    assert "Chain length: 1" in captured.out


@pytest.mark.asyncio
async def test_distribute_backup(backup_manager):
    p2p_network = P2PNetwork(None)
    p2p_network.add_node("TrustedNode", "192.168.1.1")
    await backup_manager.distribute_backup(p2p_network, {"TrustedNode"})
    assert "TrustedNode" in p2p_network.backups


@pytest.mark.asyncio
async def test_request_backup_restoration(backup_manager):
    p2p_network = P2PNetwork(None)
    p2p_network.add_node("TrustedNode", "192.168.1.1")
    backup_data = backup_manager.create_backup()
    p2p_network.backups["TrustedNode"] = backup_data
    success = await backup_manager.request_backup_restoration(p2p_network, {"TrustedNode"})
    assert success == True
