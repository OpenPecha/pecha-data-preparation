from pathlib import Path
import shutil

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import FileNotDownloadableError

from .sanity_checks import SanityCheck


class DriveInterface:
    def __init__(self):
        self.drive = self.__login()
        self.file_types = {'spreadsheet': ['application/vnd.google-apps.spreadsheet',
                                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
                           'document': ['application/vnd.google-apps.document',
                                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document']}

    @staticmethod
    def __login():
        """
        Google Drive service with a service account.
        note: for the service account to work, you need to share the folder or
        files with the service account email.

        :return: google auth
        """
        # Define the settings dict to use a service account
        # We also can use all options available for the settings dict like
        # oauth_scope,save_credentials,etc.
        settings = {
            "client_config_backend": "service",
            "service_config": {
                "client_json_file_path": "service-secrets.json",
            }
        }
        # Create instance of GoogleAuth
        gauth = GoogleAuth(settings=settings)
        # Authenticate
        gauth.ServiceAuth()
        return GoogleDrive(gauth)

    def download_catalog(self, doc_path, doc_id):
        # can be generalized to become download_file()
        file = self.drive.CreateFile({'id': doc_id})
        print(f'\tdownloading "{file["title"]}"')
        try:
            file.GetContentFile(Path(doc_path) / (file["title"]), mimetype=self.file_types['spreadsheet'][1], )
        except FileNotDownloadableError:
            print('Links can not be downloaded. Passing...')
        return file["title"]

    def upload_catalog(self, doc_path, doc_id):
        params = {
            "title": doc_path.name,
            "mimeType": self.file_types["spreadsheet"][1],
            "id": doc_id
        }
        drive_file = self.drive.CreateFile(params)
        drive_file.SetContentFile(doc_path)
        convert = False  # convert or not to a Google Document
        drive_file.Upload(param={"convert": convert})

    def download_folder(self, local_path, drive_id):
        # create or empty local folder
        c_path = Path(local_path)
        if c_path.is_dir():
            shutil.rmtree(c_path)
        if not c_path.is_dir():
            c_path.mkdir(parents=True, exist_ok=True)

        # find all files in Drive
        file_list = self.drive.ListFile({"q": f"'{drive_id}' in parents and trashed=false",
                                         "supportsAllDrives": "true",
                                         "includeItemsFromAllDrives": "true"}).GetList()

        # add files in subfolders
        new_files = self.__list_subfolders(file_list)
        file_list.extend(new_files)

        SanityCheck.that_drive_files_are_pairs(file_list)

        # download files
        for file in file_list:
            if file['mimeType'] in self.file_types['spreadsheet']:
                print(f'\tdownloading "{file["title"]}.xlsx"')
                try:
                    file.GetContentFile(c_path / (file["title"] + ".xlsx"), mimetype=self.file_types["spreadsheet"][1],)
                except FileNotDownloadableError:
                    print('Links can not be downloaded. Passing...')

            elif file["mimeType"] in self.file_types["document"]:
                print(f'\tdownloading "{file["title"]}.docx"')
                try:
                    file.GetContentFile(c_path / (file["title"] + ".docx"), mimetype=self.file_types['document'][1],)
                except FileNotDownloadableError:
                    print('Links can not be downloaded. Passing...')

    def __list_subfolders(self, file_list):
        new_files = []
        for f in file_list:
            if 'folder' in f["mimeType"]:
                files = self.drive.ListFile({"q": f"'{f['id']}' in parents and trashed=false",
                                             "supportsAllDrives": "true",
                                             "includeItemsFromAllDrives": "true"}).GetList()
                new_files.extend(files)
        return new_files


class PushDriveFiles:
    def __init__(self):
        self.drive = self.__login()

    @staticmethod
    def __login():
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # client_secrets.json need to be in the same directory as the script
        return GoogleDrive(gauth)

    def push_files(self, files_list):
        for folder, file in files_list:
            print(f"uploading {file}")
            title = file.name if file.suffix == ".yaml" else file.stem
            params = {"title": title}

            if file.suffix == ".xlsx":
                params[
                    "mimeType"
                ] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif file.suffix == ".txt":
                params["mimeType"] = "text/plain"
            elif file.suffix == ".yaml":
                params["mimeType"] = "text/plain"
            elif file.suffix == ".docx":
                params[
                    "mimeType"
                ] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            else:
                print(f"{file}\nfile format not supported for upload.")
                continue

            docs_list = self.drive.ListFile(
                {"q": f"'{folder}' in parents and trashed=false"}
            ).GetList()
            for f in docs_list:
                if f["title"] == file.stem:
                    params["id"] = f["id"]

            if "id" not in params:
                params["parents"] = [{"id": folder}]

            drive_file = self.drive.CreateFile(params)
            drive_file.SetContentFile(file)
            convert = False if file.suffix == ".yaml" else True
            drive_file.Upload(param={"convert": convert})
