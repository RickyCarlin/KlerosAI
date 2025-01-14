<h1 align="center">KLEROS AI AGENT</h1>

<p align="center">
    An AI Agent for Analyzing Centeralized and Decenteralized Cryptocurrency Exchanges build with Python and OpenAI.
</p>

<p align="center">
    <a href='#overview'><strong>Overview</strong></a> ·
    <a href='#directory-structure'><strong>Directory Structure</strong></a> .
    <a href='#features'><strong>Features</strong></a> ·
    <a href='#exchange-support'><strong>Exchange Support</strong></a> ·
    <a href='#accessing-the-agent'><strong>Accessing the Agent</strong></a> ·
</p>

<hr>

## Overview
The Kleros AI Agent is a powerful tool designed to analyze both centralized and decentralized cryptocurrency exchanges. Built with Python and OpenAI technologies, this agent is capable of detecting arbitrage opportunities, monitoring real-time news updates, and identifying critical liquidity changes.

---

## Directory Structure

### Structure Summary
Below is the folder structure in a tree format to illustrate the project organization:

```
|- src/
|  |- services/
|  |  |- BinanceIntegrationService.py
|  |  |- ByBitIntegrationService.py
|  |  |- KrakenIntegrationService.py
|  |  |- KuCoinIntegrationService.py
|  |  |- OKXIntegrationService.py
|  |  |- TelegramConnectionService.py
|  |  |- TelethonService.py
|  |  |- AppDataService.py
|  |- logic/
|  |  |- NewScout.py
|  |  |- ArbiSense.py
|  |- models/
|  |  |- PriceDataModel.py
|  |- utils/
|     |- logger.py
|     |- fileutils.py
|- rulebooks/
|  |- [JSON files for exchange symbol rules]
|- main.py
|- README.md
```

### `src`
The main source directory containing the core services, models, and utility functions.

- **`services/`**: Contains integration services for different exchanges and communication tools.
  - `BinanceIntegrationService.py`: Handles API interactions with Binance to fetch symbol data and price changes.
  - `ByBitIntegrationService.py`: Fetches trading data from ByBit’s API.
  - `KrakenIntegrationService.py`: Retrieves asset pairs and ticker data from Kraken.
  - `KuCoinIntegrationService.py`: Interfaces with KuCoin’s market data API.
  - `OKXIntegrationService.py`: Handles OKX’s market data retrieval.
  - `TelegramConnectionService.py`: Manages connections to the Telegram Bot API and sends notifications.
  - `TelethonService.py`: Utilizes Telethon to connect to Telegram channels for scraping crypto news.
  - `AppDataService.py`: Manages file paths, API key storage, and subscription-related files.

- **`logic/`**: Contains the core logic for orchestrating services.
  - `NewScout.py`: A service that listens for crypto-related news updates from specified Telegram channels.
  - `ArbiSense.py`: Detects arbitrage opportunities by comparing price data across different exchanges.

- **`models/`**: Houses data models used in the project.
  - `PriceDataModel.py`: Represents the structure of price data, including attributes for symbol, price, exchange, and volume.

- **`utils/`**: Provides utility classes.
  - `logger.py`: Implements a singleton logger for consistent logging across services.
  - `fileutils.py`: Contains helper functions for file operations.

### `rulebooks/`
A folder where JSON files containing exchange-specific symbol rules and settings are stored.

### `main.py`
The entry point of the application that initializes and starts services like `ArbiSense` and `NewScout`. This file sets up the Flask server for real-time streaming of arbitrage data and handles user interactions via the Telegram Bot.

### `README.md`
The primary documentation file that provides a summary of the project, including features, supported exchanges, and how users can access the AI Agent.

---

## Features

### **1. ArbiSense**
A robust arbitrage detection service that scans centralized exchanges for profitable opportunities. It fetches live market data from the following exchanges:
- Binance
- ByBit
- KuCoin
- Kraken
- OKX

ArbiSense is designed to detect discrepancies in cryptocurrency prices across different exchanges in real-time. It continuously retrieves data and performs in-depth comparisons to detect profitable opportunities. The key components of ArbiSense include:

- **Threading:** Runs data retrieval threads for simultaneous updates from each exchange to ensure minimal delay.
- **Common Pair Detection:** Identifies common trading pairs between exchanges and performs pair-wise comparison.
- **Arbitrage Percentage Calculation:** Calculates percentage differences between exchanges and triggers alerts when differences exceed a specified threshold.
- **Alerts:** Sends comprehensive summaries of detected arbitrage paths via Telegram, including detailed price differences and percentage gains.

