import asyncio
from src.social_network import SocialNetwork
from src.p2p_network import P2PNetwork

async def main():
    network = SocialNetwork()
    p2p_network = P2PNetwork(network)

    network.add_user("Alice")
    network.add_user("Bob")
    network.connect_users("Alice", "Bob")

    p2p_network.add_node("Alice", "192.168.1.1")
    p2p_network.add_node("Bob", "192.168.1.2")

    # Post data
    data = "Hello, this is my first post!"
    network.post_data("Alice", data)

    # Propagate data
    await network.propagate_data("Alice", data)

    # Run consensus
    network.consensus()

    # Generate and verify ZK proof
    claim = "I have made at least one post"
    proof = network.generate_zk_proof("Alice", claim)
    is_valid = network.verify_zk_proof(proof, claim)
    print(f"Is Alice's claim valid? {is_valid}")

    # Broadcast message over P2P network
    await p2p_network.broadcast("Alice", "New post available!")

if __name__ == "__main__":
    asyncio.run(main())