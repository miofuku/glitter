import asyncio
import logging
from src.social_network import SocialNetwork

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    network = SocialNetwork()

    try:
        # Add users
        users = ["Alice", "Bob", "Charlie", "David", "Eve"]
        for user in users:
            network.add_user(user)

        # Start all P2P network nodes
        await network.start()
        logging.info("All P2P network nodes started")

        # Create connections and set up trusted nodes
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                network.connect_users(users[i], users[j])

        # Log trusted nodes for each user
        for user in users:
            trusted_nodes_count = network.get_trusted_nodes_count(user)
            logging.info(f"{user} has {trusted_nodes_count} trusted nodes")
            if user == "Alice":
                alice_blockchain = network.users["Alice"]
                for node in alice_blockchain.trusted_nodes:
                    logging.info(f"Alice's trusted node: {node.node_id}, {node.node_type}, {node.ip_address}")

        # Post data for Alice
        data = "Hello, this is my first post!"
        network.post_data("Alice", data)
        logging.info(f"Posted data for Alice: {data}")

        # Propagate data
        await network.propagate_data("Alice", data)

        # Wait a bit to allow for data propagation
        await asyncio.sleep(2)

        # Create and distribute backup
        alice_trusted_nodes = network.get_trusted_nodes_count("Alice")
        if alice_trusted_nodes >= network.total_shares:
            logging.info(f"Creating and distributing backup for Alice (trusted nodes: {alice_trusted_nodes}, required: {network.total_shares})...")
            await network.create_and_distribute_backup("Alice")
        else:
            logging.warning(f"Not enough trusted nodes for Alice to create a backup. Have {alice_trusted_nodes}, need {network.total_shares}")

        logging.info("Simulating data loss for Alice...")
        original_chain_length = len(network.users["Alice"].chain)
        network.users["Alice"].chain = []  # Clear Alice's blockchain
        logging.info(f"Alice's chain cleared. Original length: {original_chain_length}, Current length: {len(network.users['Alice'].chain)}")

        logging.info("Restoring Alice's data from backup...")
        success = await network.restore_from_backup("Alice")
        if success:
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