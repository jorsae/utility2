import glob
import hashlib
import os, sys
import shutil
import datetime

if len(sys.argv) != 2:
    print(f'Usage: {sys.argv[0]} <path>')
    sys.exit()


backup_folder = f'dd-backups-{datetime.datetime.now().timestamp()}'
os.mkdir(backup_folder)

output_file = f'{backup_folder}\changes.txt'
output = open(output_file, 'w')
output.write(f'===== DUPLICATES FOUND =====\n\n')

hashes = []
for file in glob.glob(f'{sys.argv[1]}'):
    if os.path.isdir(file):
        continue
    ff = open(file, 'rb').read()
    hash = hashlib.sha256(ff).hexdigest()
    if hash in hashes:
        filename = os.path.basename(file)
        print(f'Duplicate: {filename} : {hash}')
        output.write(f'[{hash}]: {file} --> {os.getcwd()}\{backup_folder}\{filename}\n')
        shutil.move(file, f'{os.getcwd()}\{backup_folder}\{filename}')
    else:
        hashes.append(hash)