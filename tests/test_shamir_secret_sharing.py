import pytest
import random
from src.shamir_secret_sharing import ShamirSecretSharing, PRIME


@pytest.fixture
def sss():
    return ShamirSecretSharing(PRIME)


def test_split_and_reconstruct(sss):
    secret = "This is a secret message!"
    n, k = 5, 3

    # Split the secret
    shares_list = sss.split_secret(secret, n, k)

    # Verify number of shares
    assert all(len(shares) == n for shares in shares_list)

    # Reconstruct with exactly k shares
    reconstructed = sss.reconstruct_secret([shares[:k] for shares in shares_list], k)
    assert reconstructed == secret

    # Reconstruct with more than k shares
    reconstructed = sss.reconstruct_secret(shares_list, k)
    assert reconstructed == secret


def test_different_share_combinations(sss):
    secret = "Another secret message"
    n, k = 6, 4

    shares_list = sss.split_secret(secret, n, k)

    # Try different combinations of k shares
    for _ in range(10):  # Try 10 random combinations
        random_shares_list = [random.sample(shares, k) for shares in shares_list]
        reconstructed = sss.reconstruct_secret(random_shares_list, k)
        assert reconstructed == secret


def test_not_enough_shares(sss):
    secret = "Not enough shares"
    n, k = 5, 3

    shares_list = sss.split_secret(secret, n, k)

    with pytest.raises(ValueError):
        sss.reconstruct_secret([shares[:k - 1] for shares in shares_list], k)


def test_invalid_k_value(sss):
    secret = "Invalid k value"
    n, k = 3, 5

    with pytest.raises(ValueError):
        sss.split_secret(secret, n, k)


def test_very_long_secret(sss):
    secret = "This is an extremely long secret message that we want to make sure can be properly encoded and decoded using our Shamir's Secret Sharing implementation. " * 1000
    n, k = 10, 6

    shares_list = sss.split_secret(secret, n, k)
    reconstructed = sss.reconstruct_secret([shares[:k] for shares in shares_list], k)
    assert reconstructed == secret


def test_multiple_reconstructions(sss):
    secret = "This is a moderately long secret message that we'll reconstruct multiple times."
    n, k = 8, 5

    shares_list = sss.split_secret(secret, n, k)

    for _ in range(100):  # Perform 100 reconstructions
        random_shares_list = [random.sample(shares, k) for shares in shares_list]
        reconstructed = sss.reconstruct_secret(random_shares_list, k)
        assert reconstructed == secret


if __name__ == "__main__":
    pytest.main([__file__])