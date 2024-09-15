import pytest
from src.social_network import SocialNetwork


def test_add_user():
    network = SocialNetwork()
    network.add_user("Alice")
    assert "Alice" in network.users
    assert "Alice" in network.connections


def test_connect_users():
    network = SocialNetwork()
    network.add_user("Alice")
    network.add_user("Bob")
    network.connect_users("Alice", "Bob")
    assert "Bob" in network.connections["Alice"]
    assert "Alice" in network.connections["Bob"]


def test_post_data():
    network = SocialNetwork()
    network.add_user("Alice")
    network.post_data("Alice", "Test post")
    assert len(network.users["Alice"].chain) == 2  # Genesis block + new post
    assert network.users["Alice"].chain[-1].data["data"] == "Test post"


@pytest.mark.asyncio
async def test_propagate_data():
    network = SocialNetwork()
    network.add_user("Alice")
    network.add_user("Bob")
    network.connect_users("Alice", "Bob")
    await network.propagate_data("Alice", "Test data")
    assert len(network.pending_transactions) == 1
    assert network.pending_transactions[0]["sender"] == "Alice"
    assert network.pending_transactions[0]["receiver"] == "Bob"
    assert network.pending_transactions[0]["data"] == "Test data"


def test_consensus():
    network = SocialNetwork()
    network.add_user("Alice")
    network.add_user("Bob")
    network.pending_transactions.append({"sender": "Alice", "receiver": "Bob", "data": "Test data"})
    network.consensus()
    assert len(network.pending_transactions) == 0
    assert network.users["Bob"].chain[-1].data["data"] == "Test data"


def test_add_trusted_connection():
    network = SocialNetwork()
    network.add_user("Alice")
    network.add_user("Bob")
    network.add_trusted_connection("Alice", "Bob")
    assert "Bob" in network.users["Alice"].trusted_nodes
    assert "Alice" in network.users["Bob"].trusted_nodes
