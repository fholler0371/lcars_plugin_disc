import sys

def add_it(record: str)->None:
    lines = []
    with open('/etc/fstab') as f:
        data = f.read()
        for _ in range(5):
            data = data.replace('\n\n', '\n')
        lines = data.split('\n')
    with open('/etc/fstab', 'w') as f:
        f.write('\n'.join(lines))
        f.write(record.replace("!", "\t"))
        f.write('\n\n')

def delete_it(folder: str)->None:
    lines = []
    with open('/etc/fstab') as f:
        data = f.read()
        for _ in range(5):
            data = data.replace('\n\n', '\n')
        lines = data.split('\n')
    index = -1
    for idx, line in enumerate(lines):
        if folder in line:
            index = idx
    if index > -1:
        del lines[index]
    with open('/etc/fstab', 'w') as f:
        f.write('\n'.join(lines))
        f.write('\n')

if __name__ == '__main__':
    match sys.argv[1]:
        case 'del':
            delete_it(sys.argv[2])
        case 'add':
            add_it(sys.argv[2])
        case _:
            print('hallo')
            print(sys.argv)