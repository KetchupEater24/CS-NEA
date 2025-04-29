import re

# this script reads your existing quiz session code file (quizsession.py),
# lowercases all comment text, and writes out a new file quizsession_clean.py

def lowercase_comments(input_path: str, output_path: str):
    with open(input_path, 'r') as infile:
        lines = infile.readlines()

    with open(output_path, 'w') as outfile:
        for line in lines:
            if '#' in line:
                # split at first '#'
                parts = line.split('#', 1)
                code_part = parts[0]
                comment_part = parts[1]
                # lowercase comment text
                outfile.write(code_part + '#' + comment_part.lower())
            else:
                outfile.write(line)

if __name__ == '__main__':
    lowercase_comments('quizsession.py', 'quizsession_clean.py')
    print('Lowercased comments and saved to quizsession_clean.py')
