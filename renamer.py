import argparse
import os

def main():
    args = parse_arguments()

    print(f'{args.folder=}')
    print(f'{os.path.isabs(args.folder)=}')
    print(f'{os.path.isdir(args.folder)=}')

    print(get_path(args.folder))

def parse_arguments():
    parser = argparse.ArgumentParser()
    required_group = parser.add_mutually_exclusive_group(required=True)
    required_group.add_argument('--folder', '-f', type=str, help='Folder to rename files in')
    args = parser.parse_args()
    return args

def get_path(path):
    return os.path.abspath(path)

if __name__ == '__main__':
    main()