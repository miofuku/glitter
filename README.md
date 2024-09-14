# glitter - Personal Blockchain Social Network

## Overview

This project is a prototype for a decentralized social network built on personal blockchains with zero-knowledge proof capabilities. It aims to provide a privacy-preserving platform for social interactions, offering users full control over their data while enabling verifiable social connections.
## Key features:

* Personal blockchain for each user
* Peer-to-peer network simulation
* Digital signatures for data authenticity
* Zero-knowledge proofs for privacy-preserving validation (placeholder implementation)
* Simple consensus mechanism
* Data propagation across the network
* Backup and restoration system using a web of trust

## Requirements

* Python 3.7+
* Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/personal-blockchain-social-network.git
cd personal-blockchain-social-network
```

2. Create and activate a virtual environment:
```
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage
To run the prototype:
```
python3 main.py
```

## Running Tests
To run the tests:
```
pytest tests/
```

## Components
* `blockchain.py`: Implements the core blockchain functionality and personal blockchain management.
* `social_network.py`: Manages the social network aspects, including user interactions and data propagation.
* `p2p_network.py`: Simulates the peer-to-peer network for data exchange and backup distribution.
* `backup_manager.py`: Handles the creation, distribution, and restoration of backups using the web of trust.
* `zk_snark.py`: A placeholder for zero-knowledge proof functionality (not fully implemented).

## Current Limitations
This prototype is a conceptual implementation and has several limitations:
1. The ZK-SNARK implementation is a placeholder and not functional.
2. The P2P network is simulated and doesn't involve actual network communications.
3. The consensus mechanism is simplified and not suitable for a real-world scenario.
4. There's no persistent storage; all data is held in memory.
5. Security measures are minimal and not sufficient for a production environment.
6. There's no user interface; all interactions are programmatic.

## Future Development
To turn this prototype into a fully functional system, consider the following enhancements:
1. Implement a real ZK-SNARK library for actual zero-knowledge proofs.
2. Develop a proper P2P networking layer using a library like libp2p.
3. Design and implement a more robust consensus algorithm suitable for personal blockchains.
4. Add persistent storage for blockchain data.
5. Implement comprehensive security measures, including encryption for data at rest and in transit.
6. Develop a user-friendly interface (web or mobile app).
7. Enhance the backup and restoration system with more sophisticated encryption and recovery mechanisms.
8. Implement partial backups and versioning for more flexible data management.
9. Conduct thorough testing, including security audits and penetration testing.
10. Optimize for scalability to handle a large number of users and high transaction volumes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This prototype is for educational purposes only and is not suitable for handling real personal data or for use in a production environment. Use at your own risk.