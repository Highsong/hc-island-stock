import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# 检查AKShare是否可用
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    ak = None
    AKSHARE_AVAILABLE = False


class StockDataSource:
    """股票数据源类 - 优先使用新浪接口（AKShare）"""

    def __init__(self):
        self._debug_mode = True

    def get_name(self) -> str:
        return "AKShare(新浪/东方财富)"

    def is_available(self) -> bool:
        return AKSHARE_AVAILABLE

    def _log_akshare_error(self, api_name: str, stock_code: str, error: Exception, message: str,
                          response_data: Optional[str] = None, request_params: Optional[Dict] = None):
        """记录AKShare错误日志"""
        if not self._debug_mode:
            return

        error_info = {
            "timestamp": datetime.now().isoformat(),
            "api_name": api_name,
            "stock_code": stock_code,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_repr": repr(error),
            "message": message,
            "akshare_version": getattr(ak, '__version__', 'Unknown') if ak else 'Not Available',
            "python_version": __import__('sys').version,
            "platform": __import__('platform').platform(),
            "request_params": request_params,
            "response_data": response_data
        }

        print(f"\n{'='*80}")
        print(f"AKSHARE接口错误详情:")
        print(f"时间: {error_info['timestamp']}")
        print(f"API: {error_info['api_name']}")
        print(f"股票代码: {error_info['stock_code']}")
        print(f"错误类型: {error_info['error_type']}")
        print(f"错误信息: {error_info['error_message']}")
        print(f"错误repr: {error_info['error_repr']}")
        print(f"AKShare版本: {error_info['akshare_version']}")
        print(f"Python版本: {error_info['python_version']}")
        print(f"平台: {error_info['platform']}")
        print(f"附加信息: {error_info['message']}")
        if request_params:
            print(f"请求参数: {request_params}")
        if response_data:
            print(f"响应数据: {response_data[:1000] if len(response_data) > 1000 else response_data}")
        print(f"{'='*80}\n")

    def _get_income_statement(self, stock_code: str, period: str) -> Dict[str, Dict]:
        """获取利润表数据 - 优先使用新浪接口"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                if not AKSHARE_AVAILABLE:
                    print(f"警告: AKShare不可用，使用示例数据")
                    return {}

                print(f"\n{'='*80}")
                print(f"准备调用利润表接口 (重试次数: {retry_count + 1}/{max_retries})")
                print(f"股票代码: {stock_code}")
                print(f"数据周期: {period}")
                print(f"接口调用时间: {datetime.now().isoformat()}")
                print(f"{'='*80}\n")

                # 优先使用新浪接口
                print(f"调用新浪利润表接口: {stock_code}")

                try:
                    sina_request_params = {
                        "stock_code": stock_code,
                        "symbol": "利润表",
                        "period": period,
                        "api_name": "ak.stock_financial_report_sina"
                    }
                    print(f"新浪接口参数: {json.dumps(sina_request_params, ensure_ascii=False, indent=2)}")

                    df = ak.stock_financial_report_sina(stock_code, symbol="利润表")
                    print(f"新浪接口调用完成，返回类型: {type(df)}")

                    if df is None or (hasattr(df, 'empty') and df.empty):
                        raise Exception(f"新浪接口返回空数据 (股票: {stock_code})")

                    print(f"新浪利润表接口成功: {len(df)} 条记录")
                    return self._process_income_data(df)

                except Exception as e2:
                    print(f"新浪接口失败: {type(e2).__name__}: {e2}")

                    if retry_count < max_retries - 1:
                        print(f"等待2秒后重试...")
                        import time
                        time.sleep(2)
                        retry_count += 1
                        continue

                    # 最后一次重试失败，尝试备选方案
                    print(f"新浪接口失败，尝试东方财富接口作为备选")
                    try:
                        if period in ('quarter', 'Q1', 'Q2', 'Q3', 'Q4'):
                            df = ak.stock_profit_sheet_by_quarterly_em(stock_code)
                        else:
                            df = ak.stock_profit_sheet_by_report_em(stock_code)

                        if df is not None and not (hasattr(df, 'empty') and df.empty):
                            print(f"东方财富备选方案成功: {len(df)} 条记录")
                            return self._process_income_data(df)
                        else:
                            raise Exception("备选方案也返回空数据")
                    except Exception as e3:
                        print(f"备选方案失败: {e3}")
                        break

            except Exception as e:
                print(f"获取利润表数据时发生错误: {e}")
                if retry_count < max_retries - 1:
                    retry_count += 1
                    continue
                else:
                    break

        print(f"所有尝试都失败，返回空数据")
        return {}

    def _get_balance_sheet(self, stock_code: str, period: str) -> Dict[str, Dict]:
        """获取资产负债表数据 - 优先使用新浪接口"""
        try:
            if not AKSHARE_AVAILABLE:
                self._log_akshare_error("AKShare可用性检查", stock_code, Exception("AKShare未安装"), "跳过网络查询")
                return {}

            print(f"优先调用新浪资产负债表接口: {stock_code}")
            try:
                df = ak.stock_financial_report_sina(stock_code, symbol="资产负债表")
                if df is None:
                    self._log_akshare_error("stock_financial_report_sina", stock_code, Exception("API返回None"), "新浪资产负债表接口返回None")
                    raise Exception("API返回None")
                print(f"新浪资产负债表接口成功: {len(df)} 条记录")
                return self._process_balance_data(df)
            except Exception as e1:
                self._log_akshare_error("stock_financial_report_sina", stock_code, e1, "新浪资产负债表接口失败，尝试东方财富作为备选")
                # 尝试东方财富接口作为备选
                try:
                    df = ak.stock_balance_sheet_by_report_em(stock_code)
                    if df is None:
                        self._log_akshare_error("stock_balance_sheet_by_report_em", stock_code, Exception("API返回None"), "东方财富资产负债表接口返回None")
                        raise Exception("API返回None")
                    print(f"东方财富资产负债表接口备选方案成功: {len(df)} 条记录")
                    return self._process_balance_data(df)
                except Exception as e2:
                    self._log_akshare_error("stock_balance_sheet_by_report_em", stock_code, e2, "东方财富资产负债表接口备选方案也失败")
                    return {}

        except Exception as e:
            self._log_akshare_error("获取资产负债表数据", stock_code, e, "获取资产负债表数据失败")
            return {}

    def _get_cash_flow(self, stock_code: str, period: str) -> Dict[str, Dict]:
        """获取现金流量表数据 - 优先使用新浪接口"""
        try:
            if not AKSHARE_AVAILABLE:
                self._log_akshare_error("AKShare可用性检查", stock_code, Exception("AKShare未安装"), "跳过网络查询")
                return {}

            print(f"优先调用新浪现金流量表接口: {stock_code}")
            try:
                df = ak.stock_financial_report_sina(stock_code, symbol="现金流量表")
                if df is None:
                    self._log_akshare_error("stock_financial_report_sina", stock_code, Exception("API返回None"), "新浪现金流量表接口返回None")
                    raise Exception("API返回None")
                print(f"新浪现金流量表接口成功: {len(df)} 条记录")
                return self._process_cash_flow_data(df)
            except Exception as e1:
                self._log_akshare_error("stock_financial_report_sina", stock_code, e1, f"新浪{period}现金流量表接口失败，尝试东方财富作为备选")
                # 尝试东方财富接口作为备选
                try:
                    if period in ('quarter', 'Q1', 'Q2', 'Q3', 'Q4'):
                        df = ak.stock_cash_flow_sheet_by_quarterly_em(stock_code)
                    else:
                        df = ak.stock_cash_flow_sheet_by_report_em(stock_code)

                    if df is None:
                        api_name = f"stock_cash_flow_sheet_by_{period}ly_em" if period == 'quarter' else "stock_cash_flow_sheet_by_report_em"
                        self._log_akshare_error(api_name, stock_code, Exception("API返回None"), f"东方财富{period}现金流量表接口返回None")
                        raise Exception("API返回None")
                    print(f"东方财富{period}现金流量表接口备选方案成功: {len(df)} 条记录")
                    return self._process_cash_flow_data(df)
                except Exception as e2:
                    api_name = f"stock_cash_flow_sheet_by_{period}ly_em" if period == 'quarter' else "stock_cash_flow_sheet_by_report_em"
                    self._log_akshare_error(api_name, stock_code, e2, f"东方财富{period}现金流量表接口备选方案也失败")
                    return {}

        except Exception as e:
            self._log_akshare_error("获取现金流量表数据", stock_code, e, "获取现金流量表数据失败")
            return {}

    def _process_income_data(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """处理利润表数据"""
        result = {}

        if df is None or df.empty:
            return result

        try:
            # 遍历数据框，按年份组织数据
            for _, row in df.iterrows():
                # 尝试多种可能的字段名来获取报告日期
                report_date = str(row.get('报告期', '') or row.get('报告日', ''))
                if not report_date or report_date == 'nan':
                    continue

                # 从报告日格式（如20251231）中提取年份
                if len(report_date) == 8 and report_date.isdigit():
                    year = report_date[:4]  # 提取前4位作为年份

                    # 判断是否为季度数据：Q1(0331), Q2(0630), Q3(0930), Q4(1231)
                    quarter = None
                    if report_date.endswith('0331'):
                        quarter = 'Q1'
                    elif report_date.endswith('0630'):
                        quarter = 'Q2'
                    elif report_date.endswith('0930'):
                        quarter = 'Q3'
                    elif report_date.endswith('1231'):
                        quarter = 'Q4'

                    # 如果是季度数据，按年份和季度组织
                    if quarter:
                        if year not in result:
                            result[year] = {}
                        result[year][quarter] = {
                            '营业收入': self._safe_float(row.get('营业收入', 0) or row.get('营业总收入', 0)),
                            '净利润': self._safe_float(row.get('归属于母公司股东的净利润', 0) or row.get('净利润', 0)),
                            '营业成本': self._safe_float(row.get('营业成本', 0)),
                            '销售费用': self._safe_float(row.get('销售费用', 0)),
                            '管理费用': self._safe_float(row.get('管理费用', 0)),
                            '财务费用': self._safe_float(row.get('财务费用', 0))
                        }
                    else:
                        # 对于非标准日期格式，按年度处理
                        if year not in result:
                            result[year] = {
                                '营业收入': [self._safe_float(row.get('营业收入', 0) or row.get('营业总收入', 0))],
                                '净利润': [self._safe_float(row.get('归属于母公司股东的净利润', 0) or row.get('净利润', 0))],
                                '营业成本': [self._safe_float(row.get('营业成本', 0))],
                                '销售费用': [self._safe_float(row.get('销售费用', 0))],
                                '管理费用': [self._safe_float(row.get('管理费用', 0))],
                                '财务费用': [self._safe_float(row.get('财务费用', 0))]
                            }
                else:
                    # 如果不是8位数字格式，直接使用原始值
                    result[report_date] = {
                        '营业收入': [self._safe_float(row.get('营业收入', 0) or row.get('营业总收入', 0))],
                        '净利润': [self._safe_float(row.get('归属于母公司股东的净利润', 0) or row.get('净利润', 0))],
                        '营业成本': [self._safe_float(row.get('营业成本', 0))],
                        '销售费用': [self._safe_float(row.get('销售费用', 0))],
                        '管理费用': [self._safe_float(row.get('管理费用', 0))],
                        '财务费用': [self._safe_float(row.get('财务费用', 0))]
                    }
        except Exception as e:
            print(f"处理利润表数据时出错: {e}")

        return result

    def _process_balance_data(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """处理资产负债表数据"""
        result = {}

        if df is None or df.empty:
            return result

        try:
            for _, row in df.iterrows():
                report_date = str(row.get('报告期', ''))
                if not report_date or report_date == 'nan':
                    continue

                # 从报告日格式（如20251231）中提取年份
                if len(report_date) == 8 and report_date.isdigit():
                    year = report_date[:4]  # 提取前4位作为年份

                    # 判断是否为季度数据：Q1(0331), Q2(0630), Q3(0930), Q4(1231)
                    quarter = None
                    if report_date.endswith('0331'):
                        quarter = 'Q1'
                    elif report_date.endswith('0630'):
                        quarter = 'Q2'
                    elif report_date.endswith('0930'):
                        quarter = 'Q3'
                    elif report_date.endswith('1231'):
                        quarter = 'Q4'

                    # 如果是季度数据，按年份和季度组织
                    if quarter:
                        if year not in result:
                            result[year] = {}
                        result[year][quarter] = {
                            '总资产': self._safe_float(row.get('总资产', 0)),
                            '总负债': self._safe_float(row.get('总负债', 0)),
                            '所有者权益': self._safe_float(row.get('所有者权益', 0)),
                            '流动资产': self._safe_float(row.get('流动资产', 0)),
                            '流动负债': self._safe_float(row.get('流动负债', 0)),
                            '存货': self._safe_float(row.get('存货', 0)),
                            '货币资金': self._safe_float(row.get('货币资金', 0))
                        }
                    else:
                        # 对于非标准日期格式，按年度处理
                        if year not in result:
                            result[year] = {
                                '总资产': [self._safe_float(row.get('总资产', 0))],
                                '总负债': [self._safe_float(row.get('总负债', 0))],
                                '所有者权益': [self._safe_float(row.get('所有者权益', 0))],
                                '流动资产': [self._safe_float(row.get('流动资产', 0))],
                                '流动负债': [self._safe_float(row.get('流动负债', 0))],
                                '存货': [self._safe_float(row.get('存货', 0))],
                                '货币资金': [self._safe_float(row.get('货币资金', 0))]
                            }
                else:
                    # 如果不是8位数字格式，直接使用原始值
                    result[report_date] = {
                        '总资产': [self._safe_float(row.get('总资产', 0))],
                        '总负债': [self._safe_float(row.get('总负债', 0))],
                        '所有者权益': [self._safe_float(row.get('所有者权益', 0))],
                        '流动资产': [self._safe_float(row.get('流动资产', 0))],
                        '流动负债': [self._safe_float(row.get('流动负债', 0))],
                        '存货': [self._safe_float(row.get('存货', 0))],
                        '货币资金': [self._safe_float(row.get('货币资金', 0))]
                    }
        except Exception as e:
            print(f"处理资产负债表数据时出错: {e}")

        return result

    def _process_cash_flow_data(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """处理现金流量表数据"""
        result = {}

        if df is None or df.empty:
            return result

        try:
            for _, row in df.iterrows():
                report_date = str(row.get('报告期', '') or row.get('报告日', ''))
                if not report_date or report_date == 'nan':
                    continue

                # 从报告日格式（如20251231）中提取年份
                if len(report_date) == 8 and report_date.isdigit():
                    year = report_date[:4]  # 提取前4位作为年份

                    # 判断是否为季度数据：Q1(0331), Q2(0630), Q3(0930), Q4(1231)
                    quarter = None
                    if report_date.endswith('0331'):
                        quarter = 'Q1'
                    elif report_date.endswith('0630'):
                        quarter = 'Q2'
                    elif report_date.endswith('0930'):
                        quarter = 'Q3'
                    elif report_date.endswith('1231'):
                        quarter = 'Q4'

                    # 如果是季度数据，按年份和季度组织
                    if quarter:
                        if year not in result:
                            result[year] = {}
                        result[year][quarter] = {
                            '经营活动现金流': self._safe_float(row.get('经营活动产生的现金流量净额', 0)),
                            '投资活动现金流': self._safe_float(row.get('投资活动产生的现金流量净额', 0)),
                            '筹资活动现金流': self._safe_float(row.get('筹资活动产生的现金流量净额', 0)),
                            '现金净增加额': self._safe_float(row.get('现金及现金等价物净增加额', 0))
                        }
                    else:
                        # 对于非标准日期格式，按年度处理
                        if year not in result:
                            result[year] = {
                                '经营活动现金流': [self._safe_float(row.get('经营活动产生的现金流量净额', 0))],
                                '投资活动现金流': [self._safe_float(row.get('投资活动产生的现金流量净额', 0))],
                                '筹资活动现金流': [self._safe_float(row.get('筹资活动产生的现金流量净额', 0))],
                                '现金净增加额': [self._safe_float(row.get('现金及现金等价物净增加额', 0))]
                            }
                else:
                    # 如果不是8位数字格式，直接使用原始值
                    result[report_date] = {
                        '经营活动现金流': [self._safe_float(row.get('经营活动产生的现金流量净额', 0))],
                        '投资活动现金流': [self._safe_float(row.get('投资活动产生的现金流量净额', 0))],
                        '筹资活动现金流': [self._safe_float(row.get('筹资活动产生的现金流量净额', 0))],
                        '现金净增加额': [self._safe_float(row.get('现金及现金等价物净增加额', 0))]
                    }
        except Exception as e:
            print(f"处理现金流量表数据时出错: {e}")

        return result

    def _safe_float(self, value) -> float:
        """安全转换为浮点数 - 修复大数值处理问题"""
        result = pd.to_numeric(value, errors='coerce')
        if pd.isna(result):
            return 0.0
        return float(result)

    def _generate_sample_data(self, stock_code: str, start_year: str, end_year: str) -> Dict:
        """生成示例数据用于演示（委托给共享函数）"""
        from data_extraction.sample_data_source import generate_sample_data
        return generate_sample_data(stock_code, start_year, end_year)

    def get_stock_info(self, stock_code: str) -> Dict:
        """获取股票基本信息"""
        try:
            if not AKSHARE_AVAILABLE:
                return self._get_fallback_stock_info(stock_code)

            # 尝试使用AKShare获取股票信息
            try:
                # 使用股票基本信息接口
                df = ak.stock_individual_info_em(symbol=stock_code)
                if df is not None and not df.empty:
                    # 转换为字典格式
                    info_dict = {}
                    for _, row in df.iterrows():
                        key = row.get('item', '')
                        value = row.get('value', '')
                        if key and value:
                            info_dict[key] = value

                    # 提取关键信息
                    stock_name = info_dict.get('股票名称', '') or info_dict.get('公司全称', '') or f"股票{stock_code}"
                    industry = info_dict.get('行业', '') or info_dict.get('所属行业', '') or '未知行业'
                    market = self._determine_market(stock_code)

                    return {
                        'code': stock_code,
                        'name': stock_name,
                        'industry': industry,
                        'market': market,
                        'area': info_dict.get('地区', '') or info_dict.get('所在地', '') or '未知地区',
                        'pe': 0,
                        'pb': 0,
                        'total_share': 0,
                        'circulating_share': 0
                    }
            except Exception as e:
                print(f"使用AKShare获取股票信息失败: {e}")

            # 如果AKShare失败，尝试其他接口
            try:
                # 尝试使用股票列表接口
                stock_basics = ak.stock_zh_a_spot()
                if stock_basics is not None and not stock_basics.empty:
                    stock_data = stock_basics[stock_basics['代码'] == stock_code]
                    if not stock_data.empty:
                        row = stock_data.iloc[0]
                        return {
                            'code': stock_code,
                            'name': row.get('名称', f"股票{stock_code}"),
                            'industry': '未知行业',
                            'market': self._determine_market(stock_code),
                            'area': '未知地区',
                            'pe': 0,
                            'pb': 0,
                            'total_share': 0,
                            'circulating_share': 0
                        }
            except Exception as e2:
                print(f"使用股票列表接口获取信息失败: {e2}")

            # 如果所有接口都失败，返回默认信息
            return self._get_fallback_stock_info(stock_code)

        except Exception as e:
            print(f"获取股票信息时发生错误: {e}")
            return self._get_fallback_stock_info(stock_code)

    def _determine_market(self, stock_code: str) -> str:
        """根据股票代码判断市场"""
        if stock_code.startswith('6'):
            return '沪市A股'
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            return '深市A股'
        elif stock_code.startswith('4') or stock_code.startswith('8'):
            return '北交所'
        else:
            return '未知市场'

    def _get_fallback_stock_info(self, stock_code: str) -> Dict:
        """获取默认的股票信息"""
        # 预定义一些知名股票的信息
        known_stocks = {
            '600519': {'name': '贵州茅台', 'industry': '白酒', 'market': '沪市A股'},
            '000001': {'name': '平安银行', 'industry': '银行', 'market': '深市A股'},
            '000002': {'name': '万科A', 'industry': '房地产', 'market': '深市A股'},
            '600000': {'name': '浦发银行', 'industry': '银行', 'market': '沪市A股'},
            '600036': {'name': '招商银行', 'industry': '银行', 'market': '沪市A股'},
            '601318': {'name': '中国平安', 'industry': '保险', 'market': '沪市A股'},
            '000858': {'name': '五粮液', 'industry': '白酒', 'market': '深市A股'},
            '002415': {'name': '海康威视', 'industry': '安防设备', 'market': '深市A股'},
            '300059': {'name': '东方财富', 'industry': '互联网服务', 'market': '深市A股'},
        }

        if stock_code in known_stocks:
            stock_data = known_stocks[stock_code]
            return {
                'code': stock_code,
                'name': stock_data['name'],
                'industry': stock_data['industry'],
                'market': stock_data['market'],
                'area': '未知地区',
                'pe': 0,
                'pb': 0,
                'total_share': 0,
                'circulating_share': 0
            }
        else:
            # 返回通用默认信息
            return {
                'code': stock_code,
                'name': f"股票{stock_code}",
                'industry': '未知行业',
                'market': self._determine_market(stock_code),
                'area': '未知地区',
                'pe': 0,
                'pb': 0,
                'total_share': 0,
                'circulating_share': 0
            }

    def get_stock_financial_data(self, stock_code: str, start_year: str, end_year: str, period: str) -> Dict[str, Any]:
        """获取股票财务数据 - 主要接口方法"""
        result = {}

        try:
            print(f"\n{'='*80}")
            print(f"开始获取股票财务数据")
            print(f"股票代码: {stock_code}")
            print(f"时间范围: {start_year} - {end_year}")
            print(f"数据周期: {period}")
            print(f"{'='*80}\n")

            # 首先尝试获取真实数据
            if AKSHARE_AVAILABLE:
                try:
                    # 获取利润表数据
                    income_data = self._get_income_statement(stock_code, period)
                    if income_data:
                        result.update(income_data)

                    # 获取资产负债表数据
                    balance_data = self._get_balance_sheet(stock_code, period)
                    if balance_data:
                        # 合并资产负债表数据到结果中
                        for year, year_data in balance_data.items():
                            if year not in result:
                                result[year] = {}
                            if isinstance(year_data, dict):
                                for quarter, quarter_data in year_data.items():
                                    if isinstance(quarter_data, dict):
                                        if quarter not in result[year]:
                                            result[year][quarter] = {}
                                        result[year][quarter].update({
                                            'balance_sheet': quarter_data
                                        })
                            else:
                                # 年度数据格式
                                result[year] = {'balance_sheet': year_data}

                    # 获取现金流量表数据
                    cash_flow_data = self._get_cash_flow(stock_code, period)
                    if cash_flow_data:
                        # 合并现金流量表数据到结果中
                        for year, year_data in cash_flow_data.items():
                            if year not in result:
                                result[year] = {}
                            if isinstance(year_data, dict):
                                for quarter, quarter_data in year_data.items():
                                    if isinstance(quarter_data, dict):
                                        if quarter not in result[year]:
                                            result[year][quarter] = {}
                                        if 'balance_sheet' in result[year][quarter]:
                                            result[year][quarter]['cash_flow'] = quarter_data
                                        else:
                                            result[year][quarter].update({
                                                'cash_flow': quarter_data
                                            })
                            else:
                                # 年度数据格式
                                if 'balance_sheet' in result[year]:
                                    result[year]['cash_flow'] = year_data
                                else:
                                    result[year].update({'cash_flow': year_data})

                    # 如果没有获取到数据或数据不完整，使用示例数据
                    if not result:
                        print(f"警告: 未能获取到 {stock_code} 的真实数据，使用示例数据进行演示")
                        result = self._generate_sample_data(stock_code, start_year, end_year)

                except Exception as e:
                    print(f"获取真实数据时出错: {e}")
                    print(f"使用示例数据进行演示")
                    result = self._generate_sample_data(stock_code, start_year, end_year)
            else:
                print(f"AKShare不可用，使用示例数据进行演示")
                result = self._generate_sample_data(stock_code, start_year, end_year)

            # 确保数据结构一致性
            result = self._normalize_data_structure(result, period)

            # 过滤用户指定年份范围的数据
            filtered_result = {}
            start_y = int(start_year)
            end_y = int(end_year)

            for year, year_data in result.items():
                try:
                    year_int = int(year)
                    if start_y <= year_int <= end_y:
                        filtered_result[year] = year_data
                except (ValueError, TypeError):
                    # 如果年份转换失败，跳过这个年份
                    continue

            # 如果没有找到指定年份范围的数据，使用示例数据
            if not filtered_result:
                print(f"警告: 在{start_year}-{end_year}范围内未找到数据，使用示例数据")
                filtered_result = self._generate_sample_data(stock_code, start_year, end_year)

            print(f"成功获取 {len(filtered_result)} 年的数据 (过滤自 {len(result)} 年原始数据)")
            return filtered_result

        except Exception as e:
            print(f"获取股票财务数据时发生错误: {e}")
            # 返回示例数据作为最后备选
            return self._generate_sample_data(stock_code, start_year, end_year)

    def _normalize_data_structure(self, data: Dict, period: str) -> Dict:
        """标准化数据结构"""
        normalized = {}

        for year, year_data in data.items():
            if isinstance(year_data, dict):
                if period in ('quarter', 'Q1', 'Q2', 'Q3', 'Q4'):
                    # 季度数据
                    if period == 'quarter':
                        # 全部季度，保持原有结构
                        normalized[year] = {}
                        for quarter, quarter_data in year_data.items():
                            if isinstance(quarter_data, dict):
                                combined_data = {}
                                for key, value in quarter_data.items():
                                    if key not in ['balance_sheet', 'cash_flow']:
                                        combined_data[key] = value
                                if 'balance_sheet' in quarter_data:
                                    combined_data['balance_sheet'] = quarter_data['balance_sheet']
                                if 'cash_flow' in quarter_data:
                                    combined_data['cash_flow'] = quarter_data['cash_flow']
                                normalized[year][quarter] = combined_data
                            else:
                                normalized[year][quarter] = quarter_data
                    else:
                        # 单个季度（Q1/Q2/Q3/Q4），只保留匹配的季度
                        if period in year_data:
                            quarter_data = year_data[period]
                            if isinstance(quarter_data, dict):
                                combined_data = {}
                                for key, value in quarter_data.items():
                                    if key not in ['balance_sheet', 'cash_flow']:
                                        combined_data[key] = value
                                if 'balance_sheet' in quarter_data:
                                    combined_data['balance_sheet'] = quarter_data['balance_sheet']
                                if 'cash_flow' in quarter_data:
                                    combined_data['cash_flow'] = quarter_data['cash_flow']
                                normalized[year] = combined_data
                            else:
                                normalized[year] = quarter_data
                else:
                    # 年度数据，检查是否包含季度数据
                    if any(key.startswith('Q') for key in year_data.keys()):
                        # 包含季度数据，需要聚合为年度数据
                        annual_data = self._aggregate_quarterly_to_annual(year_data)
                        normalized[year] = annual_data
                    elif any(key in year_data for key in ['营业收入', '净利润']):
                        # 这是利润表格式的数据
                        normalized[year] = {
                            'income_statement': {k: [v] for k, v in year_data.items() if k not in ['balance_sheet', 'cash_flow']}
                        }
                        if 'balance_sheet' in year_data:
                            normalized[year]['balance_sheet'] = {k: [v] for k, v in year_data['balance_sheet'].items()}
                        if 'cash_flow' in year_data:
                            normalized[year]['cash_flow'] = {k: [v] for k, v in year_data['cash_flow'].items()}
                    else:
                        # 已经是正确格式的数据
                        normalized[year] = year_data
            else:
                normalized[year] = year_data

        return normalized

    def _aggregate_quarterly_to_annual(self, quarterly_data: Dict) -> Dict:
        """将季度数据聚合为年度数据"""
        annual_data = {
            'income_statement': {
                '营业收入': [0],
                '净利润': [0],
                '营业成本': [0],
                '销售费用': [0],
                '管理费用': [0],
                '财务费用': [0]
            },
            'balance_sheet': {
                '总资产': [0],
                '总负债': [0],
                '所有者权益': [0],
                '流动资产': [0],
                '流动负债': [0],
                '存货': [0],
                '货币资金': [0]
            },
            'cash_flow': {
                '经营活动现金流': [0],
                '投资活动现金流': [0],
                '筹资活动现金流': [0],
                '现金净增加额': [0]
            }
        }

        # 聚合利润表和现金流量表数据（相加）
        flow_items = ['营业收入', '净利润', '营业成本', '销售费用', '管理费用', '财务费用',
                     '经营活动现金流', '投资活动现金流', '筹资活动现金流', '现金净增加额']

        for quarter, quarter_data in quarterly_data.items():
            if not isinstance(quarter_data, dict):
                continue

            # 聚合利润表数据
            for item in ['营业收入', '净利润', '营业成本', '销售费用', '管理费用', '财务费用']:
                if item in quarter_data:
                    annual_data['income_statement'][item][0] += quarter_data[item]

            # 聚合现金流量表数据
            if 'cash_flow' in quarter_data and isinstance(quarter_data['cash_flow'], dict):
                for item in ['经营活动现金流', '投资活动现金流', '筹资活动现金流', '现金净增加额']:
                    if item in quarter_data['cash_flow']:
                        annual_data['cash_flow'][item][0] += quarter_data['cash_flow'][item]

        # 使用Q4的资产负债表数据作为年度数据
        if 'Q4' in quarterly_data and isinstance(quarterly_data['Q4'], dict):
            q4_data = quarterly_data['Q4']
            if 'balance_sheet' in q4_data and isinstance(q4_data['balance_sheet'], dict):
                for item in ['总资产', '总负债', '所有者权益', '流动资产', '流动负债', '存货', '货币资金']:
                    if item in q4_data['balance_sheet']:
                        annual_data['balance_sheet'][item][0] = q4_data['balance_sheet'][item]
            else:
                # 如果没有balance_sheet包装层，直接从Q4数据中提取
                for item in ['总资产', '总负债', '所有者权益', '流动资产', '流动负债', '存货', '货币资金']:
                    if item in q4_data:
                        annual_data['balance_sheet'][item][0] = q4_data[item]

        return annual_data