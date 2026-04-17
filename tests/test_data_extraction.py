# tests/test_data_extraction.py
def test_pdf_parser_initialization():
    from src.data_extraction.pdf_parser import PDFParser
    parser = PDFParser()
    assert parser is not None

def test_extract_financial_tables():
    from src.data_extraction.pdf_parser import PDFParser
    parser = PDFParser()
    # 测试文件路径需要根据实际文件调整
    result = parser.extract_financial_tables("data/raw_pdfs/02MT2025年年报.pdf")
    assert isinstance(result, dict)
    assert "income_statement" in result
    assert "balance_sheet" in result
    assert "cash_flow" in result