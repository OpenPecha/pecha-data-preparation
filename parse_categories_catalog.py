import yaml
from pathlib import Path

from preparation import DriveManager


dm = DriveManager()
catalog = dm.download_n_parse_catalog()
print(catalog)