from fileread.last_lines import last_lines

if __name__ == "__main__":
    for line in last_lines('data/test.txt'):
        print(line, end='')
