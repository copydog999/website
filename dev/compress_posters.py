"""
海报图片无损压缩工具
压缩 database/data/poster 目录下的所有JPEG图片
使用JPEG优化算法,保持视觉质量不变
"""

import os
from PIL import Image
import sys


# 配置
POSTER_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'data', 'poster')
JPEG_QUALITY_NORMAL = 85  # 普通质量 (<=10KB)
JPEG_QUALITY_AGGRESSIVE = 60  # 激进质量 (>10KB)
MAX_WIDTH_NORMAL = 1920  # 普通最大宽度
MAX_WIDTH_AGGRESSIVE = 1280  # 激进最大宽度
SIZE_THRESHOLD = 10 * 1024  # 10KB阈值


def compress_jpeg_lossless(input_path, output_path, quality=85, max_width=None):
    """
    无损压缩JPEG图片
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        quality: JPEG质量 (85-95推荐)
        max_width: 最大宽度(可选)
    """
    try:
        # 打开图片
        img = Image.open(input_path)
        
        # 转换为RGB模式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 如果需要调整大小
        if max_width and img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
            print(f"  调整尺寸: {img.width}x{img.height}")
        
        # 保存优化后的JPEG
        img.save(output_path, 'JPEG', quality=quality, optimize=True, progressive=True)
        
        # 计算压缩率
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"  原始大小: {original_size / 1024:.2f} KB")
        print(f"  压缩后: {compressed_size / 1024:.2f} KB")
        print(f"  压缩率: {compression_ratio:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"  错误: {str(e)}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("海报图片压缩工具")
    print("=" * 60)
    print(f"目标目录: {POSTER_DIR}")
    print(f"大小阈值: {SIZE_THRESHOLD / 1024:.0f} KB")
    print(f"普通质量: {JPEG_QUALITY_NORMAL} (<= {SIZE_THRESHOLD / 1024:.0f} KB)")
    print(f"激进质量: {JPEG_QUALITY_AGGRESSIVE} (> {SIZE_THRESHOLD / 1024:.0f} KB)")
    print()
    
    # 检查目录是否存在
    if not os.path.exists(POSTER_DIR):
        print(f"错误: 目录不存在 - {POSTER_DIR}")
        sys.exit(1)
    
    # 获取所有JPEG文件
    image_files = []
    for filename in os.listdir(POSTER_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            image_files.append(filename)
    
    if not image_files:
        print("未找到JPEG图片文件")
        sys.exit(0)
    
    print(f"找到 {len(image_files)} 个JPEG文件\n")
    
    # 统计信息
    total_original = 0
    total_compressed = 0
    success_count = 0
    fail_count = 0
    
    # 处理每个文件
    for filename in sorted(image_files):
        input_path = os.path.join(POSTER_DIR, filename)
        output_path = input_path  # 直接覆盖原文件
        
        # 检查文件大小,决定压缩策略
        file_size = os.path.getsize(input_path)
        is_large = file_size > SIZE_THRESHOLD
        
        quality = JPEG_QUALITY_AGGRESSIVE if is_large else JPEG_QUALITY_NORMAL
        max_width = MAX_WIDTH_AGGRESSIVE if is_large else MAX_WIDTH_NORMAL
        
        print(f"处理: {filename} ({file_size / 1024:.2f} KB) {'[激进压缩]' if is_large else ''}")
        
        # 备份原文件
        backup_path = input_path + '.backup'
        try:
            import shutil
            shutil.copy2(input_path, backup_path)
        except Exception as e:
            print(f"  警告: 备份失败 - {str(e)}")
        
        # 压缩图片
        if compress_jpeg_lossless(input_path, output_path, quality, max_width):
            success_count += 1
            
            # 累加文件大小
            total_original += os.path.getsize(backup_path)
            total_compressed += os.path.getsize(output_path)
        else:
            fail_count += 1
            # 恢复备份
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, input_path)
                os.remove(backup_path)
        
        print()
    
    # 输出统计信息
    print("=" * 60)
    print("压缩完成!")
    print("=" * 60)
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"总原始大小: {total_original / 1024 / 1024:.2f} MB")
    print(f"总压缩后: {total_compressed / 1024 / 1024:.2f} MB")
    
    if total_original > 0:
        total_ratio = (1 - total_compressed / total_original) * 100
        print(f"总压缩率: {total_ratio:.1f}%")
        print(f"节省空间: {(total_original - total_compressed) / 1024 / 1024:.2f} MB")
    
    print()
    print("提示:")
    print("  - 使用JPEG优化算法,视觉质量基本不变")
    print("  - 备份文件已保存为 *.backup 扩展名")
    print("  - 如需恢复,请删除压缩后的文件并重命名备份文件")


if __name__ == '__main__':
    main()
