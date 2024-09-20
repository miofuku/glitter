import pytest
from src.backup_manager import BackupManager
from unittest.mock import Mock
import os


@pytest.fixture
def backup_manager():
    mock_blockchain = Mock()
    mock_blockchain.owner = "TestUser"
    mock_blockchain.chain = [
        Mock(index=i, timestamp=1000 + i, data={"message": f"Block {i}"}, previous_hash=f"hash{i - 1}", hash=f"hash{i}")
        for i in range(3)]
    return BackupManager(mock_blockchain)


def test_split_secret(backup_manager):
    secret = b"This is a test secret" * 10
    n, k = 5, 3
    shares = backup_manager.split_secret(secret, n, k)

    assert len(shares) == n
    assert all(isinstance(share, tuple) and len(share) == 2 for share in shares)
    assert all(isinstance(share[0], int) and isinstance(share[1], bytes) for share in shares)


def test_reconstruct_secret(backup_manager):
    secret = b"This is a test secret" * 10
    n, k = 5, 3
    shares = backup_manager.split_secret(secret, n, k)

    # Test with exact k shares
    reconstructed = backup_manager.reconstruct_secret(shares[:k], k)
    assert reconstructed == secret

    # Test with more than k shares
    reconstructed = backup_manager.reconstruct_secret(shares[:k + 1], k)
    assert reconstructed == secret


def test_reconstruct_secret_with_insufficient_shares(backup_manager):
    secret = b"This is a test secret" * 10
    n, k = 5, 3
    shares = backup_manager.split_secret(secret, n, k)

    # Test with less than k shares
    reconstructed = backup_manager.reconstruct_secret(shares[:k - 1], k)
    assert reconstructed is None


def test_create_backup(backup_manager):
    backup_data = backup_manager.create_backup()
    assert isinstance(backup_data, bytes)
    assert len(backup_data) > 0


def test_restore_from_backup(backup_manager):
    original_chain = backup_manager.personal_blockchain.chain
    backup_data = backup_manager.create_backup()

    # Clear the blockchain
    backup_manager.personal_blockchain.chain = []

    backup_manager.restore_from_backup(backup_data)
    restored_chain = backup_manager.personal_blockchain.chain

    assert len(restored_chain) == len(original_chain)
    for original, restored in zip(original_chain, restored_chain):
        assert original.index == restored.index
        assert original.data == restored.data


def test_split_and_reconstruct_with_random_data(backup_manager):
    for _ in range(100):  # Test with 100 random secrets
        secret = os.urandom(64)  # 64 bytes of random data
        n, k = 5, 3
        shares = backup_manager.split_secret(secret, n, k)
        reconstructed = backup_manager.reconstruct_secret(shares[:k], k)
        assert reconstructed == secret, f"Failed to reconstruct secret: {secret.hex()}"


def test_lagrange_interpolation(backup_manager):
    # Test the lagrange_interpolation function directly
    x_s = [1, 2, 3]
    y_s = [6, 11, 18]  # represents y = x^2 + 5

    def lagrange_interpolation(x, x_s, y_s):
        prime = 2 ** 256 - 189

        def pi(vals, var, j):
            acc = 1
            for i, val in enumerate(vals):
                if i != j:
                    try:
                        acc *= (var - val) * pow(vals[j] - val, -1, prime)
                    except ValueError:
                        return None
            return acc % prime

        result = 0
        for j, y in enumerate(y_s):
            pi_val = pi(x_s, x, j)
            if pi_val is None:
                return None
            result += y * pi_val
        return result % prime

    # Test interpolation at x = 4 (should be 4^2 + 5 = 21)
    result = lagrange_interpolation(4, x_s, y_s)
    assert result == 21, f"Expected 21, got {result}"

    # Test interpolation at x = 0 (should be 5)
    result = lagrange_interpolation(0, x_s, y_s)
    assert result == 5, f"Expected 5, got {result}"


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

    # Try to restore with all nodes
    success = await backup_manager.request_backup_restoration(p2p_network, trusted_nodes)
    assert success, "Failed to restore backup with all nodes"

    # Try to restore with minimum required nodes
    min_nodes = trusted_nodes[:3]
    success = await backup_manager.request_backup_restoration(p2p_network, min_nodes)
    assert success, "Failed to restore backup with minimum required nodes"

    # Try to restore with insufficient nodes
    insufficient_nodes = trusted_nodes[:2]
    success = await backup_manager.request_backup_restoration(p2p_network, insufficient_nodes)
    assert not success, "Unexpectedly succeeded in restoring backup with insufficient nodes"


if __name__ == "__main__":
    pytest.main([__file__])