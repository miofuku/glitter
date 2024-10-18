import asyncio
import logging
from src.social_network import SocialNetwork

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


async def main():
    network = SocialNetwork()

    try:
        # Add users
        users = ["Alice", "Bob", "Charlie", "David", "Eve"]
        for user in users:
            network.add_user(user)
            logging.info(f"Added user: {user}")

        # Start all P2P network nodes
        await network.start()
        logging.info("All P2P network nodes started")

        # Create connections and set up trusted nodes
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                network.connect_users(users[i], users[j])
                logging.info(f"Connected users: {users[i]} and {users[j]}")

        # Log trusted nodes for Alice
        alice_trusted_nodes = network.get_trusted_nodes_count("Alice")
        logging.info(f"Alice has {alice_trusted_nodes} trusted nodes")
        for node in network.users["Alice"].trusted_nodes:
            logging.info(f"Alice's trusted node: {node.node_id}, {node.node_type}, {node.ip_address}")

        # Post data for Alice
        data = "Hello, this is Alice's first post!"
        network.post_data("Alice", data)
        logging.info(f"Posted data for Alice: {data}")

        # Create and distribute backup for Alice
        logging.info("Creating and distributing backup for Alice...")
        backup_success = await network.create_and_distribute_backup("Alice")
        if backup_success:
            logging.info("Backup created and distributed successfully")
        else:
            logging.error("Failed to create and distribute backup")

        # Simulate data loss for Alice
        logging.info("Simulating data loss for Alice...")
        original_chain_length = len(network.users["Alice"].chain)
        network.users["Alice"].chain = []  # Clear Alice's blockchain
        logging.info(f"Alice's chain cleared. Original length: {original_chain_length}, Current length: {len(network.users['Alice'].chain)}")

        # Restore Alice's data
        logging.info("Restoring Alice's data from backup...")
        restore_success = await network.restore_from_backup("Alice")
        if restore_success:
            logging.info("Alice's data restored successfully!")
            restored_chain_length = len(network.users["Alice"].chain)
            logging.info(f"Alice's chain length: {restored_chain_length}")
            if restored_chain_length > 0:
                logging.info(f"Last block data: {network.users['Alice'].chain[-1].data}")
            if restored_chain_length == original_chain_length:
                logging.info("Restoration successful: chain length matches the original")
            else:
                logging.warning(f"Restoration partially successful: original length {original_chain_length}, restored length {restored_chain_length}")
        else:
            logging.error("Failed to restore Alice's data.")

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {str(e)}")

    finally:
        # Clean up
        await network.stop()
        logging.info("Network stopped")

if __name__ == "__main__":
    asyncio.run(main())