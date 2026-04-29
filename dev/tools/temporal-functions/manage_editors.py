#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编辑部成员数据管理脚本
提供对 nowledge.json 的增删改查功能
"""

import json
import os
import sys
from pathlib import Path


class EditorManager:
    """编辑部成员数据管理器"""
    
    def __init__(self, json_file=None):
        """初始化
        
        Args:
            json_file: JSON 文件路径，默认为 database/nowledge.json
        """
        if json_file is None:
            # 获取脚本所在目录的父目录
            script_dir = Path(__file__).parent
            json_file = script_dir.parent / "database" / "data" / "nowledge.json"
        
        self.json_file = Path(json_file)
        self.data = self._load_data()
    
    def _load_data(self):
        """加载 JSON 数据"""
        if not self.json_file.exists():
            print(f"警告: 文件 {self.json_file} 不存在，将创建新文件")
            return []
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"错误: JSON 格式错误 - {e}")
            return []
    
    def _save_data(self):
        """保存数据到 JSON 文件"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✓ 数据已保存到 {self.json_file}")
        except Exception as e:
            print(f"错误: 保存失败 - {e}")
    
    def list_all(self):
        """列出所有成员"""
        if not self.data:
            print("暂无成员数据")
            return
        
        print(f"\n{'='*60}")
        print(f"编辑部成员列表 (共 {len(self.data)} 人)")
        print(f"{'='*60}\n")
        
        for member in self.data:
            print(f"ID: {member['id']}")
            print(f"姓名: {member['name']}")
            print(f"职位: {member['position']}")
            print(f"机构: {member['institution']}")
            print(f"h-index: {member.get('h-index', 'N/A')}")
            print(f"论文数: {len(member.get('papers', []))}")
            print("-" * 60)
    
    def get_by_id(self, member_id):
        """根据 ID 查询成员
        
        Args:
            member_id: 成员 ID
            
        Returns:
            dict: 成员信息，未找到返回 None
        """
        for member in self.data:
            if member['id'] == member_id:
                return member
        return None
    
    def display_member(self, member):
        """显示成员详细信息
        
        Args:
            member: 成员字典
        """
        if not member:
            print("未找到该成员")
            return
        
        print(f"\n{'='*60}")
        print(f"成员详细信息")
        print(f"{'='*60}\n")
        print(f"ID: {member['id']}")
        print(f"姓名: {member['name']}")
        print(f"职位: {member['position']}")
        print(f"机构: {member['institution']}")
        print(f"头衔: {member.get('title', 'N/A')}")
        print(f"h-index: {member.get('h-index', 'N/A')}")
        print(f"\n研究方向:")
        for field in member.get('resfield', []):
            print(f"  - {field}")
        
        print(f"\n个人简介:")
        print(f"  {member.get('bio', 'N/A')}")
        
        papers = member.get('papers', [])
        print(f"\n学术论文 (共 {len(papers)} 篇):")
        for i, paper in enumerate(papers, 1):
            venue = paper.get('journal') or paper.get('conference', 'N/A')
            venue_type = "期刊" if paper.get('journal') else "会议"
            print(f"  {i}. {paper['title']}")
            print(f"     {venue_type}: {venue}, {paper.get('year', 'N/A')}")
            print(f"     DOI: {paper.get('doi', 'N/A')}")
        
        print(f"\n头像: {member.get('avatar_url', 'N/A')}")
        print(f"背景: {member.get('backgound_url', member.get('background_url', 'N/A'))}")
        print(f"{'='*60}\n")
    
    def add_member(self, member_data):
        """添加新成员
        
        Args:
            member_data: 成员数据字典
        """
        # 检查 ID 是否已存在
        if any(m['id'] == member_data['id'] for m in self.data):
            print(f"错误: ID {member_data['id']} 已存在")
            return False
        
        self.data.append(member_data)
        self._save_data()
        print(f"✓ 成功添加成员: {member_data['name']} (ID: {member_data['id']})")
        return True
    
    def update_member(self, member_id, updates):
        """更新成员信息
        
        Args:
            member_id: 成员 ID
            updates: 要更新的字段字典
            
        Returns:
            bool: 是否更新成功
        """
        member = self.get_by_id(member_id)
        if not member:
            print(f"错误: 未找到 ID 为 {member_id} 的成员")
            return False
        
        # 更新字段
        for key, value in updates.items():
            member[key] = value
        
        self._save_data()
        print(f"✓ 成功更新成员: {member['name']} (ID: {member_id})")
        return True
    
    def delete_member(self, member_id):
        """删除成员
        
        Args:
            member_id: 成员 ID
            
        Returns:
            bool: 是否删除成功
        """
        member = self.get_by_id(member_id)
        if not member:
            print(f"错误: 未找到 ID 为 {member_id} 的成员")
            return False
        
        confirm = input(f"确认删除成员 '{member['name']}' (ID: {member_id})? (y/n): ")
        if confirm.lower() != 'y':
            print("取消删除")
            return False
        
        self.data = [m for m in self.data if m['id'] != member_id]
        self._save_data()
        print(f"✓ 成功删除成员: {member['name']} (ID: {member_id})")
        return True
    
    def search_by_name(self, keyword):
        """按姓名搜索成员
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 匹配的成员列表
        """
        results = [m for m in self.data if keyword.lower() in m['name'].lower()]
        return results
    
    def add_paper(self, member_id, paper_data):
        """为成员添加论文
        
        Args:
            member_id: 成员 ID
            paper_data: 论文数据字典，包含 title, year, doi, journal/conference
            
        Returns:
            bool: 是否添加成功
        """
        member = self.get_by_id(member_id)
        if not member:
            print(f"错误: 未找到 ID 为 {member_id} 的成员")
            return False
        
        if 'papers' not in member:
            member['papers'] = []
        
        member['papers'].append(paper_data)
        self._save_data()
        print(f"✓ 成功为 {member['name']} 添加论文: {paper_data['title']}")
        return True


