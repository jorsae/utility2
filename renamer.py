import argparse
import os


folder_searched = []

class FileChange():
    def __init__(self, filepath, old_filepath, hash):
        self.filepath = filepath
        self.old_filepath = old_filepath
        self.hash = hash
    
    def __str__(self):
        return f'{self.filepath} - {self.old_filepath} | {self.hash}'

    def to_dict(self):
        return { 'filepath': self.filepath, 'old_filepath': self.old_filepath, 'hash': self.hash }

def main():
    args = parse_arguments()

    print(f'{args.folder=}')
    print(f'{os.path.isabs(args.folder)=}')
    print(f'{os.path.isdir(args.folder)=}')
    print(f'{args.recursive=}')
    print(f'{args.filetype=}')

    print(get_path(args.folder))
    fo, fi = change_files(args, f'{get_path(args.folder)}\\')
    print(f'folder: {fo}')
    print(f'files: {fi}')

def parse_arguments():
    parser = argparse.ArgumentParser()
    required_group = parser.add_mutually_exclusive_group(required=True)
    required_group.add_argument('--folder', '-f', type=str, help='Folder to rename files in')
    parser.add_argument('--recursive', '-r', action='store_true', help='recursively add files')
    parser.add_argument('--filetype', '--ft', type=str, default='*', help='Whitelist filetype. e.g: ".txt .csv". Defaults to *')
    args = parser.parse_args()

    args.filetype = clean_filetype(args.filetype)
    return args

def get_path(path):
    return os.path.abspath(path)

# Clean filetype from input
def clean_filetype(filetype):
    return filetype.split(' ')

# Checks the file extension to the filetype filter
def check_extension(filepath, filetype):
    extension = os.path.splitext(filepath)[1]
    if filetype == ['*']:
        return True
    return extension in filetype

# Gets all files based on folder, filetype and recursive
def change_files(args, start_folder):
    folder_searched.append(start_folder)
    files_count = 0
    folder_count = 0
    
    for file in os.listdir(start_folder):
        filepath = f'{start_folder}{file}'
        if os.path.isdir(filepath):
            folder_count += 1
            print(f'{filepath} | dir')
            if args.recursive is False:
                continue
            if filepath not in folder_searched:
                print(f'extend: {filepath}')
                fo_s, fi_s = change_files(args, f'{filepath}\\')
                files_count += fi_s
                folder_count += fo_s
        else:
            files_count += 1
            print(f'{filepath} | file')
            extension = os.path.splitext(filepath)[1]
            if check_extension(extension, args.filetype):
                pass
    return folder_count, files_count

if __name__ == '__main__':
    main()  