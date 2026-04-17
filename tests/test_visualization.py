# tests/test_visualization.py
def test_create_line_chart():
    from src.visualization.chart_generator import ChartGenerator

    chart_gen = ChartGenerator()
    data = {
        '年份': ['2021', '2022', '2023', '2024', '2025'],
        '营业收入': [1000, 1200, 1400, 1600, 1800]
    }

    fig = chart_gen.create_line_chart(data, '营业收入', '年度营收趋势')
    assert fig is not None

def test_create_bar_chart():
    from src.visualization.chart_generator import ChartGenerator

    chart_gen = ChartGenerator()
    data = {
        '年份': ['2021', '2022', '2023', '2024', '2025'],
        '净利润': [200, 240, 280, 320, 360]
    }

    fig = chart_gen.create_bar_chart(data, '净利润', '年度净利润对比')
    assert fig is not None