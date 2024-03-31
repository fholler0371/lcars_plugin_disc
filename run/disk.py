import sys
if __name__ == '__main__':
    BASE_PATH = sys.argv[1]
    del sys.argv[1]
else:
    BASE_PATH = None
import asyncio
import json
import argparse


from pprint import pprint


async def format_drive(drive: str, mode: str)->None:
    match mode:
        case 'ext4':
            cmd = f'sudo mkfs.ext4 -F /dev/{drive}'
            err_pos = 1
        case 'vfat':
            cmd = f'sudo mkfs.vfat /dev/{drive}'
            err_pos = 0
        case _:
            print('Unbekanntes Format')
            return
    p = await asyncio.subprocess.create_subprocess_shell(cmd, 
                                                         stderr=asyncio.subprocess.PIPE, 
                                                         stdout=asyncio.subprocess.PIPE)
    out, err = await p.communicate()
    err = err.decode().split('\n')[err_pos:]
    if len(err) > 0:
        print()
        print('\n'.join(err))

async def mount(drive: str, folder: str)->None:
    p = await asyncio.subprocess.create_subprocess_shell(f'sudo mkdir -p {folder}', 
                                                         stderr=asyncio.subprocess.PIPE, 
                                                         stdout=asyncio.subprocess.PIPE)
    await p.wait()
    p = await asyncio.subprocess.create_subprocess_shell(f'sudo mount /dev/{drive} {folder}', 
                                                         stderr=asyncio.subprocess.PIPE, 
                                                         stdout=asyncio.subprocess.PIPE)
    await p.wait()

async def umount(folder: str)->None:
    p = await asyncio.subprocess.create_subprocess_shell(f'sudo umount {folder}', 
                                                         stderr=asyncio.subprocess.PIPE, 
                                                         stdout=asyncio.subprocess.PIPE)
    await p.wait()

async def get_drives():
    p = await asyncio.subprocess.create_subprocess_shell('lsblk -J -o UUID,NAME,SIZE,MOUNTPOINT,FSTYPE', 
                                                         stderr=asyncio.subprocess.PIPE, 
                                                         stdout=asyncio.subprocess.PIPE)
    out, _ = await p.communicate()
    for data in json.loads(out.decode()).get('blockdevices', []):
        for drive in data.get('children', []):
            yield (drive.get('name', ''), drive.get('size', ''), drive.get('mountpoint', '') if drive.get('mountpoint') is not None else '', drive.get('uuid', ''),
                   drive.get('fstype', ''))  

async def main()->None:
    parser = argparse.ArgumentParser(prog='lcars-disk',
                                     description='Laufwerkstool')
    subparser = parser.add_subparsers()
    format = subparser.add_parser("format", help='Formatieren von Laufwerken')
    format.add_argument("drive", type=str, help='Laufwerk ohne /dev/')
    format.add_argument("-t", '--type', choices=['ext4', 'vfat'], default='ext4', help='Laufwerk ohne /dev/')
    format.set_defaults(mode='format')
    format = subparser.add_parser("mount", help='Mounten eines Laufwerkes')
    format.add_argument("drive", type=str, help='Laufwerk ohne /dev/')
    format.add_argument("folder", type=str, help='Order an den gebunden werden soll')
    format.set_defaults(mode='mount')
    format = subparser.add_parser("umount", help='Unmounten eines Laufwerkes')
    format.add_argument("folder", type=str, help='Order an dem entfernt werden soll')
    format.set_defaults(mode='umount')
    #parser.add_argument('-f', action='store_true', dest='format', help='Formatieren von Laufwerk')
    #subparsers.add_argument('-d', '--drive', dest='drive', help='Name des Laufwerkes')
    #subparsers.add_argument('--formattype', dest='format_type', help='Name des Laufwerkes', choices=['ext4', 'vfat'], default='ext4')
    args = parser.parse_args()
    if hasattr(args, 'mode') and args.mode == 'format':
        await format_drive(args.drive, args.type)
    elif hasattr(args, 'mode') and args.mode == 'mount':
        await mount(args.drive, args.folder)
    elif hasattr(args, 'mode') and args.mode == 'umount':
        await umount(args.folder)
    else:
        async for entry in get_drives():
            print(f'{entry[0]: <15}{entry[1]: >6} {entry[2]: <25} {entry[4]: <6} {entry[3]} ')

if __name__ == '__main__':
    asyncio.run(main())