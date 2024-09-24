# In main.py

import asyncio
from src.social_network import SocialNetwork
from src.p2p_network import P2PNetwork


async def main():
    network = SocialNetwork()
    p2p_network = P2PNetwork(network)
    network.p2p_network = p2p_network

    # Add users
    users = ["Alice", "Bob", "Charlie", "David", "Eve"]
    for user in users:
        network.add_user(user)
        p2p_network.add_node(user, f"192.168.1.{users.index(user) + 1}", f"{user.lower()}_id")

    # Create connections and add trusted nodes
    for i in range(len(users)):
        for j in range(i + 1, len(users)):
            network.connect_users(users[i], users[j])

            # Add as trusted contact
            network.add_trusted_connection(users[i], users[j], "contact")

            # Add user's device as trusted node
            device_id = f"{users[i].lower()}_device"
            device_ip = f"192.168.2.{i + 1}"
            network.users[users[i]].add_trusted_node(device_id, "device", device_ip)
            p2p_network.add_node(f"{users[i]}_device", device_ip, device_id)

    # Demonstrate IP address change
    print("Changing IP address for Alice's device...")
    alice_device_id = "alice_device"
    new_ip = "192.168.3.1"
    p2p_network.update_node_ip(alice_device_id, new_ip)
    print(f"Alice's device new IP: {new_ip}")

    # Post data for Alice
    data = "Hello, this is my first post!"
    network.post_data("Alice", data)

    # Propagate data
    await network.propagate_data("Alice", data)

    # Create and distribute backup
    print("Creating and distributing backup for Alice...")
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

    # Generate and verify ZK proof (placeholder implementation)
    claim = "I have made at least one post"
    proof = network.generate_zk_proof("Alice", claim)
    is_valid = network.verify_zk_proof(proof, claim)
    print(f"Is Alice's claim valid? {is_valid}")
    print("Note: This is a placeholder implementation and always returns True.")

    # Print trusted nodes for Alice
    print("\nAlice's trusted nodes:")
    for node in network.users["Alice"].trusted_nodes:
        print(f"Node ID: {node.node_id}, Type: {node.node_type}, IP: {node.ip_address}")


if __name__ == "__main__":
    asyncio.run(main())