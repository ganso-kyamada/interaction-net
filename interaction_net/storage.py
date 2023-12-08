import csv
import os


class Storage:
    values = {
        "users": [],
        "grounds": [],
        "schedules": [],
    }

    def csv(self, name):
        if name not in self.values.keys():
            return []

        if len(self.values[name]) == 0:
            self.values[name] = self.__set_storage_rows(name)

        return self.values[name]

    def __set_storage_rows(self, name):
        rows = []
        filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f"storages/{name}.csv"
        )
        with open(filename) as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        return rows
