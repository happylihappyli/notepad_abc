#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细鼠标操作记录器
专门用于记录文档列表和函数列表功能问题的详细操作日志
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path

class DetailedMouseLogger:
    def __init__(self):
        """初始化详细记录器"""
        self.log_file = Path("detailed_mouse_operations.log")
        self.operations = []
        self.start_time = datetime.now()
        
        # 创建详细日志文件
        self._create_detailed_log()
    
    def _create_detailed_log(self):
        """创建详细日志文件"""
        header = f"""
==================================================
详细鼠标操作记录 - 文档列表/函数列表问题诊断
开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
程序: notepad_abc_new.exe
问题描述: 点击菜单后无任何显示
==================================================

用户报告的问题:
- 点击菜单"视图"->"文档列表"无任何显示
- 点击菜单"视图"->"函数列表"无任何显示

操作记录:
"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def log_program_start(self):
        """记录程序启动"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        operation = {
            'time': timestamp,
            'type': 'program_start',
            'description': '用户启动notepad_abc_new.exe程序',
            'details': {
                'exe_path': 'notepad_abc_new.exe',
                'working_dir': str(Path.cwd())
            }
        }
        self._log_operation(operation)
        print(f"🚀 [{timestamp}] 程序启动")
    
    def log_menu_operation(self, menu_path, expected_result, actual_result):
        """记录菜单操作"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        operation = {
            'time': timestamp,
            'type': 'menu_operation',
            'description': f'点击菜单: {menu_path}',
            'details': {
                'menu_path': menu_path,
                'expected_result': expected_result,
                'actual_result': actual_result,
                'issue': '无任何显示' if actual_result == '无响应' else '其他问题'
            }
        }
        self._log_operation(operation)
        
        status_icon = "❌" if actual_result == "无响应" else "⚠️"
        print(f"{status_icon} [{timestamp}] 菜单: {menu_path}")
        print(f"   期望: {expected_result}")
        print(f"   实际: {actual_result}")
    
    def log_visual_observation(self, observation_type, description, details):
        """记录视觉观察"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        operation = {
            'time': timestamp,
            'type': 'visual_observation',
            'description': f'视觉观察: {observation_type}',
            'details': {
                'observation_type': observation_type,
                'description': description,
                'details': details
            }
        }
        self._log_operation(operation)
        print(f"👁️  [{timestamp}] {observation_type}: {description}")
    
    def log_error_observation(self, error_type, description, context):
        """记录错误观察"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        operation = {
            'time': timestamp,
            'type': 'error_observation',
            'description': f'错误观察: {error_type}',
            'details': {
                'error_type': error_type,
                'description': description,
                'context': context
            }
        }
        self._log_operation(operation)
        print(f"❌ [{timestamp}] 错误: {error_type}")
        print(f"   描述: {description}")
    
    def _log_operation(self, operation):
        """记录操作到日志文件"""
        self.operations.append(operation)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{operation['time']}] {operation['description']}\n")
            if 'details' in operation:
                for key, value in operation['details'].items():
                    f.write(f"  {key}: {value}\n")
    
    def generate_diagnostic_report(self):
        """生成诊断报告"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # 分析问题
        menu_operations = [op for op in self.operations if op['type'] == 'menu_operation']
        failed_operations = [op for op in menu_operations if op['details']['actual_result'] == '无响应']
        
        # 生成报告
        report = {
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': int(duration.total_seconds()),
            'total_operations': len(self.operations),
            'menu_operations': len(menu_operations),
            'failed_operations': len(failed_operations),
            'failure_rate': len(failed_operations) / len(menu_operations) * 100 if menu_operations else 0,
            'problem_summary': '文档列表和函数列表功能完全失效',
            'suspected_causes': [
                '资源文件未正确编译',
                '对话框资源未嵌入可执行文件',
                '面板创建函数存在问题',
                'COM组件初始化失败'
            ]
        }
        
        # 写入报告
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*60 + "\n")
            f.write("诊断报告\n")
            f.write("="*60 + "\n")
            f.write(f"问题总结: {report['problem_summary']}\n")
            f.write(f"测试时长: {report['duration_seconds']} 秒\n")
            f.write(f"菜单操作次数: {report['menu_operations']}\n")
            f.write(f"失败操作次数: {report['failed_operations']}\n")
            f.write(f"失败率: {report['failure_rate']:.1f}%\n")
            
            f.write("\n疑似原因:\n")
            for cause in report['suspected_causes']:
                f.write(f"  - {cause}\n")
            
            f.write("\n修复建议:\n")
            f.write("  1. 检查资源文件编译状态\n")
            f.write("  2. 验证对话框资源是否正确嵌入\n")
            f.write("  3. 检查面板创建相关代码\n")
            f.write("  4. 查看错误日志获取详细信息\n")
        
        return report

