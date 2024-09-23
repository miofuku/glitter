import asyncio
from src.social_network import SocialNetwork
from src.p2p_network import P2PNetwork


async def main():
    network = SocialNetwork()
    p2p_network = P2PNetwork(network)
    network.p2p_network = p2p_network  # Set the p2p_network attribute

    # Add more users to ensure enough trusted nodes
    users = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]
    for user in users:
        network.add_user(user)

    # Create more connections and trusted connections
    for i in range(len(users)):
        for j in range(i + 1, len(users)):
            network.connect_users(users[i], users[j])
            network.add_trusted_connection(users[i], users[j])

    # Add nodes to the P2P network
    for i, user in enumerate(users):
        p2p_network.add_node(user, f"192.168.1.{i + 1}")

    # Post data for Alice
    data = "Hello, this is my first post!"
    network.post_data("Alice", data)

    # Propagate data
    await network.propagate_data("Alice", data)

    # Create and distribute backup
    await network.create_and_distribute_backup("Alice")

    print("Simulating data loss for Alice...")
    network.users["Alice"].chain = []  # Clear Alice's blockchain

    print("Restoring Alice's data from backup...")
    success = await network.restore_from_backup("Alice")
    if success:
        print("Alice's data restored successfully!")
        print(f"Alice's chain length: {len(network.users['Alice'].chain)}")
        print(f"Last block data: {network.users['Alice'].chain[-1].data}")
    else:
        print("Failed to restore Alice's data.")

    # Run consensus
    network.consensus()

    # Generate and verify ZK proof
    claim = "I have made at least one post"
    proof = network.generate_zk_proof("Alice", claim)
    is_valid = network.verify_zk_proof(proof, claim)
    print(f"Is Alice's claim valid? {is_valid}")
    print("Note: This is a placeholder implementation and always returns True.")


if __name__ == "__main__":
    asyncio.run(main())
