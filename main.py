import asyncio
import logging
from src.social_network import SocialNetwork

logging.basicConfig(level=logging.INFO)


async def main():
    network = SocialNetwork()

    try:
        # Add users
        users = ["Alice", "Bob", "Charlie", "David", "Eve"]
        for user in users:
            network.add_user(user)

        # Start all P2P network nodes
        await network.start()

        # Create connections
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                network.connect_users(users[i], users[j])

        # Post data for Alice
        data = "Hello, this is my first post!"
        network.post_data("Alice", data)

        # Propagate data
        await network.propagate_data("Alice", data)

        # Wait a bit to allow for data propagation
        await asyncio.sleep(2)

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

    finally:
        # Clean up
        await network.stop()

if __name__ == "__main__":
    asyncio.run(main())