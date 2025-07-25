# Python Trading Bot

This is a trading bot built with Python using a clean (hexagonal) architecture. It supports backtesting and live trading on Binance.

## Features

- **Multiple Strategies**: Implements several trading strategies including EMA Cross, RSI, MACD, EMA Rebound, and Bollinger Bands Breakout.
- **Risk Management**: Configurable risk per trade, take profit, and stop loss.
- **Backtesting**: Test your strategies on historical data.
- **Live Trading**: Run the bot with your Binance account.
- **Persistence**: Saves trades, logs, and performance metrics to CSV files.
- **Dockerized**: Easy to set up and run with Docker.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/trading-bot.git
   cd trading-bot
   ```

2. **Set up your environment variables:**
   - Create a `.env` file by copying the example:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file and add your Binance API key and secret:
     ```
     BINANCE_API_KEY=your_api_key
     BINANCE_API_SECRET=your_api_secret
     ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

## Usage

### Backtesting

To run the bot in backtest mode, use the following command:

```bash
python main.py --mode backtest
```

This will fetch historical data, run the strategies, and generate `trades.csv` and `metrics.csv` files.

### Live Trading

To run the bot in live mode, use the following command:

```bash
python main.py --mode live
```

**Note:** Live trading is not fully implemented yet.

## Configuration

The main configuration is in the `config.yml` file. Here you can enable/disable strategies, adjust parameters, and set risk management rules.

## Adding Binance API Keys

1.  Log in to your Binance account.
2.  Go to **API Management**.
3.  Create a new API key.
4.  Make sure to enable trading permissions.
5.  Copy the API key and secret key into your `.env` file.

## Running Tests

To run the tests, use the following command:

```bash
python -m unittest discover -s tests
```
