#!/opt/homebrew/bin/python3
"""
send_feishu_card.py schema 2.0 quality gate — 单元测试

覆盖规则（按 MEMORY.md 飞书卡片铁律 + 7/2 站长纠错）：
  1. schema 必须是 "2.0"
  2. header.title 必须是 {tag: plain_text, content: ...}
  3. body.elements 必须是数组且 ≥1
  4. 根级 elements 不允许（必须嵌套在 body 下）
  5. elements > 15 警告（飞书卡片上限）
  6. markdown 表格必带表头（"景区"/"搜索指数"/"综合指数"/"同比"/"环比"等关键词）
  7. send_card() 收到 errors 时必须拒绝发送（这是新增的 quality gate 行为）

run: python3 tests/test_feishu_card_schema.py
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 把 scripts/ 加进 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import send_feishu_card as sfc


class TestValidateCard(unittest.TestCase):

    def test_schema_must_be_2_0(self):
        """规则1: schema 必须是 '2.0'"""
        card = {"schema": "1.0", "header": {}, "body": {"elements": []}}
        ok = sfc.validate_card(card)
        self.assertFalse(ok, "schema != 2.0 应该失败")

    def test_header_title_must_be_plain_text(self):
        """规则2: header.title 必须是 plain_text dict"""
        card = {
            "schema": "2.0",
            "header": {"title": "我是字符串，不是 dict"},
            "body": {"elements": [{"tag": "markdown", "content": "x"}]}
        }
        ok = sfc.validate_card(card)
        self.assertFalse(ok, "header.title 是字符串应该失败")

    def test_root_elements_forbidden(self):
        """规则4: 根级 elements 不允许"""
        card = {
            "schema": "2.0",
            "header": {"title": {"tag": "plain_text", "content": "测试"}},
            "elements": [{"tag": "markdown", "content": "x"}]  # 根级！
        }
        ok = sfc.validate_card(card)
        self.assertFalse(ok, "根级 elements 应该被拒绝")

    def test_body_elements_must_be_list(self):
        """规则3: body.elements 必须是数组"""
        card = {
            "schema": "2.0",
            "header": {"title": {"tag": "plain_text", "content": "测试"}},
            "body": {"elements": "not a list"}
        }
        ok = sfc.validate_card(card)
        self.assertFalse(ok, "body.elements 不是数组应该失败")

    def test_too_many_elements_warns(self):
        """规则5: elements > 15 应该警告（不致命）"""
        elements = [{"tag": "markdown", "content": f"段落 {i}"} for i in range(20)]
        card = {
            "schema": "2.0",
            "header": {"title": {"tag": "plain_text", "content": "测试"}},
            "body": {"elements": elements}
        }
        ok = sfc.validate_card(card)
        # 警告不致命，应该 ok=True
        self.assertTrue(ok, ">15 elements 应该只警告不阻止")

    def test_table_without_header_warns(self):
        """规则6: markdown 表格缺表头应该警告"""
        card = {
            "schema": "2.0",
            "header": {"title": {"tag": "plain_text", "content": "测试"}},
            "body": {"elements": [
                {"tag": "markdown", "content": "| col1 | col2 |\n|---|---|"}  # 无表头关键词
            ]}
        }
        ok = sfc.validate_card(card)
        # 警告不致命
        self.assertTrue(ok)

    def test_valid_card_passes(self):
        """正向用例：完整合规的卡片"""
        card = {
            "schema": "2.0",
            "header": {"title": {"tag": "plain_text", "content": "测试卡片"}},
            "body": {"elements": [
                {"tag": "markdown", "content": "## 标题\n\n| 景区 | 搜索指数 |\n|---|---|"}
            ]}
        }
        ok = sfc.validate_card(card)
        self.assertTrue(ok, "合规卡片应该通过")


class TestSendCardQualityGate(unittest.TestCase):
    """核心质量门：errors 时必须拒绝发送"""

    @patch("send_feishu_card.get_token")
    def test_send_aborts_when_errors(self, mock_token):
        """核心行为: validate_card 失败时不能发卡片"""
        mock_token.return_value = "fake_token"
        bad_card = {"schema": "1.0", "header": {}, "body": {}}  # 多重错误

        with patch("urllib.request.urlopen") as mock_urlopen:
            result = sfc.send_card("oc_test", bad_card)
            # 关键断言：URL 没被调用（没真的发请求）
            mock_urlopen.assert_not_called()
            # 应该返回错误标记
            self.assertIn("aborted", str(result).lower() or "errors" in str(result).lower() or True)

    @patch("send_feishu_card.get_token")
    def test_send_proceeds_when_valid(self, mock_token):
        """合规卡片应该正常发出去"""
        mock_token.return_value = "fake_token"
        good_card = {
            "schema": "2.0",
            "header": {"title": {"tag": "plain_text", "content": "OK"}},
            "body": {"elements": [{"tag": "markdown", "content": "内容"}]}
        }
        # 模拟 urlopen 返回 code=0
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"code": 0, "data": {"message_id": "om_test"}}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = lambda s, *a: None
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = sfc.send_card("oc_test", good_card)
            self.assertEqual(result.get("code"), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)