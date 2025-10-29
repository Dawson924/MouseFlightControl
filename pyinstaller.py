import os
import shutil
import subprocess


def main():
    folders_to_copy = ['assets', 'locales', 'presets', 'scripts']
    source_dir = os.getcwd()
    target_dir = os.path.join(source_dir, 'dist', 'MouseFlightControl')

    try:
        print('开始执行打包...')
        result = subprocess.run(
            ['pyinstaller', 'MouseFlightControl.spec', '--noconfirm'],
            check=True,
            capture_output=True,
            text=True,
        )
        print('打包完成!')
        print('输出信息:', result.stdout)

        # 检查目标目录是否存在
        if not os.path.exists(target_dir):
            print(f'错误: 目标目录 {target_dir} 不存在，打包可能失败。')
            return

        # 复制文件夹
        for folder in folders_to_copy:
            src = os.path.join(source_dir, folder)
            dest = os.path.join(target_dir, folder)

            # 检查源文件夹是否存在
            if not os.path.exists(src):
                print(f'警告: 源文件夹 {src} 不存在，跳过复制。')
                continue

            # 如果目标文件夹已存在，先删除
            if os.path.exists(dest):
                print(f'目标文件夹 {dest} 已存在，先删除...')
                if os.path.isfile(dest) or os.path.islink(dest):
                    os.unlink(dest)
                else:
                    shutil.rmtree(dest)

            # 复制文件夹
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
