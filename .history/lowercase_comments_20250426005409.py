import re

def lowercase_comments(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile:
        lines = infile.readlines()

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for line in lines:
            if '#' in line:
                code, comment = line.split('#', 1)
                outfile.write(code + '#' + comment.lower())
            else:
                outfile.write(line)

if __name__ == '__main__':
    lowercase_comments('quizsession.py', 'quizsession_clean.py')
    print('Lowercased comments and saved to quizsession_clean.py')
