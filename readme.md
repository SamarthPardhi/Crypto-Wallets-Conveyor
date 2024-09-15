# Crypto Wallets Conveyor

## Overview

This project is a specialized system designed to recover and transfer cryptocurrency assets from potentially compromised wallets to secure addresses. It was developed for a client needing to move funds from user wallets that may have been compromised to new, secure wallet addresses.

The system consists of a Flask-based web application that provides a dashboard interface to control and monitor asset recovery operations. It interacts with multiple blockchain networks, including Bitcoin and EVM-compatible chains like Ethereum, Polygon, and Binance Smart Chain.

## Key files

- `main.py`: Contains logic and controls the flow.
- `app.py`: The Flask-based web app to provide the user interface and scanning through blockchains and performing gas and fund trade-offs.
- `config.py`: Contains blockchain network RPC endpoints, API keys for blockchain data providers, and user authentication information.

## Security Considerations and Risks

This repository is for educational purposes. It deals with highly sensitive data (private keys) and performs irreversible financial transactions. As such, it comes with significant risks:

1. **Private Key Exposure**: Improper handling of private keys could lead to unauthorized access and asset theft.

2. **Network Security**: Reliance on third-party RPC endpoints introduces potential for man-in-the-middle attacks.

3. **Access Control**: Unauthorized access to the dashboard could allow malicious actors to initiate transfers.

4. **Data Integrity**: Errors in parsing input data could lead to incorrect transfer operations.

5. **Regulatory Compliance**: Automated movement of assets may have legal implications depending on jurisdiction.

## Usage Warning

This system is designed for a specific use case and should only be used by qualified individuals who understand the associated risks. Improper use could result in permanent loss of cryptocurrency assets. Always verify recipient addresses and transfer amounts before initiating any operations.