def create_sample_member(member_id):
    """创建示例成员数据模板
    
    Args:
        member_id: 成员 ID
        
    Returns:
        dict: 示例成员数据
    """
    return {
        "id": member_id,
        "name": "姓名",
        "position": "职位",
        "institution": "所属机构",
        "title": "学术头衔",
        "resfield": ["研究方向1", "研究方向2"],
        "bio": "个人简介",
        "papers": [],
        "avatar_url": "头像URL",
        "backgound_url": "背景图片URL",
        "h-index": 0
    }


def print_help():
    """打印帮助信息"""
    help_text = """
╔═══════════════════════════════════════════════════════════╗
║           编辑部成员数据管理工具                           ║
╚═══════════════════════════════════════════════════════════╝

用法: python manage_editors.py <命令> [参数]

命令:
  list                          列出所有成员
  get <id>                      查看指定成员详情
  search <关键词>                按姓名搜索成员
  add                           添加新成员（交互式）
  update <id>                   更新成员信息（交互式）
  delete <id>                   删除成员
  add-paper <id>                为成员添加论文（交互式）
  help                          显示此帮助信息

示例:
  python manage_editors.py list
  python manage_editors.py get 1
  python manage_editors.py search copycat
  python manage_editors.py add
  python manage_editors.py update 1
  python manage_editors.py delete 1
  python manage_editors.py add-paper 1
"""
    print(help_text)


def interactive_add(manager):
    """交互式添加成员"""
    print("\n=== 添加新成员 ===\n")
    
    # 获取最大 ID
    max_id = max([m['id'] for m in manager.data], default=0)
    new_id = max_id + 1
    
    member = create_sample_member(new_id)
    
    print(f"ID (自动分配): {new_id}")
    member['name'] = input("姓名: ")
    member['position'] = input("职位: ")
    member['institution'] = input("所属机构: ")
    member['title'] = input("学术头衔: ")
    
    print("研究方向 (多个用逗号分隔):")
    fields = input("> ").split(',')
    member['resfield'] = [f.strip() for f in fields if f.strip()]
    
    member['bio'] = input("个人简介: ")
    member['avatar_url'] = input("头像 URL: ")
    member['backgound_url'] = input("背景图片 URL (可选): ")
    
    h_index = input("h-index (默认 0): ")
    member['h-index'] = int(h_index) if h_index else 0
    
    if manager.add_member(member):
        print("\n提示: 可以使用 'add-paper' 命令为该成员添加论文")


