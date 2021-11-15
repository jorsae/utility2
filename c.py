import argparse
import os
import re

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', '-F', type=str, help='Folder for mp4/mkv files')
    parser.add_argument('--file', '-f', type=str, help='Single file')
    parser.add_argument('--filetype', '--ft', type=str, default='.vtt',  help='Whitelist filetype. default: .vtt')
    args = parser.parse_args()
    if args.file:
        convert_file(args.file)
    if args.folder:
        print(args.filetype)
        if args.folder.endswith('\\') is False:
            args.folder = f'{args.folder}\\'
        for f in os.listdir(args.folder):
            if f.endswith(args.filetype):
                convert_file(f, args.folder)


def convert_file(file, folder = ''):
    print(f'Converting file: {folder}{file}')
    with open(f'{folder}{file}', 'r', encoding='utf-8') as f:
        new_file = open(f'{folder}new_{file}', 'w')
        diff_file = open(f'{folder}diff_{file}', 'w')
        
        line = f.readline()
        line_count = 1
        while line:
            made_changes = False
            line = line.strip()
            original_line = line

            line, c1 = fix_star(line)
            line, c2 = fix_l(line)
            line, c3 = fix_ticks(line)
            s = c1 + c2 + c3
            
            if s > 0:
                diff_file.write(f'{str(line_count)}\t{str(s)}\n')
                diff_file.write(f'{original_line}\n')
                diff_file.write(f'{line}\n\n')
            new_file.write(f'{line}\n')
                
            line = f.readline()
            line_count += 1

def fix_star(line):
    if '*' in line:
        return line.replace('*', 'b'), 1
    return line, 0

def fix_l(line):
    changes = 0
    last_alpha = False
    lines = list(line)
    for i in range(len(lines)):
        if lines[i] == 'I' and last_alpha:
            lines[i] = 'l'
            changes += 1

        if lines[i].isalpha():
            last_alpha = True
        else:
            last_alpha = False
    return ''.join(lines), changes

def fix_ticks(line):
        ticks = re.findall(r" '", line)
        if len(ticks) <= 0:
            return line, 0
        
        line = line.replace(" '", "'")
        return line, 1

if __name__ == '__main__':
    main()