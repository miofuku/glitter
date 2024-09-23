# glitter - Interpersonal Network

## Overview

This project is a revolutionary approach to social networking, leveraging personal blockchain technology to give users full control over their data while enabling privacy-preserving social interactions. 
It aims to address the significant shortcomings of current Web2 social networks and professional platforms by prioritizing user privacy, data ownership, and authentic connections.

## Key features:

* **Personal Blockchains**: Each user has their own blockchain, ensuring data ownership and control.
* **Decentralized Architecture**: No central authority controls user data.
* **Privacy-Preserving**: Uses zero-knowledge proofs for claim verification without revealing underlying data.
* **Distributed Backup System**: Implements Shamir's Secret Sharing for distributed, secure backups.
* **P2P Communication**: Simulates a peer-to-peer network for data propagation and backup distribution.
* **Consensus Mechanism**: Implements a simple majority consensus (can be extended for more robust mechanisms).

## Requirements

* Python 3.7+
* Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```
git clone https://github.com/miofuku/glitter.git
cd glitter
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
* `src/`:
  * `blockchain.py`: Implements the PersonalBlockchain class
  * `social_network.py`: Manages the SocialNetwork class
  * `p2p_network.py`: Simulates the P2PNetwork
  * `backup_manager.py`: Handles backup and restoration of personal blockchains
  * `shamir_secret_sharing.py`: Implements Shamir's Secret Sharing algorithm
  * `zk_snark.py`: Placeholder for zero-knowledge proof implementation.
  * `block.py`: Defines the Block class for blockchain entries
* `tests/`: Contains unit and integration tests for all major components.

## Current Limitations
This prototype is a conceptual implementation and has several limitations:
1. The zero-knowledge proof system is a placeholder and needs a real implementation.
2. The P2P network is simulated and would need to be replaced with a real implementation for production use.
3. The consensus mechanism is a simple placeholder and should be replaced with a more robust algorithm.

## Future Development
To turn this prototype into a fully functional system, consider the following enhancements:
1. Implement a real zero-knowledge proof system to replace the current placeholder.
2. Enhance the P2P network simulation with actual network capabilities.
3. Develop a more sophisticated consensus mechanism.
4. Implement a user interface for easier interaction with the network.
5. Conduct a comprehensive security audit before any production use.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This prototype is for educational purposes only and is not suitable for handling real personal data or for use in a production environment. Use at your own risk.