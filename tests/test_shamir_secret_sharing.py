import pytest
import random
from src.shamir_secret_sharing import ShamirSecretSharing, PRIME
from src.blockchain import PersonalBlockchain


@pytest.fixture
def sss():
    return ShamirSecretSharing(PRIME)


@pytest.fixture
def personal_blockchain():
    return PersonalBlockchain("TestUser", b"Genesis Block Data")


def test_split_and_reconstruct(sss, personal_blockchain):
    n, k = 5, 3

    # Split the secret
    shares_list = sss.split_secret(personal_blockchain, n, k)

    # Verify number of shares
    assert all(len(shares) == n for shares in shares_list)

    # Reconstruct with exactly k shares
    reconstructed_data = sss.reconstruct_secret([shares[:k] for shares in shares_list], k)

    assert reconstructed_data['owner'] == personal_blockchain.owner
    assert len(reconstructed_data['chain']) == 1  # Only genesis block
    assert reconstructed_data['chain'][0]['data'] == personal_blockchain.chain[0].data


def test_different_share_combinations(sss, personal_blockchain):
    n, k = 6, 4

    shares_list = sss.split_secret(personal_blockchain, n, k)

    # Try different combinations of k shares
    for _ in range(10):  # Try 10 random combinations
        random_shares_list = [random.sample(shares, k) for shares in shares_list]
        reconstructed_data = sss.reconstruct_secret(random_shares_list, k)
        assert reconstructed_data['owner'] == personal_blockchain.owner
        assert len(reconstructed_data['chain']) == 1
        assert reconstructed_data['chain'][0]['data'] == personal_blockchain.chain[0].data


def test_not_enough_shares(sss, personal_blockchain):
    n, k = 5, 3

    shares_list = sss.split_secret(personal_blockchain, n, k)

    with pytest.raises(ValueError):
        sss.reconstruct_secret([shares[:k - 1] for shares in shares_list], k)


def test_invalid_k_value(sss, personal_blockchain):
    n, k = 3, 5
    with pytest.raises(ValueError, match="k must be less than or equal to n"):
        sss.split_secret(personal_blockchain, n, k)


def test_invalid_n_value(sss, personal_blockchain):
    n, k = 1, 2
    with pytest.raises(ValueError, match="n must be at least 2"):
        sss.split_secret(personal_blockchain, n, k)


def test_invalid_k_value_low(sss, personal_blockchain):
    n, k = 3, 1
    with pytest.raises(ValueError, match="k must be at least 2"):
        sss.split_secret(personal_blockchain, n, k)


def test_multiple_reconstructions(sss, personal_blockchain):
    n, k = 8, 5

    shares_list = sss.split_secret(personal_blockchain, n, k)

    for _ in range(100):  # Perform 100 reconstructions
        random_shares_list = [random.sample(shares, k) for shares in shares_list]
        reconstructed_data = sss.reconstruct_secret(random_shares_list, k)
        assert reconstructed_data['owner'] == personal_blockchain.owner
        assert len(reconstructed_data['chain']) == 1
        assert reconstructed_data['chain'][0]['data'] == personal_blockchain.chain[0].data


def test_different_k_n_values(sss, personal_blockchain):
    test_cases = [(5, 3), (7, 4), (10, 6)]

    for n, k in test_cases:
        shares_list = sss.split_secret(personal_blockchain, n, k)

        assert all(len(shares) == n for shares in shares_list)

        reconstructed_data = sss.reconstruct_secret([shares[:k] for shares in shares_list], k)

        assert reconstructed_data['owner'] == personal_blockchain.owner
        assert len(reconstructed_data['chain']) == 1
        assert reconstructed_data['chain'][0]['data'] == personal_blockchain.chain[0].data

        # Try reconstruction with k-1 shares (should fail)
        with pytest.raises(ValueError):
            sss.reconstruct_secret([shares[:k - 1] for shares in shares_list], k)


if __name__ == "__main__":
    pytest.main([__file__])
