import argparse
import hashlib
import json
import os
import re

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
    parser = argparse.ArgumentParser()
    required_group = parser.add_mutually_exclusive_group(required=True)
    required_group.add_argument('--folder', '-f', type=str, help='Folder to rename files in')
    required_group.add_argument('--recovery', type=str, help='Recovery file to restore filenames')
    parser.add_argument('--recursive', '-r', action='store_true', help='recursively add files')
    parser.add_argument('--filetype', '--ft', type=str, default='*', help='Whitelist filetype. e.g: ".txt .csv". Defaults to *')
    parser.add_argument('--filefilter', '--ff', type=str, help='Whitelist files based on filename, using regex')
    parser.add_argument('--replace', type=str, help='Filename string to replace')
    parser.add_argument('--pattern', type=str, help='Renaming pattern')
    parser.add_argument('--ignore-checksum', dest='ignore_checksum', action='store_true', help='Store checksums when renaming')
    args = parser.parse_args()

    print(f'{args.recovery=}')
    if args.recovery:
        print(f'Restoring files from: {args.recovery}')
        file_changes = parse_recovery_file(args)
        print(f'Found: {len(file_changes)} file change(s)')
        success, failed = restore_changes(args, file_changes)
        print(f'Successfully restored: {success}, failed to restore: {failed}')
        return
    print(f'{args.folder=}')
    print(f'{args.recursive=}')
    print(f'{args.filetype=}')
    print(f'{args.filefilter=}')
    print(f'{args.replace=}')
    print(f'{args.pattern=}')
    print(f'{args.ignore_checksum=}')
    args.filetype = clean_filetype(args.filetype)
    args.folder = f'{os.getcwd()}{args.folder}'
    file_changes = change_files(args.folder, args)
    create_recovery_file(args, file_changes)

# Restores changes by recovery file
def restore_changes(args, file_changes):
    success = 0
    failed = 0
    for fc in file_changes:
        try:
            if args.ignore_checksum:
                os.rename(fc.filepath, fc.old_filepath)
            else:
                hash = get_hash(fc.filepath)
                if hash == fc.hash:
                    os.rename(fc.filepath, fc.old_filepath)
                else:
                    print(f'Failed to restore: {fc.filepath}, checksum not matching.\n{fc.hash} - {hash}')
            success += 1
        except Exception as e:
            print(e)
            failed += 1
    return success, failed

# Parses a recovery file
def parse_recovery_file(args):
    try:
        with open(args.recovery) as f:
            data = json.loads(f.read())
        args.folder = data.get("folder")
        args.recursive = data.get("recursive")
        args.filetype = clean_filetype(data.get("filetype"))
        args.replace = data.get("replace")
        args.pattern = data.get("pattern")
        
        file_changes = []
        file_changes_data = data.get("file_changes")
        for fc in file_changes_data:
            file_changes.append(FileChange(fc['filepath'], fc['old_filepath'], fc['hash']))
        return file_changes
    except Exception as e:
        print(e)

# Creates a json file to restore changes made
def create_recovery_file(args, file_changes):
    if len(file_changes) <= 0:
        print('No changes made')
        return

    save_data = {
        'folder': args.folder,
        'recursive': args.recursive,
        'filetype': ' '.join(args.filetype),
        'replace': args.replace,
        'pattern': args.pattern,
        'file_changes': [obj.to_dict() for obj in file_changes]
    }
    try:
        json_data = json.dumps(save_data, ensure_ascii=False, indent=4)
        with open('recovery.json', 'w') as f:
            f.write(json_data)
    except Exception as e:
        print(e)

# Clean filetype from input
def clean_filetype(filetype):
    return filetype.split(' ')

# Checks the file extension to the filetype filter
def check_extension(extension, filetype):
    if filetype == ['*']:
        return True
    return extension in filetype

# Gets all files based on folder, filetype and recursive
def change_files(start_folder, args):
    file_changes = []
    folder_searched.append(start_folder)
    index = 1
    
    for file in os.listdir(start_folder):
        filepath = f'{start_folder}{file}'
        if os.path.isdir(filepath):
            if args.recursive is False:
                continue
            if filepath not in folder_searched:
                file_changes.extend(change_files(f'{filepath}\\', args))
        else:
            extension = os.path.splitext(filepath)[1]
            if check_extension(extension, args.filetype):
                if args.filefilter is not None:
                    if file_match(file, args.filefilter):
                        new_filepath, hash = change_filename(filepath, index, args)
                        file_changes.append(FileChange(new_filepath, filepath, hash))
                else:
                    new_filepath, hash = change_filename(filepath, index, args)
                    file_changes.append(FileChange(new_filepath, filepath, hash))
            index += 1
    return file_changes

# Matches filename to filefilter using regex
def file_match(file, filefilter):
    try:
        s = re.search(filefilter, file)
        return False if s is None else True
    except Exception as e:
        print(e)

# Gets checksum from a file
def get_hash(file):
    sha256 = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

# Changes a filename based on args given
def change_filename(old_filepath, index, args):
    extension = os.path.splitext(old_filepath)[1]
    filename = os.path.basename(old_filepath)
    filename = filename[0:-len(extension)]
    path = os.path.dirname(old_filepath)
    
    if args.replace is None:
        filename = args.pattern
    else:
        filename = filename.replace(args.replace, args.pattern)
    
    filename = filename_increment(filename, index)

    filepath = f'{path}\\{filename}{extension}'
    if old_filepath == filepath:
        return None, None
    
    hash = None
    if args.ignore_checksum is False:
        hash = get_hash(old_filepath)
    
    try:
        os.rename(old_filepath, filepath)
        return filepath, hash
    except OSError as oe:
        print(oe)
        return None, None
    except Exception as e:
        print(e)
        return None, None

# Replaces ? in args.pattern and replaces it with incremental numbers, 0-padded for each ?
def filename_increment(filename, index):
    digits = filename.count('?')
    if digits <= 0:
        return filename

    loc = filename.find('?')
    padding = digits - len(str(index))
    index_num = index
    if padding > 0:
        index_num = f'{"0" * padding}{index}'

    filename = f'{filename[:loc]}{index_num}{filename[loc:]}'
    filename = filename.replace('?', '')
    return filename

if __name__ == '__main__':
    main()