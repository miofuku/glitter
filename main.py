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
            try:
                network.add_user(user)
                logging.info(f"Added user: {user}")
            except Exception as e:
                logging.error(f"Error adding user {user}: {str(e)}")

        # Start all P2P network nodes
        try:
            await network.start()
            logging.info("All P2P network nodes started")
        except Exception as e:
            logging.error(f"Error starting P2P network nodes: {str(e)}")

        # Create connections and set up trusted nodes
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                try:
                    network.connect_users(users[i], users[j])
                    logging.info(f"Connected users: {users[i]} and {users[j]}")
                except Exception as e:
                    logging.error(f"Error connecting users {users[i]} and {users[j]}: {str(e)}")

        # Post data for Alice
        try:
            data = "Hello, this is my first post!"
            network.post_data("Alice", data)
            logging.info(f"Posted data for Alice: {data}")
        except Exception as e:
            logging.error(f"Error posting data for Alice: {str(e)}")

        # Propagate data
        try:
            await network.propagate_data("Alice", data)
            logging.info("Propagated Alice's data")
        except Exception as e:
            logging.error(f"Error propagating Alice's data: {str(e)}")

        # Wait a bit to allow for data propagation
        await asyncio.sleep(2)

        # Create and distribute backup
        try:
            logging.info("Creating and distributing backup for Alice...")
            await network.create_and_distribute_backup("Alice")
        except Exception as e:
            logging.error(f"Error creating and distributing backup for Alice: {str(e)}")

        # Simulate data loss
        try:
            logging.info("Simulating data loss for Alice...")
            network.users["Alice"].chain = []  # Clear Alice's blockchain
        except Exception as e:
            logging.error(f"Error simulating data loss for Alice: {str(e)}")

        # Restore data from backup
        try:
            logging.info("Restoring Alice's data from backup...")
            success = await network.restore_from_backup("Alice")
            if success:
                logging.info("Alice's data restored successfully!")
                logging.info(f"Alice's chain length: {len(network.users['Alice'].chain)}")
                logging.info(f"Last block data: {network.users['Alice'].chain[-1].data}")
            else:
                logging.error("Failed to restore Alice's data.")
        except Exception as e:
            logging.error(f"Error restoring Alice's data: {str(e)}")

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {str(e)}")

    finally:
        # Clean up
        try:
            await network.stop()
            logging.info("Network stopped")
        except Exception as e:
            logging.error(f"Error stopping the network: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())