### **2. NewsPulse**
A feature that tracks crypto news from Telegram channels to detect major announcements that may impact market movements.

**Highlights:**
- Subscribes to predefined Telegram channels.
- Uses `TelethonService` to receive and parse messages containing relevant keywords.

NewsPulse is responsible for monitoring key channels for updates that might influence the crypto market.

- **Predefined Channels:** Monitors a list of predefined Telegram channels known for impactful news.
- **Message Parsing:** Uses regex-based parsing to detect relevant keywords such as 'listing', 'pump', or new project announcements.
- **Real-Time Alerts:** Summarizes detected news into actionable messages and sends them to users.

### **3. SolScouter**
Detects new liquidity pools for token pairs on the Solana blockchain using Raydium AMM V4.

**Detailed Description:**
SolScouter is designed to detect and report the creation of new liquidity pools in decentralized finance (DeFi):

- **Pool Detection:** Tracks blockchain events related to Raydium AMM liquidity pool creation.
- **Token Information:** Retrieves metadata for the token pairs and reports their attributes.
- **Timely Notifications:** Ensures that users are informed immediately when a new liquidity pool is detected.

### **4. BinEdge**
Analyzes possible conversion paths on Binance to detect intra-exchange arbitrage opportunities.

**Detailed Description:**
BinEdge explores all possible trading paths within Binance to detect internal arbitrage opportunities:

- **Pathfinding Algorithm:** Implements a search algorithm to detect trading routes from asset A to B and back to A.
- **WebSocket Data:** Utilizes real-time data from Binance's WebSocket to ensure up-to-date analysis.
- **Profit Evaluation:** Evaluates each path based on trading fees and price spreads to identify profitable routes.

---

## Detailed Directory and Code Flow

### 1. **Exchange Integration Services**
Each integration service (Binance, ByBit, Kraken, KuCoin, OKX) implements the following key methods:
- `start_price_retrieval_thread()`: Initiates a background thread to continuously fetch and update prices.
- `fetch_latest_prices()`: Queries the respective API for the latest ticker information.
- `get_usdt_pairs_dictionary()`: Retrieves the USDT trading pairs and their respective prices.

**Example:**
`ByBitIntegrationService.py`
```python
self.price_retrieval_thread = threading.Thread(target=self._price_data_retrieval)
self.price_retrieval_thread_running = True
self.price_retrieval_thread.start()
```

### 2. **Telegram Communication Services**
- `TelegramConnectionService.py`: Sends notifications to subscribed users via Telegram Bot.
- `TelethonService.py`: Adds channels to listen for crypto-related news and processes messages to detect symbols.

**Main Functions:**
- `send_message_to_all_users()`: Sends a broadcast message.
- `start_client_with_phone_number()`: Initializes the Telethon client.

### 3. **Arbitrage Detection (`ArbiSense.py`)**
- Detects price differences between exchanges.
- Compares trading pairs and sends alerts for arbitrage opportunities.
- Uses threading to perform parallel data analysis.

### 4. **News Detection (`NewScout.py`)**
- Monitors channels and parses messages to extract relevant trading symbols.
- Broadcasts detected news to users via Telegram.

### 5. **Web Server (`main.py`)**
- Implements a Flask-based server that streams arbitrage data to clients.
- Uses Server-Sent Events (SSE) for real-time updates.

---

## API Configuration and Secrets
The `AppDataService.py` ensures that API keys and Telegram Bot tokens are securely stored in JSON files within the `keys` folder. The necessary keys and tokens include:
- `telegramBotToken`
- `api_id` (for Telethon)
- `api_hash` (for Telethon)
- `news_channels` (list of Telegram channels)

---

## Installation and Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## Exchange Support

### Centralized Exchanges
- Binance
- ByBit
- KuCoin
- Kraken
- OKX

### Decentralized Exchanges
- Raydium AMM V4 on Solana blockchain

---

## Accessing the Agent
- **Telegram:** The bot sends real-time alerts.
- **Web Interface:** Accessible via the `/stream` endpoint for real-time arbitrage data.

---

## Future Enhancements
- Add support for more decentralized exchanges.
- Implement machine learning models for predicting price movements.
- Support advanced filtering options for news updates.

---
