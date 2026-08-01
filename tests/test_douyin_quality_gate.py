#!/opt/homebrew/bin/python3
"""
douyin_index.py quality gate — 单元测试

覆盖规则：
  A. 数据完整性门：8 景区里至少 6 个 search>0，否则判定"采集失败"
  B. 数值合理性门：search/synth 必须在 0~1_000_000_000 之间，异常值标红
  C. 格式合法性门：每个 dict 必须含 name/search/synth 三个键

run: python3 tests/test_douyin_quality_gate.py
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import douyin_index as di


class TestParseSubscriptionText(unittest.TestCase):
    """测试核心解析函数 + quality gate"""

    def test_valid_block_parses_search_and_synth(self):
        """正向用例：完整合规的页面文本"""
        text = """
郑州电影小镇
电脑端订阅 站内信推送 异动阈值 20%
搜索指数 12345 日环比 +5%
综合指数 67890 日环比 -3%
"""
        result = di.parse_subscription_text(text)
        zzm = next(s for s in result if s["name"] == "郑州电影小镇")
        self.assertEqual(zzm["search"], 12345)
        self.assertEqual(zzm["synth"], 67890)
        self.assertEqual(zzm["search_trend"], "+5%")
        self.assertEqual(zzm["synth_trend"], "-3%")

    def test_commas_in_numbers_handled(self):
        """千分位逗号应被去除"""
        text = """
郑州电影小镇
搜索指数 1,234,567 日环比 +5%
综合指数 678,900 日环比 -3%
"""
        result = di.parse_subscription_text(text)
        zzm = next(s for s in result if s["name"] == "郑州电影小镇")
        self.assertEqual(zzm["search"], 1234567)
        self.assertEqual(zzm["synth"], 678900)

    def test_missing_spot_returns_zeros(self):
        """页面没有该景区 → 返回 0 字典（不 crash）"""
        text = "无关文本"
        result = di.parse_subscription_text(text)
        zzm = next(s for s in result if s["name"] == "郑州电影小镇")
        self.assertEqual(zzm["search"], 0)
        self.assertEqual(zzm["synth"], 0)


class TestQualityGateA_Completeness(unittest.TestCase):
    """A. 数据完整性门"""

    def test_gate_a_passes_when_six_or_more_valid(self):
        """≥6 个景区有数据 → 通过"""
        # 6 个有数（从 i=1 开始避开 0）
        spots = [{"name": f"景区{i}", "search": i*100, "synth": i*200, "search_trend": "", "synth_trend": "", "anomaly": False} for i in range(1, 7)]
        # 加 2 个 0
        spots += [{"name": "景区6", "search": 0, "synth": 0, "search_trend": "", "synth_trend": "", "anomaly": False}]
        spots += [{"name": "景区7", "search": 0, "synth": 0, "search_trend": "", "synth_trend": "", "anomaly": False}]
        ok, report = di.check_quality_gate(spots)
        self.assertTrue(ok, f"6/8 应该有数据，应该通过。报告: {report}")

    def test_gate_a_fails_when_less_than_six_valid(self):
        """<6 个景区有数据 → 失败"""
        spots = [{"name": f"景区{i}", "search": 0, "synth": 0, "search_trend": "", "synth_trend": "", "anomaly": False} for i in range(8)]
        # 只有 1 个有数
        spots[0]["search"] = 100
        ok, report = di.check_quality_gate(spots)
        self.assertFalse(ok)
        self.assertIn("完整性", report)


class TestQualityGateB_Range(unittest.TestCase):
    """B. 数值合理性门"""

    def test_gate_b_flags_over_range(self):
        """search > 1e9 应该被标红（但不算失败）"""
        spots = [{"name": "正常景区", "search": 1000, "synth": 2000, "search_trend": "", "synth_trend": "", "anomaly": False}]
        # 加一个超范围
        spots.append({"name": "异常景区", "search": 999999999999, "synth": 0, "search_trend": "", "synth_trend": "", "anomaly": False})
        ok, report = di.check_quality_gate(spots)
        self.assertIn("数值超范围", report)
        self.assertIn("异常景区", report)

    def test_gate_b_negative_values_flagged(self):
        """负数应该被标红（指数不可能为负）"""
        spots = [{"name": "负数景区", "search": -100, "synth": 0, "search_trend": "", "synth_trend": "", "anomaly": False}]
        ok, report = di.check_quality_gate(spots)
        self.assertIn("数值超范围", report)


class TestQualityGateC_Structure(unittest.TestCase):
    """C. 格式合法性门"""

    def test_gate_c_flags_missing_keys(self):
        """缺键的 dict 应该被丢弃"""
        spots = [
            {"name": "完整", "search": 100, "synth": 200, "search_trend": "", "synth_trend": "", "anomaly": False},
            {"name": "缺search", "synth": 200, "search_trend": "", "synth_trend": "", "anomaly": False},  # 缺 search
        ]
        ok, report = di.check_quality_gate(spots)
        self.assertIn("格式错误", report)
        self.assertIn("缺search", report)


class TestIntegration(unittest.TestCase):
    """集成：parse + check_quality_gate 串联"""

    def test_typical_douyin_page_passes_all_gates(self):
        """典型抖音页面应该过三道门"""
        text = """
郑州电影小镇
搜索指数 12345 日环比 +5%
综合指数 67890 日环比 -3%

万岁山武侠城
搜索指数 23000 日环比 +10%
综合指数 45000 日环比 +2%

清明上河园
搜索指数 56000 日环比 -1%
综合指数 89000 日环比 +5%

只有河南戏剧幻城
搜索指数 34000 日环比 +8%
综合指数 67000 日环比 +3%

郑州方特欢乐世界
搜索指数 28000 日环比 +2%
综合指数 52000 日环比 -1%

郑州海昌海洋公园
搜索指数 15000 日环比 +4%
综合指数 30000 日环比 +6%
"""
        spots = di.parse_subscription_text(text)
        ok, report = di.check_quality_gate(spots)
        # 6/8 有数据，应过完整性门
        self.assertTrue(ok, f"典型页面应通过。报告: {report}")


if __name__ == "__main__":
    unittest.main(verbosity=2)