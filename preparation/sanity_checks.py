from collections import defaultdict


class SanityCheck:
    def __init__(self):
        pass

    @staticmethod
    def drive_files_are_pairs(file_list):
        """
        currently only checks that there are no less and no more than 2 files with the same name in the folder

        used in google_drive.py class RetrieveDriveFiles().download_folder()

        :param file_list: list of Google Drive files
        :return:
        """
        EXPECTED = 2
        check = defaultdict(int)
        for f in file_list:
            if 'folder' in f['mimeType']:
                continue
            else:
                check[f['title']] += 1

        for name, count in check.items():
            if count != EXPECTED:
                print(f'!!! {count} file for "{name}".\t\t\tExpected: 2 (1 document and 1 spreadsheet)')
        print('')
