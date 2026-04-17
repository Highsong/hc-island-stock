# tests/integration_test.py
import os

def test_full_analysis_pipeline():
    """测试完整分析流程"""
    from src.app import DataProcessor

    processor = DataProcessor()

    # 测试数据处理
    result = processor.process_selected_years(['2023', '2024', '2025'])

    assert isinstance(result, dict)
    assert 'charts' in result
    assert 'insights' in result
    assert 'latest_year' in result

def test_pdf_extraction_integration():
    """测试PDF提取集成"""
    from src.data_extraction.pdf_parser import PDFParser
    from src.data_extraction.data_cleaner import DataCleaner

    parser = PDFParser()
    cleaner = DataCleaner()

    # 如果有测试PDF文件，进行实际测试
    test_pdf = "data/raw_pdfs/02MT2025年年报.pdf"
    if os.path.exists(test_pdf):
        raw_data = parser.extract_financial_tables(test_pdf)
        cleaned_data = cleaner.clean_financial_data(raw_data)

        assert isinstance(cleaned_data, dict)

def test_chart_generation_integration():
    """测试图表生成集成"""
    from src.visualization.chart_generator import ChartGenerator

    chart_gen = ChartGenerator()
    test_data = {
        '年份': ['2021', '2022', '2023'],
        '营业收入': [1000, 1200, 1400]
    }

    chart = chart_gen.create_line_chart(test_data, '营业收入', '测试图表')
    assert chart is not None

def test_financial_analysis_integration():
    """测试财务分析集成"""
    from src.analysis.financial_metrics import FinancialMetrics
    from src.analysis.insights_generator import InsightsGenerator

    # 测试数据
    income_data = {
        '营业收入': [1000, 1200, 1400],
        '净利润': [200, 240, 280],
        '营业成本': [600, 720, 840]
    }

    # 计算指标
    metrics = FinancialMetrics()
    ratios = metrics.calculate_profitability_ratios(income_data)
    growth_rates = metrics.calculate_growth_rates(income_data)

    # 生成洞察
    insights_gen = InsightsGenerator()
    insights = insights_gen.generate_comprehensive_report({
        'profitability_ratios': ratios,
        'growth_rates': growth_rates
    })

    assert isinstance(insights, dict)
    assert 'profitability' in insights
    assert 'growth' in insights

def test_data_processing_pipeline():
    """测试数据处理流水线"""
    import os
    import sys
    sys.path.append('src')

    from src.utils.helpers import detect_new_reports, extract_year_from_filename
    from src.data_extraction.pdf_parser import PDFParser
    from src.data_extraction.data_cleaner import DataCleaner

    # 检测PDF文件
    pdf_files = detect_new_reports()
    assert len(pdf_files) > 0, "应该至少检测到一个PDF文件"

    # 提取年份
    for pdf_file in pdf_files[:1]:  # 只测试第一个文件
        year = extract_year_from_filename(pdf_file)
        assert year != '未知年份', f"应该能从 {pdf_file} 提取年份"

        # 测试PDF解析
        pdf_path = os.path.join('data/raw_pdfs', pdf_file)
        if os.path.exists(pdf_path):
            parser = PDFParser()
            raw_data = parser.extract_financial_tables(pdf_path)

            # 测试数据清洗
            cleaner = DataCleaner()
            cleaned_data = cleaner.clean_financial_data(raw_data)

            assert isinstance(cleaned_data, dict)
            break