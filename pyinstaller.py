import os
import shutil
import subprocess


def main():
    folders_to_copy = ['assets', 'i18n', 'Inits', 'Scripts', 'Lua', 'Joycons']
    source_dir = os.getcwd()
    target_dir = os.path.join(source_dir, 'out')

    try:
        print('开始执行打包...')
        result = subprocess.run(
            ['pyinstaller', '--distpath=out', 'pyinstaller.spec', '--noconfirm'],
            check=True,
            capture_output=True,
            text=True,
        )
        print('打包完成!')
        print('输出信息:', result.stdout)

        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        for folder in folders_to_copy:
            src = os.path.join(source_dir, folder)
            dest = os.path.join(target_dir, folder)

            if not os.path.exists(src):
                print(f'警告: 源文件夹 {src} 不存在，跳过复制。')
                continue

            if os.path.exists(dest):
                print(f'目标文件夹 {dest} 已存在，先删除...')
                if os.path.isfile(dest) or os.path.islink(dest):
                    os.unlink(dest)
                else:
                    shutil.rmtree(dest)

            print(f'正在复制 {src} 到 {dest}...')
            shutil.copytree(src, dest)
            print(f'复制 {folder} 完成。')

        print('所有操作完成。')

    except subprocess.CalledProcessError as e:
        print(f'pyinstaller执行失败: {e.stderr}')
    except Exception as e:
        print(f'发生错误: {str(e)}')


if __name__ == '__main__':
    main()
