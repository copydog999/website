import os
import sys
from pathlib import Path
import PyPDF2
from tqdm import tqdm


def update_pdf_title_to_filename(pdf_path):
    """
    将PDF文件的元数据标题修改为文件名（不含扩展名）

    Args:
        pdf_path: PDF文件的完整路径

    Returns:
        bool: 是否成功修改
    """
    try:
        # 获取文件名（不含扩展名）作为新标题
        file_name = Path(pdf_path).stem

        # 读取原PDF文件
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_writer = PyPDF2.PdfWriter()

            # 复制所有页面
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            # 获取原元数据（如果有的话）
            metadata = pdf_reader.metadata
            if metadata:
                # 创建新的元数据，只修改标题，保留其他信息
                new_metadata = {
                    '/Title': file_name,
                    '/Author': metadata.get('/Author', ''),
                    '/Subject': metadata.get('/Subject', ''),
                    '/Keywords': metadata.get('/Keywords', ''),
                    '/Creator': metadata.get('/Creator', ''),
                    '/Producer': metadata.get('/Producer', '')
                }
            else:
                # 如果没有原元数据，只设置标题
                new_metadata = {
                    '/Title': file_name
                }

            # 添加元数据
            pdf_writer.add_metadata(new_metadata)

            # 写入新文件（先写入临时文件，然后替换原文件）
            temp_path = pdf_path + '.temp'
            with open(temp_path, 'wb') as output_file:
                pdf_writer.write(output_file)

        # 用临时文件替换原文件
        os.replace(temp_path, pdf_path)
        return True

    except Exception as e:
        print(f"处理文件 {pdf_path} 时出错: {str(e)}")
        return False


def batch_update_pdf_titles(root_dir):
    """
    批量更新目录及其子目录下所有PDF文件的标题

    Args:
        root_dir: 根目录路径
    """
    # 转换为Path对象
    root_path = Path(root_dir)

    if not root_path.exists():
        print(f"错误：目录 {root_dir} 不存在")
        return

    # 收集所有PDF文件
    pdf_files = list(root_path.rglob("*.pdf"))

    if not pdf_files:
        print(f"在 {root_dir} 及其子目录中未找到PDF文件")
        return

    print(f"找到 {len(pdf_files)} 个PDF文件")
    print("开始处理...")

    # 统计处理结果
    success_count = 0
    fail_count = 0

    # 使用进度条显示处理进度
    for pdf_file in tqdm(pdf_files, desc="处理进度"):
        if update_pdf_title_to_filename(str(pdf_file)):
            success_count += 1
        else:
            fail_count += 1

    # 输出处理结果
    print(f"\n处理完成！")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {fail_count} 个文件")


def main():
    """
    主函数
    """
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 如果提供了命令行参数，使用第一个参数作为目标目录
        target_dir = sys.argv[1]
    else:
        # 否则使用当前目录
        target_dir = "../articles"

    # 询问用户确认
    print(f"将要处理目录及其子目录下的所有PDF文件: {os.path.abspath(target_dir)}")
    print("这个操作会将每个PDF文件的元数据标题修改为对应的文件名。")
    response = input("是否继续？(y/n): ")

    if response.lower() == 'y':
        batch_update_pdf_titles(target_dir)
    else:
        print("操作已取消")


if __name__ == "__main__":
    main()