import csv
import os


class Storage:
    def csv(self, name):
        rows = []
        filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f"storages/{name}.csv"
        )
        with open(filename) as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        return rows
