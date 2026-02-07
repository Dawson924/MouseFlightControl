import os
import shutil
import subprocess
import sys


def main():
    source_dir = os.getcwd()
    spec_file = os.path.join(source_dir, 'pyinstaller.spec')
    target_dir = os.path.join(source_dir, 'out')

    print(f'Working directory: {source_dir}')
    print(f'Python executable: {sys.executable}')
    print(f'PyInstaller spec file: {spec_file}')
    print(f'Target directory: {target_dir}')

    if not os.path.exists(spec_file):
        print(f'Error: PyInstaller spec file {spec_file} not found')
        print('File list in current directory:')
        for file in os.listdir(source_dir):
            print(f'  - {file}')
        sys.exit(1)

    try:
        print('\nStarting PyInstaller packaging...')

        subprocess.run(
            [
                sys.executable,
                '-m',
                'PyInstaller',
                '--distpath=out',
                spec_file,
                '--noconfirm',
            ],
            check=True,
            cwd=source_dir,
            encoding='utf-8',
            errors='replace',
        )

        print('\nPyInstaller packaging completed!\n\n')

        os.makedirs(target_dir, exist_ok=True)
        print(f'Confirmed target directory exists: {target_dir}')

        folders_to_copy = ['assets', 'i18n', 'Inits', 'Scripts', 'Lua', 'Joycons']

        for folder in folders_to_copy:
            src = os.path.join(source_dir, folder)
            dest = os.path.join(target_dir, folder)

            if not os.path.exists(src):
                print(f'Warning: Source folder {src} does not exist, skip copying.')
                continue

            if os.path.exists(dest):
                print(f'Target folder {dest} already exists, deleting first...')
                if os.path.isfile(dest) or os.path.islink(dest):
                    os.unlink(dest)
                else:
                    shutil.rmtree(dest, ignore_errors=True)

            print(f'Copying {src} to {dest}...')
            shutil.copytree(src, dest, ignore_dangling_symlinks=True)
            print(f'Copy of {folder} completed.')

        print('\nAll packaging and copying operations completed.')

    except subprocess.CalledProcessError as e:
        print(f'\nPyInstaller execution failed, return code: {e.returncode}')
        print(f'Failed command: {" ".join(e.cmd)}')
        sys.exit(e.returncode)
    except FileNotFoundError as e:
        print(f'\nFile not found error: {str(e)}')
        sys.exit(1)
    except PermissionError as e:
        print(f'\nPermission error: {str(e)}')
        sys.exit(1)
    except Exception as e:
        print(f'\nUnknown error: {str(e)}')
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
