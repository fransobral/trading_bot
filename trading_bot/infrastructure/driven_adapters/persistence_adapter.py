import csv
import pandas as pd

class PersistenceAdapter:
    def __init__(self, config):
        self.config = config

    def save_trades(self, trades):
        if not trades:
            return

        df = pd.DataFrame(trades)
        df.to_csv(self.config['persistence']['trades_file'], index=False)

    def save_metrics(self, metrics):
        with open(self.config['persistence']['metrics_file'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(metrics.keys())
            writer.writerow(metrics.values())
