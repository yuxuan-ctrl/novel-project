#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词质量验证脚本
自动检查和修复图像提示词的常见问题
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class PromptValidator:
    """提示词验证器"""

    # 风格锚定词库
    STYLE_KEYWORDS = [
        "仙侠动漫风格",
        "中国玄幻国风动漫风格",
        "色彩鲜明对比强烈",
        "流畅线条",
        "戏剧性",
        "悲壮感",
        "威严",
        "压迫感",
        "清幽",
        "仙家"
    ]

    # 质量约束词
    QUALITY_CONSTRAINTS = [
        "角色动作精准比例正常",
        "光影统一符合场景氛围",
        "画面干净不要文字水印logo",
        "不要畸形手指和多余肢体"
    ]

    # 角色映射表
    CHARACTER_MAP = {
        "林玄": "linxuan.png",
        "林渊": "linxuan.png",
        "慧觉": "huijue.png",
        "青袍修士": "huijue.png",
        "菩提祖师": "puti_zushi.png",
        "如来佛祖": "rulai_fozu.png",
        "孙悟空": "sun_wukong.png",
        "玉帝": "yudi.png",
        "观音菩萨": "guanyin_pusa.png"
    }

    # 场景映射表
    SCENE_MAP = {
        "斩仙台": "斩仙台.png",
        "方寸山": "方寸山.png",
        "天庭": "天庭.png",
        "徐府": "徐府.png",
        "云海": "云海.png",
        "仙山": "仙山.png"
    }

    def __init__(self, character_dir: str = "character_images", scene_dir: str = "scene_images"):
        """
        初始化验证器

        Args:
            character_dir: 角色图片目录
            scene_dir: 场景图片目录
        """
        self.character_dir = Path(character_dir)
        self.scene_dir = Path(scene_dir)
        self.results = []

    def validate_file(self, json_file: str) -> Dict:
        """
        验证整个JSON文件

        Args:
            json_file: JSON文件路径

        Returns:
            验证结果字典
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 兼容两种格式
        shots = data.get('shots', data) if isinstance(data, dict) else data

        print(f"开始验证 {len(shots)} 个镜头...")
        print("=" * 60)

        valid_count = 0
        needs_fix = 0
        auto_fixed = 0

        for shot in shots:
            result = self.validate_shot(shot)
            self.results.append(result)

            if result['is_valid']:
                valid_count += 1
            else:
                needs_fix += 1
                if result['auto_fixed']:
                    auto_fixed += 1

        # 生成汇总
        summary = {
            "total_shots": len(shots),
            "valid_shots": valid_count,
            "needs_fix": needs_fix,
            "auto_fixed": auto_fixed,
            "needs_manual": needs_fix - auto_fixed,
            "results": self.results
        }

        return summary

    def validate_shot(self, shot: Dict) -> Dict:
        """
        验证单个镜头

        Args:
            shot: 镜头数据字典

        Returns:
            验证结果字典
        """
        issues = []
        warnings = []
        auto_fixed = False

        prompt = shot.get('prompt', '')
        shot_number = shot.get('shot_number', '?')

        # 1. 检查六要素完整性
        element_issues = self._check_six_elements(prompt)
        issues.extend(element_issues)

        # 2. 检查角色绑定正确性
        binding_issues = self._check_character_binding(shot)
        issues.extend(binding_issues['issues'])
        if binding_issues['auto_fixed']:
            auto_fixed = True

        # 3. 检查参考图存在性
        ref_issues = self._check_reference_images(shot)
        issues.extend(ref_issues['issues'])
        if ref_issues['auto_fixed']:
            auto_fixed = True

        # 4. 检查风格锚定词
        style_issues = self._check_style_keywords(prompt)
        issues.extend(style_issues)
        if style_issues and self._can_auto_fix_style(prompt):
            warnings.append("Shot {}: 风格锚定词不足，建议补充".format(shot_number))

        # 5. 检查质量约束
        quality_issues = self._check_quality_constraints(prompt)
        issues.extend(quality_issues)
        if quality_issues and self._can_auto_fix_quality(prompt):
            warnings.append("Shot {}: 质量约束缺失，建议补充".format(shot_number))

        # 6. 检查长度
        length_issues = self._check_length(prompt)
        warnings.extend(length_issues)

        # 7. 检查格式
        format_issues = self._check_format(shot)
        issues.extend(format_issues)

        # 8. 检查错误比喻
        metaphor_issues = self._check_metaphors(prompt)
        issues.extend(metaphor_issues)

        # 尝试自动修复
        fixed_prompt = None
        if issues and self._can_auto_fix(shot, issues):
            fixed_prompt = self._fix_shot(shot, issues)
            auto_fixed = True

        return {
            "shot_number": shot_number,
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "auto_fixed": auto_fixed,
            "fixed_prompt": fixed_prompt
        }

    def _check_six_elements(self, prompt: str) -> List[str]:
        """检查六要素完整性"""
        issues = []

        # 检查场景描述（远景、中景、近景关键词）
        if not any(kw in prompt for kw in ['远景', '中景', '近景']):
            issues.append("缺少三层环境描述（远景/中景/近景）")

        # 检查角色描述
        if not any(kw in prompt for kw in ['服装', '衣着', '身穿', '身着']):
            issues.append("缺少角色服装描述")

        # 检查位置描述
        if not any(kw in prompt for kw in ['位于', '位于画面', '画面', '位置', '站位']):
            issues.append("缺少精确位置描述")

        # 检查光影描述
        if not any(kw in prompt for kw in ['光', '影', '照明', '光源']):
            issues.append("缺少光影描述")

        return issues

    def _check_character_binding(self, shot: Dict) -> Dict:
        """检查角色绑定正确性"""
        issues = []
        auto_fixed = False

        prompt = shot.get('prompt', '')
        characters = shot.get('characters', [])
        character_refs = shot.get('character_refs', [])

        # 检查是否以【图X参考开头
        if characters and not prompt.startswith('【图'):
            issues.append("缺少【图X参考角色】开头")
            # 可以自动修复
            auto_fixed = True

        # 检查角色数量与参考图数量是否匹配
        char_image_refs = [r for r in character_refs if any(
            char_img in r for char_img in self.CHARACTER_MAP.values()
        )]

        if len(characters) != len(char_image_refs):
            issues.append(f"角色数量({len(characters)})与角色参考图数量({len(char_image_refs)})不匹配")

        return {"issues": issues, "auto_fixed": auto_fixed}

    def _check_reference_images(self, shot: Dict) -> Dict:
        """检查参考图是否存在"""
        issues = []
        auto_fixed = False

        character_refs = shot.get('character_refs', [])
        valid_refs = []

        for ref in character_refs:
            # 检查角色图
            if ref in self.CHARACTER_MAP.values():
                ref_path = self.character_dir / ref
                if not ref_path.exists():
                    issues.append(f"角色参考图不存在: {ref}")
                else:
                    valid_refs.append(ref)
            # 检查场景图
            elif ref in self.SCENE_MAP.values():
                ref_path = self.scene_dir / ref
                if not ref_path.exists():
                    issues.append(f"场景参考图不存在: {ref}")
                else:
                    valid_refs.append(ref)

        if len(valid_refs) < len(character_refs):
            auto_fixed = True

        return {"issues": issues, "auto_fixed": auto_fixed}

    def _check_style_keywords(self, prompt: str) -> List[str]:
        """检查风格锚定词"""
        found = sum(1 for kw in self.STYLE_KEYWORDS if kw in prompt)
        if found < 3:
            return [f"风格锚定词不足（找到{found}个，需要至少3个）"]
        return []

    def _check_quality_constraints(self, prompt: str) -> List[str]:
        """检查质量约束"""
        missing = []
        for constraint in self.QUALITY_CONSTRAINTS:
            if constraint not in prompt:
                missing.append(constraint)
        if missing:
            return [f"缺少质量约束: {', '.join(missing)}"]
        return []

    def _check_length(self, prompt: str) -> List[str]:
        """检查提示词长度"""
        length = len(prompt)
        if length < 140:
            return [f"提示词过短（{length}字，建议140-260字）"]
        if length > 260:
            return [f"提示词过长（{length}字，建议140-260字）"]
        return []

    def _check_format(self, shot: Dict) -> List[str]:
        """检查格式正确性"""
        issues = []

        required_fields = ['shot_number', 'prompt', 'has_character', 'characters', 'character_refs']
        for field in required_fields:
            if field not in shot:
                issues.append(f"缺少必需字段: {field}")

        return issues

    def _check_metaphors(self, prompt: str) -> List[str]:
        """检查错误比喻"""
        issues = []

        # 检查"像X一样"模式
        pattern = r'像[^，。]{1,4}一样'
        matches = re.findall(pattern, prompt)
        if matches:
            for match in matches:
                # 排除安全词汇
                if match not in ['像松树一样', '像山峰一样', '像海洋一样']:
                    issues.append(f"包含可能引起误会的比喻: {match}")

        return issues

    def _can_auto_fix(self, shot: Dict, issues: List[str]) -> bool:
        """判断是否可以自动修复"""
        # 只有部分问题可以自动修复
        fixable_patterns = [
            '缺少质量约束',
            '风格锚定词不足'
        ]
        return any(any(p in issue for p in fixable_patterns) for issue in issues)

    def _can_auto_fix_style(self, prompt: str) -> bool:
        """判断风格词是否可以自动补充"""
        # 通常可以自动补充
        return True

    def _can_auto_fix_quality(self, prompt: str) -> bool:
        """判断质量约束是否可以自动补充"""
        # 通常可以自动补充
        return True

    def _fix_shot(self, shot: Dict, issues: List[str]) -> str:
        """自动修复提示词"""
        prompt = shot.get('prompt', '')

        # 补充质量约束
        if any('质量约束' in issue for issue in issues):
            prompt = self._add_quality_constraints(prompt)

        # 补充风格锚定词
        if any('风格锚定词' in issue for issue in issues):
            prompt = self._add_style_keywords(prompt)

        return prompt

    def _add_quality_constraints(self, prompt: str) -> str:
        """添加质量约束"""
        constraints = []
        for constraint in self.QUALITY_CONSTRAINTS:
            if constraint not in prompt:
                constraints.append(constraint)

        if constraints:
            # 在结尾添加
            if not prompt.endswith('。'):
                prompt += '，'
            else:
                prompt = prompt.rstrip('。') + '，'
            prompt += '，'.join(constraints) + '。'

        return prompt

    def _add_style_keywords(self, prompt: str) -> str:
        """添加风格锚定词"""
        # 检查已有的风格词
        found = [kw for kw in self.STYLE_KEYWORDS if kw in prompt]

        # 添加缺失的关键词
        missing = [kw for kw in self.STYLE_KEYWORDS[:5] if kw not in found]
        if missing and len(found) < 3:
            # 在适当位置添加（通常在镜头描述后）
            if '16:9' in prompt:
                insert_pos = prompt.find('16:9')
                prompt = prompt[:insert_pos] + '，'.join(missing[:3]) + '，' + prompt[insert_pos:]
            else:
                prompt += '，' + '，'.join(missing[:3])

        return prompt

    def generate_report(self, summary: Dict, output_file: str = None) -> str:
        """
        生成验证报告

        Args:
            summary: 验证汇总结果
            output_file: 输出文件路径（可选）

        Returns:
            报告内容
        """
        lines = []
        lines.append("# 提示词验证报告")
        lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("\n## 汇总统计")
        lines.append(f"- 总镜头数: {summary['total_shots']}")
        lines.append(f"- 验证通过: {summary['valid_shots']}")
        lines.append(f"- 需要修复: {summary['needs_fix']}")
        lines.append(f"- 可自动修复: {summary['auto_fixed']}")
        lines.append(f"- 需要人工处理: {summary['needs_manual']}")

        # 问题列表
        all_issues = []
        for result in summary['results']:
            all_issues.extend(result['issues'])

        if all_issues:
            lines.append("\n## 发现的问题")
            for i, result in enumerate(summary['results'], 1):
                if result['issues']:
                    lines.append(f"\n### 镜头 {result['shot_number']}")
                    for issue in result['issues']:
                        lines.append(f"- {issue}")

        # 警告列表
        all_warnings = []
        for result in summary['results']:
            all_warnings.extend(result['warnings'])

        if all_warnings:
            lines.append("\n## 警告")
            for warning in all_warnings:
                lines.append(f"- {warning}")

        # 建议
        lines.append("\n## 改进建议")
        if summary['needs_manual'] > 0:
            lines.append("- 有部分镜头需要人工修复，请仔细检查")
        if any('三层环境' in issue for issue in all_issues):
            lines.append("- 多个镜头缺少三层环境描述，建议补充远景/中景/近景")
        if any('位置' in issue for issue in all_issues):
            lines.append("- 多个镜头缺少精确位置描述，建议添加画面坐标")
        if any('服装' in issue for issue in all_issues):
            lines.append("- 多个镜头缺少详细服装描述，建议参考角色特征锁定表")

        report = '\n'.join(lines)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到: {output_file}")

        return report

    def save_fixed_prompts(self, summary: Dict, output_file: str):
        """
        保存修复后的提示词

        Args:
            summary: 验证汇总结果
            output_file: 输出文件路径
        """
        fixed_shots = []

        for result in summary['results']:
            if result['auto_fixed'] and result['fixed_prompt']:
                # 创建修复后的镜头
                fixed_shot = {
                    "shot_number": result['shot_number'],
                    "prompt": result['fixed_prompt'],
                    "is_auto_fixed": True
                }
                fixed_shots.append(fixed_shot)

        if fixed_shots:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(fixed_shots, f, ensure_ascii=False, indent=2)
            print(f"修复后的提示词已保存到: {output_file}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python prompt_validator.py <JSON文件> [--fix] [--output-dir <目录>]")
        print("\n选项:")
        print("  --fix          尝试自动修复问题")
        print("  --output-dir   指定输出目录")
        sys.exit(1)

    json_file = sys.argv[1]
    auto_fix = '--fix' in sys.argv

    # 获取输出目录
    output_dir = None
    if '--output-dir' in sys.argv:
        idx = sys.argv.index('--output-dir')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    # 创建验证器
    validator = PromptValidator()

    # 执行验证
    summary = validator.validate_file(json_file)

    # 打印汇总
    print("\n" + "=" * 60)
    print("验证完成！")
    print(f"总镜头数: {summary['total_shots']}")
    print(f"验证通过: {summary['valid_shots']}")
    print(f"需要修复: {summary['needs_fix']}")
    print(f"可自动修复: {summary['auto_fixed']}")
    print(f"需要人工处理: {summary['needs_manual']}")
    print("=" * 60)

    # 生成报告
    report_file = None
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        report_file = os.path.join(output_dir, 'validation_report.md')
    elif auto_fix:
        report_file = 'validation_report.md'

    if report_file:
        validator.generate_report(summary, report_file)

    # 保存修复后的提示词
    if auto_fix and summary['auto_fixed'] > 0:
        fixed_file = None
        if output_dir:
            fixed_file = os.path.join(output_dir, 'fixed_prompts.json')
        else:
            fixed_file = 'fixed_prompts.json'

        validator.save_fixed_prompts(summary, fixed_file)


if __name__ == "__main__":
    main()