def interactive_detailed_logging():
    """交互式详细记录"""
    print("🐭 详细鼠标操作记录器")
    print("=" * 50)
    print("专门用于诊断文档列表和函数列表功能问题")
    print("")
    
    # 创建记录器
    logger = DetailedMouseLogger()
    
    print("📝 开始记录您的操作...")
    print("请按照以下步骤操作，我会详细记录每个步骤")
    print("")
    
    # 步骤1: 程序启动
    input("1. 请先启动 notepad_abc_new.exe，然后按 Enter 继续...")
    logger.log_program_start()
    
    # 步骤2: 测试文档列表
    print("\n2. 现在测试文档列表功能:")
    print("   - 点击菜单: 视图 -> 文档列表")
    print("   - 观察左侧是否显示面板")
    
    input("操作完成后按 Enter 记录结果...")
    
    doc_list_visible = input("文档列表面板是否显示? (是/否): ").strip().lower()
    actual_result = "显示成功" if doc_list_visible == "是" else "无响应"
    
    logger.log_menu_operation(
        "视图 -> 文档列表",
        "左侧显示文档列表面板",
        actual_result
    )
    
    if doc_list_visible == "否":
        visual_details = input("请描述您看到的情况 (如: 无任何变化/闪退/错误提示): ").strip()
        logger.log_visual_observation("文档列表测试", "面板未显示", visual_details)
    
    # 步骤3: 测试函数列表
    print("\n3. 现在测试函数列表功能:")
    print("   - 点击菜单: 视图 -> 函数列表")
    print("   - 观察是否显示函数列表面板")
    
    input("操作完成后按 Enter 记录结果...")
    
    func_list_visible = input("函数列表面板是否显示? (是/否): ").strip().lower()
    actual_result = "显示成功" if func_list_visible == "是" else "无响应"
    
    logger.log_menu_operation(
        "视图 -> 函数列表",
        "显示函数列表面板",
        actual_result
    )
    
    if func_list_visible == "否":
        visual_details = input("请描述您看到的情况: ").strip()
        logger.log_visual_observation("函数列表测试", "面板未显示", visual_details)
    
    # 步骤4: 其他观察
    print("\n4. 其他观察:")
    has_errors = input("程序运行过程中是否有错误提示或异常? (是/否): ").strip().lower()
    
    if has_errors == "是":
        error_details = input("请描述错误信息: ").strip()
        logger.log_error_observation("运行时错误", error_details, "菜单操作后")
    
    # 生成诊断报告
    print("\n📊 生成详细诊断报告...")
    report = logger.generate_diagnostic_report()
    
    print("\n" + "="*60)
    print("诊断报告摘要")
    print("="*60)
    print(f"问题总结: {report['problem_summary']}")
    print(f"测试时长: {report['duration_seconds']} 秒")
    print(f"菜单操作次数: {report['menu_operations']}")
    print(f"失败操作次数: {report['failed_operations']}")
    print(f"失败率: {report['failure_rate']:.1f}%")
    
    print("\n🔧 修复建议:")
    print("  1. 检查资源文件编译状态")
    print("  2. 验证对话框资源是否正确嵌入")
    print("  3. 检查面板创建相关代码")
    print("  4. 查看错误日志获取详细信息")
    
    print(f"\n📁 详细日志文件: {logger.log_file}")
    print("✅ 记录完成")

if __name__ == "__main__":
    interactive_detailed_logging()