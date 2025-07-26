import argparse
import yaml
from dotenv import load_dotenv
import os
import sys

# Agregar el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.backtesting_service import BacktestingService
from infrastructure.driven_adapters.exchange_adapter import ExchangeAdapter
from infrastructure.driven_adapters.persistence_adapter import PersistenceAdapter
from infrastructure.driven_adapters.logging_adapter import LoggingAdapter

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description='Trading Bot')
    parser.add_argument('--mode', type=str, required=True, choices=['backtest', 'live'], help='Execution mode')
    args = parser.parse_args()

    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)

    # Replace placeholders with environment variables
    config['exchange']['api_key'] = os.getenv('BINANCE_API_KEY')
    config['exchange']['api_secret'] = os.getenv('BINANCE_API_SECRET')

    logging_adapter = LoggingAdapter(config)
    exchange_adapter = ExchangeAdapter(config)
    persistence_adapter = PersistenceAdapter(config)

    if args.mode == 'backtest':
        logging_adapter.log_info('Running in backtest mode')
        backtesting_service = BacktestingService(config, exchange_adapter, persistence_adapter)
        backtesting_service.run()
    elif args.mode == 'live':
        logging_adapter.log_info('Running in live mode')
        # Live trading logic would go here
        pass

if __name__ == '__main__':
    main()
