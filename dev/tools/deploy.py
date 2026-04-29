import os
import zipfile
import subprocess
from pathlib import Path


def create_deploy_zip():
    # 获取项目根目录 - 从 tools 目录向上两级
    project_dir = Path(__file__).parent.parent.parent

    # 获取脚本文件名
    script_name = Path(__file__).name

    # 获取当前脚本的相对路径（相对于项目根目录）
    current_script_path = Path(__file__).relative_to(project_dir)

    # 需要排除的文件夹(系统和版本控制)
    excluded_folders = {'.idea', '.git', 'dev', 'articles', 'System Volume Information','$RECYCLE.BIN','dev_guidelines.md'}

    # 输出文件路径（在项目根目录）
    zip_path = project_dir / 'deploy.zip'

    print(f"正在创建压缩包: {zip_path}")
    print(f"排除的文件夹: {excluded_folders}")
    print(f"排除的脚本: {script_name}")

    # 创建zip文件
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历项目根目录下的所有文件和文件夹
        for item in project_dir.rglob('*'):
            # 跳过 deploy.zip 和 deploy.py 本身
            if item.name == 'deploy.zip' or item.name == script_name:
                continue
            should_exclude = False
            for part in item.parts:
                if part in excluded_folders:
                    should_exclude = True
                    break

            if should_exclude:
                print(f"排除文件夹: {item.relative_to(project_dir)}")
                continue

            # 计算在zip中的相对路径（相对于项目根目录）
            arcname = item.relative_to(project_dir)

            if item.is_file():
                print(f"添加文件: {arcname}")
                zipf.write(item, arcname)
            elif item.is_dir():
                # 确保空文件夹也被包含
                if not any(item.iterdir()):
                    print(f"添加空文件夹: {arcname}")
                    zipf.write(item, arcname)

    print(f"\n完成! 压缩包已创建: {zip_path}")
    print(f"文件大小: {zip_path.stat().st_size / 1024:.2f} KB")


if __name__ == '__main__':
    try:
        create_deploy_zip()
        # 用资源管理器打开压缩包所在位置
        subprocess.run(['explorer', '/select,', str(Path(__file__).parent.parent.parent / 'deploy.zip')], shell=True)
        # 打开Netlify页面
        subprocess.run(['start', 'https://app.netlify.com/projects/journalofest/overview'], shell=True)
    except Exception as e:
        print(f"创建压缩包时出错: {e}")