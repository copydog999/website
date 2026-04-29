"""
清理图片压缩备份文件
删除 database/data/avatar 目录下所有 .backup 文件
"""

import os
import sys


def clean_backups():
    """清理所有备份文件"""
    # 需要清理的目录
    dirs_to_clean = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'data', 'avatar'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'data', 'poster')
    ]
    
    print("=" * 60)
    print("清理图片压缩备份文件")
    print("=" * 60)
    print()
    
    total_backup_files = []
    
    # 遍历所有目录
    for target_dir in dirs_to_clean:
        if not os.path.exists(target_dir):
            print(f"警告: 目录不存在 - {target_dir}")
            continue
        
        print(f"扫描目录: {target_dir}")
        
        # 查找备份文件
        for filename in os.listdir(target_dir):
            if filename.endswith('.backup'):
                file_path = os.path.join(target_dir, filename)
                file_size = os.path.getsize(file_path)
                total_backup_files.append((file_path, filename, file_size))
                print(f"  找到: {filename} ({file_size / 1024:.2f} KB)")
        
        print()
    
    if not total_backup_files:
        print("未找到备份文件")
        return
    
    print(f"共找到 {len(total_backup_files)} 个备份文件\n")
    
    # 确认删除
    confirm = input("确认删除这些备份文件? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消操作")
        return
    
    # 删除备份文件
    deleted_count = 0
    total_size = 0
    
    for file_path, filename, file_size in total_backup_files:
        try:
            os.remove(file_path)
            deleted_count += 1
            total_size += file_size
            print(f"已删除: {filename}")
        except Exception as e:
            print(f"删除失败 {filename}: {str(e)}")
    
    print()
    print("=" * 60)
    print("清理完成!")
    print("=" * 60)
    print(f"删除文件数: {deleted_count}")
    print(f"释放空间: {total_size / 1024 / 1024:.2f} MB")


if __name__ == '__main__':
    clean_backups()