def interactive_update(manager, member_id):
    """交互式更新成员"""
    member = manager.get_by_id(member_id)
    if not member:
        print(f"错误: 未找到 ID 为 {member_id} 的成员")
        return
    
    print(f"\n=== 更新成员: {member['name']} ===\n")
    print("留空则保持原值\n")
    
    updates = {}
    
    position = input(f"职位 [{member['position']}]: ")
    if position:
        updates['position'] = position
    
    institution = input(f"所属机构 [{member['institution']}]: ")
    if institution:
        updates['institution'] = institution
    
    title = input(f"学术头衔 [{member.get('title', 'N/A')}]: ")
    if title:
        updates['title'] = title
    
    bio = input(f"个人简介 [{member.get('bio', 'N/A')[:50]}...]: ")
    if bio:
        updates['bio'] = bio
    
    avatar = input(f"头像 URL [{member.get('avatar_url', 'N/A')}]: ")
    if avatar:
        updates['avatar_url'] = avatar
    
    background = input(f"背景 URL [{member.get('backgound_url', 'N/A')}]: ")
    if background:
        updates['backgound_url'] = background
    
    h_index = input(f"h-index [{member.get('h-index', 'N/A')}]: ")
    if h_index:
        updates['h-index'] = int(h_index)
    
    if updates:
        manager.update_member(member_id, updates)
    else:
        print("未进行任何修改")


def interactive_add_paper(manager, member_id):
    """交互式添加论文"""
    member = manager.get_by_id(member_id)
    if not member:
        print(f"错误: 未找到 ID 为 {member_id} 的成员")
        return
    
    print(f"\n=== 为 {member['name']} 添加论文 ===\n")
    
    paper = {}
    paper['title'] = input("论文标题: ")
    
    venue_type = input("类型 (journal/conference): ").lower()
    if venue_type == 'journal':
        paper['journal'] = input("期刊名称: ")
    elif venue_type == 'conference':
        paper['conference'] = input("会议名称: ")
    else:
        print("无效的类型，使用 conference")
        paper['conference'] = input("会议名称: ")
    
    year = input("年份: ")
    paper['year'] = int(year) if year else 2024
    
    paper['doi'] = input("DOI (可选): ")
    
    if manager.add_paper(member_id, paper):
        print("提示: 可以继续添加更多论文")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    manager = EditorManager()
    
    if command == 'list':
        manager.list_all()
    
    elif command == 'get':
        if len(sys.argv) < 3:
            print("用法: python manage_editors.py get <id>")
            return
        member_id = int(sys.argv[2])
        member = manager.get_by_id(member_id)
        manager.display_member(member)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("用法: python manage_editors.py search <关键词>")
            return
        keyword = sys.argv[2]
        results = manager.search_by_name(keyword)
        if results:
            print(f"\n找到 {len(results)} 个结果:\n")
            for member in results:
                print(f"ID: {member['id']}, 姓名: {member['name']}, 职位: {member['position']}")
        else:
            print(f"未找到包含 '{keyword}' 的成员")
    
    elif command == 'add':
        interactive_add(manager)
    
    elif command == 'update':
        if len(sys.argv) < 3:
            print("用法: python manage_editors.py update <id>")
            return
        member_id = int(sys.argv[2])
        interactive_update(manager, member_id)
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("用法: python manage_editors.py delete <id>")
            return
        member_id = int(sys.argv[2])
        manager.delete_member(member_id)
    
    elif command == 'add-paper':
        if len(sys.argv) < 3:
            print("用法: python manage_editors.py add-paper <id>")
            return
        member_id = int(sys.argv[2])
        interactive_add_paper(manager, member_id)
    
    elif command == 'help':
        print_help()
    
    else:
        print(f"未知命令: {command}")
        print_help()


if __name__ == '__main__':
    main()
