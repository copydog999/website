"""
头像和背景图片压缩工具
压缩 database/data/avatar 目录下的所有图片文件
"""

import os
from PIL import Image
import sys

# 配置
AVATAR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'data', 'avatar')
QUALITY_AVATAR = 30  # 头像质量 (1-100)
QUALITY_BACKGROUND = 20  # 背景质量 (1-100)
MAX_WIDTH_AVATAR = 150  # 头像最大宽度
MAX_WIDTH_BACKGROUND = 640  # 背景最大宽度


def compress_image(input_path, output_path, quality, max_width=None):
    """
    压缩单张图片
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        quality: JPEG质量 (1-100)
        max_width: 最大宽度(可选),保持宽高比缩放
    """
    try:
        # 打开图片
        img = Image.open(input_path)
        
        # 如果是PNG且有透明度,转换为RGBA
        if img.mode == 'P':
            img = img.convert('RGBA')
        
        # 如果需要调整大小
        if max_width and img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
            print(f"  调整尺寸: {img.width}x{img.height}")
        
        # 保存为JPEG (背景) 或 PNG (头像)
        file_ext = os.path.splitext(output_path)[1].lower()
        
        if file_ext == '.jpg' or file_ext == '.jpeg':
            # JPEG格式:转换为RGB
            if img.mode in ('RGBA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
        elif file_ext == '.png':
            # PNG格式:保持原模式
            img.save(output_path, 'PNG', optimize=True)
        
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
    print("头像和背景图片压缩工具")
    print("=" * 60)
    print(f"目标目录: {AVATAR_DIR}")
    print()
    
    # 检查目录是否存在
    if not os.path.exists(AVATAR_DIR):
        print(f"错误: 目录不存在 - {AVATAR_DIR}")
        sys.exit(1)
    
    # 获取所有图片文件
    image_files = []
    for filename in os.listdir(AVATAR_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_files.append(filename)
    
    if not image_files:
        print("未找到图片文件")
        sys.exit(0)
    
    print(f"找到 {len(image_files)} 个图片文件\n")
    
    # 统计信息
    total_original = 0
    total_compressed = 0
    success_count = 0
    fail_count = 0
    
    # 处理每个文件
    for filename in sorted(image_files):
        input_path = os.path.join(AVATAR_DIR, filename)
        output_path = input_path  # 直接覆盖原文件
        
        # 跳过已处理的备份文件
        if filename.endswith('_backup.png') or filename.endswith('_backup.jpg'):
            continue
        
        print(f"处理: {filename}")
        
        # 判断是头像还是背景
        is_background = 'background' in filename.lower()
        quality = QUALITY_BACKGROUND if is_background else QUALITY_AVATAR
        max_width = MAX_WIDTH_BACKGROUND if is_background else MAX_WIDTH_AVATAR
        
        # 备份原文件
        backup_path = input_path + '.backup'
        try:
            import shutil
            shutil.copy2(input_path, backup_path)
        except Exception as e:
            print(f"  警告: 备份失败 - {str(e)}")
        
        # 压缩图片
        if compress_image(input_path, output_path, quality, max_width):
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
    print("提示: 备份文件已保存为 *.backup 扩展名")
    print("如需恢复,请删除压缩后的文件并重命名备份文件")


if __name__ == '__main__':
    main()
