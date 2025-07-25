import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'trading_bot')))

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover('trading_bot/tests')
    runner = unittest.TextTestRunner()
    runner.run(suite)
