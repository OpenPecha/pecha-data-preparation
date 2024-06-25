from pathlib import Path
import yaml
import textwrap

from .google_drive import DriveInterface
from .catalog_manager import CatalogManager


class DriveManager:
    def __init__(self):
        self.conf = self.__config()

    @staticmethod
    def __config():
        template = textwrap.dedent('''\
            data_drive_folder_id: ''
            data_local_folder_path: ''
            catalog_doc_id: ''
            catalog_doc_path: ''
            ''')
        conf = Path('pecha_config.yaml')
        if not conf.is_file():
            conf.write_text(template)
            print('A new config file has been created. Please fill in the empty fields.')
            return yaml.safe_load(template)
        else:
            return yaml.safe_load(conf.read_text())

    def parse_gdrive(self):
        local_path = self.conf['data_local_folder_path']
        drive_id = self.conf['data_drive_folder_id']
        catalog_path = self.conf['catalog_doc_path']
        catalog_id = self.conf['catalog_doc_id']
        drive = DriveInterface()

        # A download all the files in the folder
        drive.download_folder(local_path, drive_id)

        # B.1 download the catalog
        catalog_name = drive.download_catalog(catalog_path, catalog_id)

        # B.2 parse the catalog
        # # catalog_name = 'Pecha Text Catalog.xlsx'
        catalog_file_path = Path(catalog_path) / catalog_name
        cm = CatalogManager(catalog_file_path, local_path)

        # B.3 add new files in catalog + push updated catalog to Drive
        catalog_updated = cm.include_new_texts(local_path)

        # B.4 upload updated catalog to Drive
        # # catalog_updated = True
        if catalog_updated:
            drive.upload_catalog(catalog_file_path, catalog_id)
            print()
