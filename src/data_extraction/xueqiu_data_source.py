"""
雪球（Xueqiu）数据源

使用雪球免费 JSON API 获取股票财务数据。
需要有效的 xq_a_token Cookie 才能访问财务数据接口。
当 Cookie 不可用时，自动返回空数据（由上层 fallback 处理）。

API 端点（已验证）:
  利润表:  /v5/stock/finance/cn/income.json
  资产负债表: /v5/stock/finance/cn/balance.json
  现金流量表: /v5/stock/finance/cn/cash_flow.json  (注意下划线)
  公司简介:  /v5/stock/f10/cn/company.json

Cookie 文件: 项目根目录下 config/XueQiuCookie.txt
"""

import os
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any


def _default_cookie_path() -> str:
    """计算默认 Cookie 文件路径（基于项目根目录）"""
    # xueqiu_data_source.py 位于 src/data_extraction/，上两级为项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(project_root, "config", "XueQiuCookie.txt")


DEFAULT_COOKIE_PATH = _default_cookie_path()


def load_cookie_from_file(path: str = DEFAULT_COOKIE_PATH) -> str:
    """从文件加载雪球 Cookie"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            # 支持 "cookie=xxx" 和直接 "xxx" 两种格式
            if raw.startswith("cookie="):
                raw = raw[len("cookie="):]
            return raw
    except Exception as e:
        print(f"[Xueqiu] 读取Cookie文件失败: {e}")
        return ""


class XueqiuDataSource:
    """雪球数据源 — 优先使用归母净利润"""

    # ──────────────────────────────────────────────
    # 雪球字段名 → 项目内部字段名 映射
    # ──────────────────────────────────────────────

    # 利润表字段映射 —— 按会计准则报表顺序排列
    # 顺序：营业收入→成本费用→其他损益→营业利润→利润总额→所得税→净利润→综合收益→每股收益
    INCOME_FIELD_MAP = {
        # ── 营业收入 ──
        "total_revenue":      "营业总收入",
        "revenue":            "营业收入",
        # ── 营业成本与费用 ──
        "operating_costs":    "营业总成本",
        "operating_cost":     "营业成本",
        "operating_taxes_and_surcharge": "税金及附加",
        "sales_fee":          "销售费用",
        "manage_fee":         "管理费用",
        "rad_cost":           "研发费用",
        "financing_expenses": "财务费用",
        "finance_cost_interest_fee":    "利息支出",
        "finance_cost_interest_income":  "利息收入",
        # ── 其他损益 ──
        "other_income":       "其他收益",
        "invest_income":      "投资收益",
        "invest_incomes_from_rr":       "对联营企业和合营企业的投资收益",
        "income_from_chg_in_fv":        "公允价值变动收益",
        "asset_impairment_loss":        "资产减值损失",
        "credit_impairment_loss":       "信用减值损失",
        "asset_disposal_income":        "资产处置收益",
        "exchg_gain":         "汇兑收益",
        "noncurrent_assets_dispose_gain": "非流动资产处置利得",
        "noncurrent_asset_disposal_loss":"非流动资产处置损失",
        # ── 利润 ──
        "op":                 "营业利润",
        "non_operating_income":"营业外收入",
        "non_operating_payout":"营业外支出",
        "profit_total_amt":   "利润总额",
        "income_tax_expenses":"所得税费用",
        # ── 净利润 ──
        "net_profit":         "净利润",
        "net_profit_atsopc":  "归母净利润",
        "net_profit_after_nrgal_atsolc": "扣非归母净利润",
        "continous_operating_np":        "持续经营净利润",
        "minority_gal":       "少数股东损益",
        "net_profit_bi":      "归属于母公司股东的净利润(调整)",
        # ── 综合收益 ──
        "total_compre_income":           "综合收益总额",
        "total_compre_income_atsopc":    "归属于母公司股东的综合收益总额",
        "total_compre_income_atms":      "归属于少数股东的综合收益总额",
        "othr_compre_income":            "其他综合收益",
        "othr_compre_income_atoopc":     "归属于母公司股东的其他综合收益",
        "othr_compre_income_atms":       "归属于少数股东的其他综合收益",
        # ── 每股收益 ──
        "basic_eps":          "基本每股收益",
        "dlt_earnings_per_share": "稀释每股收益",
    }

    # 资产负债表字段映射 —— 按会计准则报表顺序排列
    # 顺序：流动资产→流动资产合计→非流动资产→非流动资产合计→资产总计
    #       →流动负债→流动负债合计→非流动负债→非流动负债合计→负债合计
    #       →所有者权益→所有者权益合计→负债和所有者权益总计
    BALANCE_FIELD_MAP = {
        # ════════════ 资产：流动 ════════════
        "currency_funds":        "货币资金",
        "tradable_fnncl_assets": "交易性金融资产",
        "bills_receivable":      "应收票据",
        "account_receivable":    "应收账款",
        "ar_and_br":             "应收票据及应收账款",
        "interest_receivable":   "应收利息",
        "dividend_receivable":   "应收股利",
        "pre_payment":           "预付款项",
        "pre_receivable":        "预收款项",
        "othr_receivables":      "其他应收款",
        "inventory":             "存货",
        "contractual_assets":    "合同资产",
        "to_sale_asset":         "持有待售资产",
        "nca_due_within_one_year": "一年内到期的非流动资产",
        "othr_current_assets":   "其他流动资产",
        "total_current_assets":  "流动资产合计",
        # ════════════ 资产：非流动 ════════════
        "salable_financial_assets": "可供出售金融资产",
        "saleable_finacial_assets":  "可供出售金融资产(别名)",
        "held_to_maturity_invest":  "持有至到期投资",
        "other_illiquid_fnncl_assets": "其他非流动金融资产",
        "lt_receivable":         "长期应收款",
        "lt_equity_invest":      "长期股权投资",
        "invest_property":       "投资性房地产",
        "fixed_asset":           "固定资产",
        "fixed_asset_sum":       "固定资产合计",
        "fixed_assets_disposal": "固定资产清理",
        "construction_in_process":        "在建工程",
        "construction_in_process_sum":    "在建工程合计",
        "productive_biological_assets":   "生产性生物资产",
        "oil_and_gas_asset":              "油气资产",
        "intangible_assets":     "无形资产",
        "dev_expenditure":       "开发支出",
        "goodwill":              "商誉",
        "lt_deferred_expense":   "长期待摊费用",
        "dt_assets":             "递延所得税资产",
        "othr_noncurrent_assets":"其他非流动资产",
        "total_noncurrent_assets": "非流动资产合计",
        # ── 资产总计 ──
        "total_assets":          "资产总计",
        # ════════════ 负债：流动 ════════════
        "st_loan":               "短期借款",
        "tradable_fnncl_liab":   "交易性金融负债",
        "bill_payable":          "应付票据",
        "accounts_payable":      "应付账款",
        "bp_and_ap":             "应付票据及应付账款",
        "prepayments":           "预收款项",
        "contract_liabilities":  "合同负债",
        "payroll_payable":       "应付职工薪酬",
        "tax_payable":           "应交税费",
        "interest_payable":      "应付利息",
        "dividend_payable":      "应付股利",
        "othr_payables":         "其他应付款",
        "to_sale_debt":          "持有待售负债",
        "noncurrent_liab_due_in1y": "一年内到期的非流动负债",
        "othr_current_liab":     "其他流动负债",
        "total_current_liab":    "流动负债合计",
        # ════════════ 负债：非流动 ════════════
        "lt_loan":               "长期借款",
        "bond_payable":          "应付债券",
        "perpetual_bond":        "永续债",
        "lt_payable":            "长期应付款",
        "lt_payable_sum":        "长期应付款合计",
        "estimated_liab":        "预计负债",
        "dt_liab":               "递延所得税负债",
        "othr_non_current_liab": "其他非流动负债",
        "total_noncurrent_liab": "非流动负债合计",
        # ── 负债总计 ──
        "total_liab":            "负债合计",
        # ════════════ 所有者权益 ════════════
        "shares":                "实收资本(股本)",
        "capital_reserve":       "资本公积",
        "treasury_stock":        "库存股",
        "othr_compre_income":    "其他综合收益",
        "special_reserve":       "专项储备",
        "surplus_reserve":       "盈余公积",
        "earned_surplus":        "盈余公积(别名)",
        "undstrbtd_profit":      "未分配利润",
        "total_quity_atsopc":    "归属于母公司股东的权益合计",
        "minority_equity":       "少数股东权益",
        "total_holders_equity":  "所有者权益合计",
        # ── 总计 ──
        "total_liab_and_holders_equity": "负债和所有者权益总计",
        "asset_liab_ratio":      "资产负债率",
        # ── 证券行业专用（放末尾）──
        "current_assets_si":     "流动资产(证券行业)",
        "noncurrent_assets_si":  "非流动资产(证券行业)",
        "current_liab_si":       "流动负债(证券行业)",
        "noncurrent_liab_di":    "非流动负债(证券行业)",
        "noncurrent_liab_si":    "非流动负债(证券行业2)",
        "general_risk_provision":"一般风险准备",
        "frgn_currency_convert_diff": "外币报表折算差额",
    }

    # 现金流量表字段映射 —— 按会计准则报表顺序排列
    # 顺序：经营活动流入→流出→净额→投资活动流入→流出→净额→筹资活动流入→流出→净额→汇率影响→净增加→期初→期末
    CASHFLOW_FIELD_MAP = {
        # ════════════ 经营活动 ════════════
        "cash_received_of_sales_service": "销售商品、提供劳务收到的现金",
        "refund_of_tax_and_levies":       "收到的税费返还",
        "cash_received_of_othr_oa":       "收到其他与经营活动有关的现金",
        "sub_total_of_ci_from_oa":        "经营活动现金流入小计",
        "goods_buy_and_service_cash_pay": "购买商品、接受劳务支付的现金",
        "cash_paid_to_employee_etc":      "支付给职工以及为职工支付的现金",
        "payments_of_all_taxes":          "支付的各项税费",
        "othrcash_paid_relating_to_oa":   "支付其他与经营活动有关的现金",
        "sub_total_of_cos_from_oa":       "经营活动现金流出小计",
        "ncf_from_oa":                    "经营活动产生的现金流量净额",
        # ════════════ 投资活动 ════════════
        "net_cash_of_disposal_assets":    "处置固定资产、无形资产和其他长期资产收回的现金净额",
        "cash_received_of_dspsl_invest":  "处置固定资产收回的现金净额",
        "net_cash_of_disposal_branch":    "处置子公司及其他营业单位收到的现金净额",
        "invest_income_cash_received":    "取得投资收益收到的现金",
        "cash_received_of_othr_ia":       "收到其他与投资活动有关的现金",
        "sub_total_of_ci_from_ia":        "投资活动现金流入小计",
        "cash_paid_for_assets":           "购建固定资产、无形资产和其他长期资产支付的现金",
        "invest_paid_cash":               "投资支付的现金",
        "othrcash_paid_relating_to_ia":   "支付其他与投资活动有关的现金",
        "sub_total_of_cos_from_ia":       "投资活动现金流出小计",
        "ncf_from_ia":                    "投资活动产生的现金流量净额",
        # ════════════ 筹资活动 ════════════
        "cash_received_of_absorb_invest": "吸收投资收到的现金",
        "cash_received_from_investor":    "吸收投资收到的现金(别名)",
        "cash_received_of_borrowing":     "取得借款收到的现金",
        "cash_received_from_bond_issue":  "发行债券收到的现金",
        "cash_received_of_othr_fa":       "收到其他与筹资活动有关的现金",
        "sub_total_of_ci_from_fa":        "筹资活动现金流入小计",
        "cash_pay_for_debt":              "偿还债务支付的现金",
        "cash_paid_of_distribution":      "分配股利、利润或偿付利息支付的现金",
        "cash_paid_to_minority_holder":   "向少数股东支付股利",
        "othrcash_paid_relating_to_fa":   "支付其他与筹资活动有关的现金",
        "sub_total_of_cos_from_fa":       "筹资活动现金流出小计",
        "ncf_from_fa":                    "筹资活动产生的现金流量净额",
        # ════════════ 现金净增加 ════════════
        "effect_of_exchange_chg_on_cce":  "汇率变动对现金及现金等价物的影响",
        "net_increase_in_cce":            "现金及现金等价物净增加额",
        "initial_balance_of_cce":         "期初现金及现金等价物余额",
        "final_balance_of_cce":           "期末现金及现金等价物余额",
        "net_cash_amt_from_branch":       "子公司吸收少数股东投资收到的现金",
    }

    def __init__(self, cookie: str = "", cookie_path: str = DEFAULT_COOKIE_PATH):
        """
        Args:
            cookie: 雪球 Cookie 字符串（需要包含 xq_a_token）。
                   优先级高于 cookie_path。
            cookie_path: Cookie 文件路径，当 cookie 为空时从此文件读取。
        """
        self._cookie = cookie or load_cookie_from_file(cookie_path)
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://xueqiu.com/",
            "Accept": "application/json",
        })
        if self._cookie:
            self._session.headers["Cookie"] = self._cookie

    # ──────────────────────────────────────────────
    # Protocol 接口实现
    # ──────────────────────────────────────────────

    def get_name(self) -> str:
        return "雪球(Xueqiu)"

    def is_available(self) -> bool:
        """检查雪球 API 是否可用（需要有有效的 Cookie）"""
        if not self._cookie:
            return False

        try:
            test_code = self._normalize_code("SH600519")
            resp = self._session.get(
                "https://stock.xueqiu.com/v5/stock/f10/cn/company.json",
                params={"symbol": test_code},
                timeout=5,
            )
            data = resp.json()
            error_code = data.get("error_code")
            if error_code == "400016":
                print(f"[Xueqiu] ⚠️ Cookie 已过期，请更新 config/XueQiuCookie.txt（打开 xueqiu.com → F12 Network → 复制 xq_a_token）")
                return False
            return "error_code" not in data or error_code == 0
        except Exception:
            return False

    def get_stock_financial_data(
        self, stock_code: str, start_year: str, end_year: str, period: str
    ) -> Dict[str, Any]:
        """
        获取股票财务数据

        Returns:
            标准化的财务数据 dict，失败返回空 dict
        """
        try:
            code = self._normalize_code(stock_code)
            print(f"\n[{self.get_name()}] 获取 {stock_code}({code}) 财务数据, "
                  f"年份: {start_year}-{end_year}, 周期: {period}")

            # 确定请求类型
            period_type_map = {
                "year": "Q4",       # 年度 → 年报
                "year_half": "Q2",   # 半年度 → 中报
                "Q1": "Q1",          # 一季度
                "Q3": "Q3",          # 三季度
                "quarter": "all",    # 全部季度
            }
            req_type = period_type_map.get(period, "Q4")

            # 获取三张报表
            income = self._get_income_statement(code, req_type)
            balance = self._get_balance_sheet(code, req_type)
            cashflow = self._get_cashflow(code, req_type)

            # 合并三张报表
            result = self._merge_statements(income, balance, cashflow)

            # 过滤年份范围
            filtered = self._filter_years(result, start_year, end_year)

            print(f"[{self.get_name()}] 成功获取 {len(filtered)} 年数据")
            return filtered

        except Exception as e:
            print(f"[{self.get_name()}] 获取财务数据失败: {e}")
            return {}

    def get_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            code = self._normalize_code(stock_code)
            resp = self._session.get(
                "https://stock.xueqiu.com/v5/stock/f10/cn/company.json",
                params={"symbol": code},
                timeout=10,
            )
            data = resp.json()
            if data.get("error_code", 0) != 0:
                return {}

            company = data.get("data", {}).get("company", {})
            # 行业从 affiliate_industry 获取
            industry_info = company.get("affiliate_industry", {})
            industry_name = industry_info.get("ind_name", "未知行业") if isinstance(industry_info, dict) else "未知行业"

            return {
                "code": stock_code,
                "name": company.get("org_short_name_cn",
                         company.get("org_name_cn", f"股票{stock_code}")),
                "industry": industry_name,
                "market": self._determine_market(stock_code),
                "area": company.get("provincial_name",
                         company.get("reg_address_cn", "未知")),
                "pe": 0,
                "pb": 0,
                "total_share": 0,
                "circulating_share": 0,
            }
        except Exception as e:
            print(f"[{self.get_name()}] 获取股票信息失败: {e}")
            return {}

    # ──────────────────────────────────────────────
    # 私有方法：API 请求
    # ──────────────────────────────────────────────

    def _get_income_statement(self, code: str, req_type: str) -> Dict:
        """获取利润表"""
        return self._fetch_finance_api(
            "income", code, req_type, self.INCOME_FIELD_MAP
        )

    def _get_balance_sheet(self, code: str, req_type: str) -> Dict:
        """获取资产负债表"""
        return self._fetch_finance_api(
            "balance", code, req_type, self.BALANCE_FIELD_MAP
        )

    def _get_cashflow(self, code: str, req_type: str) -> Dict:
        """获取现金流量表"""
        return self._fetch_finance_api(
            "cash_flow", code, req_type, self.CASHFLOW_FIELD_MAP  # 注意：cash_flow 带下划线
        )

    def _fetch_finance_api(
        self, api_type: str, code: str, req_type: str, field_map: Dict[str, str]
    ) -> Dict:
        """
        通用财务数据请求

        Args:
            api_type: 'income' | 'balance' | 'cash_flow'
            code: 标准化后的股票代码
            req_type: 'Q4' | 'Q1' | 'Q2' | 'Q3' | 'all'
            field_map: 字段名映射
        """
        api_names = {
            "income": "income",
            "balance": "balance",
            "cash_flow": "cash_flow",  # 雪球现金流量表端点是 cash_flow
        }
        url = f"https://stock.xueqiu.com/v5/stock/finance/cn/{api_names[api_type]}.json"

        params = {
            "symbol": code,
            "type": req_type,
            "is_detail": "true",
            "count": "10",
            "timestamp": str(int(time.time() * 1000)),
        }

        resp = self._session.get(url, params=params, timeout=15)
        data = resp.json()

        if "error_code" in data and data.get("error_code") != 0:
            print(f"[{self.get_name()}] API错误: {data.get('error_description', '未知')}")
            return {}

        return self._parse_finance_list(data.get("data", {}), field_map)

    def _parse_finance_list(
        self, data: Dict, field_map: Dict[str, str]
    ) -> Dict[str, Dict]:
        """
        解析雪球返回的 list[] → {year: {字段: [值, 增长率]}}

        雪球返回格式:
        {
            "list": [
                {
                    "report_date": 1703952000000,   ← 毫秒时间戳
                    "report_name": "2023年报",
                    "total_revenue": [172054171890.91, -0.012],  ← [数值, 增长率]
                    "net_profit_atsopc": [82320067101.68, -0.045],
                    ...
                },
                ...
            ]
        }

        解析后:
        {
            "2024": {
                "营业收入": [172054171890.91, -0.012],   ← [数值, 增长率]
                "净利润":   [82320067101.68, -0.045],
                ...
            }
        }

        注意：增长率是雪球直接返回的同比数据，只有多期数据时才有意义。
        当只有一期数据时，增长率字段为 0，展示层应隐藏同比列。
        """
        result = {}
        items = data.get("list", [])

        for item in items:
            # report_date 是毫秒时间戳
            report_date_raw = item.get("report_date")
            if report_date_raw is None:
                continue

            # 毫秒时间戳 → 年份字符串
            try:
                year = datetime.fromtimestamp(report_date_raw / 1000).strftime("%Y")
            except (OSError, ValueError, TypeError):
                continue

            year_data = {}
            for src_field, dst_field in field_map.items():
                field_val = item.get(src_field)
                if field_val is None:
                    continue

                # 雪球字段值格式: [数值, 增长率] 或直接是数值
                if isinstance(field_val, (list, tuple)) and len(field_val) > 0:
                    val = self._safe_float(field_val[0])
                    # 增长率：field_val[1]，可能是 None
                    yoy = self._safe_float(field_val[1]) if len(field_val) > 1 and field_val[1] is not None else None
                elif isinstance(field_val, dict):
                    val = self._safe_float(field_val.get("value", 0))
                    yoy = None
                else:
                    val = self._safe_float(field_val)
                    yoy = None

                year_data[dst_field] = [val, yoy]

            # 特殊处理：如果归母净利润为0但有净利润，用净利润兜底
            if "归母净利润" in year_data and year_data["归母净利润"][0] == 0:
                if "净利润" in year_data and year_data["净利润"][0] != 0:
                    year_data["归母净利润"] = year_data["净利润"]

            if year_data:
                result[year] = year_data

        return result

    # ──────────────────────────────────────────────
    # 私有方法：数据合并与标准化
    # ──────────────────────────────────────────────

    def _merge_statements(
        self, income: Dict, balance: Dict, cashflow: Dict
    ) -> Dict[str, Dict]:
        """
        将三张报表合并为统一结构:

        {
            "2024": {
                "income_statement": {"营业收入": [val], "净利润": [val], ...},
                "balance_sheet": {"总资产": [val], ...},
                "cash_flow": {"经营活动现金流": [val], ...}
            }
        }
        """
        all_years = set(income.keys()) | set(balance.keys()) | set(cashflow.keys())
        result = {}

        for year in sorted(all_years):
            result[year] = {
                "income_statement": income.get(year, {}),
                "balance_sheet": balance.get(year, {}),
                "cash_flow": cashflow.get(year, {}),
            }

        return result

    def _filter_years(
        self, data: Dict, start_year: str, end_year: str
    ) -> Dict[str, Dict]:
        """过滤指定年份范围"""
        try:
            start_y = int(start_year)
            end_y = int(end_year)
        except (ValueError, TypeError):
            return data

        filtered = {}
        for year, year_data in data.items():
            try:
                y = int(year)
                if start_y <= y <= end_y:
                    filtered[year] = year_data
            except (ValueError, TypeError):
                continue

        return filtered

    # ──────────────────────────────────────────────
    # 工具方法
    # ──────────────────────────────────────────────

    def _normalize_code(self, stock_code: str) -> str:
        """
        将股票代码标准化为雪球格式 (SH600519, SZ000858)

        支持输入格式:
            - SH600519 → SH600519
            - 600519   → SH600519
            - 000858   → SZ000858
            - 300059   → SZ300059
        """
        code = stock_code.strip().upper()
        if code.startswith("SH") or code.startswith("SZ"):
            return code

        # 纯数字 → 加前缀
        if code.startswith("6"):
            return f"SH{code}"
        elif code.startswith(("0", "3")):
            return f"SZ{code}"
        elif code.startswith(("4", "8")):
            return f"BJ{code}"
        else:
            return f"SH{code}"  # 默认沪市

    @staticmethod
    def _safe_float(value) -> float:
        """安全转换为浮点数"""
        if value is None:
            return 0.0
        try:
            result = float(value)
            if result != result:  # NaN check
                return 0.0
            return result
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def _determine_market(stock_code: str) -> str:
        """根据股票代码判断市场"""
        code = stock_code.lstrip("SHZJB")
        if code.startswith("6"):
            return "沪市A股"
        elif code.startswith(("0", "3")):
            return "深市A股"
        elif code.startswith(("4", "8")):
            return "北交所"
        else:
            return "未知市场"
