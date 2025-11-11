#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式面板测试脚本
用于帮助诊断文档列表和函数列表功能问题
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path

class PanelTester:
    def __init__(self):
        """初始化测试器"""
        self.test_log = Path("panel_test_results.log")
        self.start_time = datetime.now()
        self.test_results = []
        
        # 创建日志文件头
        self._write_header()
    
    def _write_header(self):
        """写入日志文件头"""
        header = f"""
==========================================
面板功能测试日志
开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
程序: notepad_abc_new.exe
测试功能: 文档列表和函数列表
==========================================

测试记录:
"""
        with open(self.test_log, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def log_test_step(self, step_name, description, result, details=""):
        """记录测试步骤"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        test_entry = {
            'time': timestamp,
            'step': step_name,
            'description': description,
            'result': result,
            'details': details
        }
        
        self.test_results.append(test_entry)
        
        # 写入日志
        with open(self.test_log, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {step_name}: {description} (结果: {result})\n")
            if details:
                f.write(f"  详情: {details}\n")
        
        print(f"📝 [{timestamp}] {step_name}: {description} (结果: {result})")
        if details:
            print(f"   📋 详情: {details}")
    
    def test_document_list(self):
        """测试文档列表功能"""
        print("\n🧪 测试文档列表功能")
        print("-" * 30)
        
        # 步骤1: 检查程序是否运行
        exe_path = Path("notepad_abc_new.exe")
        if not exe_path.exists():
            self.log_test_step("程序检查", "检查可执行文件", "失败", "可执行文件不存在")
            return False
        
        self.log_test_step("程序检查", "检查可执行文件", "成功", "文件存在")
        
        # 步骤2: 用户操作指导
        print("💡 请执行以下操作:")
        print("  1. 启动程序: .\\notepad_abc_new.exe")
        print("  2. 点击菜单: 视图 -> 文档列表")
        print("  3. 观察左侧是否显示文档列表面板")
        
        # 步骤3: 获取用户反馈
        print("\n请回答以下问题:")
        
        # 问题1: 面板是否显示
        panel_visible = input("文档列表面板是否显示? (是/否): ").strip().lower()
        if panel_visible == "是":
            self.log_test_step("面板显示", "文档列表面板显示", "成功", "面板正常显示")
        else:
            # 问题2: 错误信息
            error_msg = input("请描述遇到的问题: ").strip()
            self.log_test_step("面板显示", "文档列表面板显示", "失败", f"面板未显示: {error_msg}")
        
        # 问题3: 面板功能
        if panel_visible == "是":
            functional = input("面板功能是否正常? (是/否): ").strip().lower()
            if functional == "是":
                self.log_test_step("功能测试", "文档列表功能", "成功", "功能正常")
            else:
                func_issue = input("请描述功能问题: ").strip()
                self.log_test_step("功能测试", "文档列表功能", "部分成功", f"功能问题: {func_issue}")
        
        return panel_visible == "是"
    
    def test_function_list(self):
        """测试函数列表功能"""
        print("\n🧪 测试函数列表功能")
        print("-" * 30)
        
        # 步骤1: 用户操作指导
        print("💡 请执行以下操作:")
        print("  1. 确保程序正在运行")
        print("  2. 点击菜单: 视图 -> 函数列表")
        print("  3. 观察是否显示函数列表面板")
        
        # 步骤2: 获取用户反馈
        print("\n请回答以下问题:")
        
        # 问题1: 面板是否显示
        panel_visible = input("函数列表面板是否显示? (是/否): ").strip().lower()
        if panel_visible == "是":
            self.log_test_step("面板显示", "函数列表面板显示", "成功", "面板正常显示")
        else:
            # 问题2: 错误信息
            error_msg = input("请描述遇到的问题: ").strip()
            self.log_test_step("面板显示", "函数列表面板显示", "失败", f"面板未显示: {error_msg}")
        
        # 问题3: 面板功能
        if panel_visible == "是":
            functional = input("面板功能是否正常? (是/否): ").strip().lower()
            if functional == "是":
                self.log_test_step("功能测试", "函数列表功能", "成功", "功能正常")
            else:
                func_issue = input("请描述功能问题: ").strip()
                self.log_test_step("功能测试", "函数列表功能", "部分成功", f"功能问题: {func_issue}")
        
        return panel_visible == "是"
    
    def generate_report(self):
        """生成测试报告"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # 统计结果
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r['result'] in ['成功', '部分成功']])
        failed_tests = len([r for r in self.test_results if r['result'] == '失败'])
        
        # 写入报告
        with open(self.test_log, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*50 + "\n")
            f.write("测试报告摘要\n")
            f.write("="*50 + "\n")
            f.write(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"持续时间: {int(duration.total_seconds())} 秒\n")
            f.write(f"总测试数: {total_tests}\n")
            f.write(f"成功/部分成功: {successful_tests}\n")
            f.write(f"失败: {failed_tests}\n")
            f.write(f"成功率: {successful_tests/total_tests*100:.1f}%\n")
            
            # 详细结果
            f.write("\n详细测试结果:\n")
            for result in self.test_results:
                f.write(f"  [{result['time']}] {result['step']}: {result['result']}\n")
        
        # 控制台输出
        print("\n📊 测试报告")
        print("=" * 40)
        print(f"总测试数: {total_tests}")
        print(f"成功/部分成功: {successful_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")
        
        # 诊断建议
        print("\n🔧 诊断建议:")
        if failed_tests > 0:
            print("  ❌ 检测到功能问题，建议:")
            print("    1. 检查资源文件是否正确编译")
            print("    2. 查看错误日志文件")
            print("    3. 验证对话框资源是否正确嵌入")
        else:
            print("  ✅ 所有功能测试通过")
        
        print(f"\n📁 详细日志: {self.test_log}")

def main():
    """主函数"""
    print("🧪 交互式面板功能测试")
    print("=" * 50)
    
    # 创建测试器
    tester = PanelTester()
    
    print("本测试将帮助诊断文档列表和函数列表功能问题")
    print("请按照提示操作并回答问题")
    
    # 测试文档列表功能
    doc_list_ok = tester.test_document_list()
    
    # 测试函数列表功能
    func_list_ok = tester.test_function_list()
    
    # 生成报告
    tester.generate_report()
    
    # 总结
    print("\n🎯 测试完成")
    if doc_list_ok and func_list_ok:
        print("✅ 所有面板功能正常")
    else:
        print("❌ 部分面板功能存在问题")
        print("💡 请查看详细日志获取诊断建议")

if __name__ == "__main__":
    main()