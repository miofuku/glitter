import asyncio
from src.social_network import SocialNetwork
from src.p2p_network import P2PNetwork

async def main():
    network = SocialNetwork()
    p2p_network = P2PNetwork(network)
    network.p2p_network = p2p_network  # Set the p2p_network attribute

    network.add_user("Alice")
    network.add_user("Bob")
    network.add_user("Charlie")

    network.connect_users("Alice", "Bob")
    network.connect_users("Alice", "Charlie")
    network.connect_users("Bob", "Charlie")

    network.add_trusted_connection("Alice", "Bob")
    network.add_trusted_connection("Alice", "Charlie")

    p2p_network.add_node("Alice", "192.168.1.1")
    p2p_network.add_node("Bob", "192.168.1.2")
    p2p_network.add_node("Charlie", "192.168.1.3")

    # Post data
    data = "Hello, this is my first post!"
    network.post_data("Alice", data)

    # Propagate data
    await network.propagate_data("Alice", data)

    # Create and distribute backup
    await network.create_and_distribute_backup("Alice")

    # Simulate data loss and restoration
    print("Simulating data loss for Alice...")
    network.users["Alice"].chain = []  # Clear Alice's blockchain

    print("Restoring Alice's data from backup...")
    success = await network.restore_from_backup("Alice")
    if success:
        print("Alice's data restored successfully!")
    else:
        print("Failed to restore Alice's data.")

    # Run consensus
    network.consensus()

    # Generate and verify ZK proof
    claim = "I have made at least one post"
    proof = network.generate_zk_proof("Alice", claim)
    is_valid = network.verify_zk_proof(proof, claim)
    print(f"Is Alice's claim valid? {is_valid}")


if __name__ == "__main__":
    asyncio.run(main())