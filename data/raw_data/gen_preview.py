#!/usr/bin/env python3
"""生成三种淡色配色方案的 HTML 预览"""

html = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
body{background:#fff;padding:24px;font-family:-apple-system,BlinkMacSystemFont,sans-serif;}
h1{font-size:1.3rem;margin-bottom:8px;}
h2{color:#333;margin-top:36px;margin-bottom:12px;font-size:1.1rem;}
.sub{color:#888;margin-bottom:24px;}
.preview-section{margin-bottom:40px;}
</style>
</head>
<body>
<h1>三种淡色表格配色方案</h1>
<p class="sub">请选择你喜欢的风格，我直接用对应方案替换代码</p>

<!-- ====== 方案A：东方财富风格 ====== -->
<div class="preview-section">
<h2>方案A — 东方财富风格（推荐，最主流）</h2>
<style>
.t-a {width:100%;border-collapse:collapse;}
.t-a thead th{background:#f5f5f5;color:#333;font-weight:600;padding:10px 14px;text-align:center;border:1px solid #e0e0e0;font-size:0.82rem;white-space:nowrap;}
.t-a tbody tr:nth-child(odd){background:#fff;}
.t-a tbody tr:nth-child(even){background:#f8f9fa;}
.t-a tbody tr:hover{background:#e3f2fd !important;}
.t-a td{padding:10px 14px;text-align:center;border:1px solid #eee;white-space:nowrap;color:#222;font-size:0.82rem;font-weight:500;}
.t-a .nc{text-align:left!important;font-weight:700;color:#111;}
.t-a .br{display:inline-block;padding:2px 8px;border-radius:4px;background:#ffebee;color:#c62828;font-weight:700;font-size:0.78rem;}
.t-a .bg{display:inline-block;padding:2px 8px;border-radius:4px;background:#e8f5e9;color:#2e7d32;font-weight:700;font-size:0.78rem;}
.t-a .buy{color:#c62828;font-weight:700;}
.t-a .sell{color:#2e7d32;font-weight:700;}
.t-a tr.sp td{background:#fff8e1!important;border-left:3px solid #ffb300;font-weight:600;color:#5d4037;}
</style>
<table class="t-a">
<thead><tr><th>持股名称</th><th>持股比例</th><th>当前市值</th><th>理想买点</th><th>年内卖点</th><th>当前股价</th><th>年内涨幅</th></tr></thead>
<tbody>
<tr><td class="nc">腾讯控股</td><td>55%</td><td>4,200</td><td class="buy">46,500</td><td class="sell">128,000</td><td>365.500</td><td><span class="br">+18.50%</span></td></tr>
<tr><td class="nc">贵州茅台</td><td>15%</td><td>2,100</td><td class="buy">16,800</td><td class="sell">47,000</td><td>1,680.00</td><td><span class="bg">-5.20%</span></td></tr>
<tr><td class="nc">分众传媒</td><td>12%</td><td>890</td><td class="buy">890</td><td class="sell">1,900</td><td>8.90</td><td><span class="br">+3.10%</span></td></tr>
<tr><td class="nc">古井贡B</td><td>7%</td><td>650</td><td class="buy">790</td><td class="sell">1,900</td><td>79.00</td><td><span class="bg">-12.30%</span></td></tr>
<tr><td class="nc">银华日利</td><td>6%</td><td>100</td><td class="buy">&mdash;</td><td class="sell">&mdash;</td><td>100.235</td><td><span class="br">+0.80%</span></td></tr>
<tr><td class="nc">海康威视</td><td>4%</td><td>320</td><td class="buy">1,920</td><td class="sell">5,700</td><td>32.50</td><td><span class="bg">-8.40%</span></td></tr>
<tr class="sp"><td class="nc">实盘净值</td><td colspan="2">基金净值法</td><td style="border-right:none">周涨幅</td><td style="border-left:none"><span class="bg">-4.38%</span></td><td>0.874</td><td><span class="bg">-13.73%</span></td></tr>
<tr class="sp"><td class="nc">对比基准</td><td colspan="2">沪深300指数基金 510310</td><td style="border-right:none">周涨幅</td><td style="border-left:none"><span class="br">+1.20%</span></td><td>4.321</td><td><span class="br">+3.67%</span></td></tr>
<tr class="sp"><td class="nc">2026/04/25</td><td colspan="2">市值亿元，腾讯古B股价为港币</td><td colspan="2" style="text-align:right">港币汇率</td><td>0.8713</td><td><span class="bg">-2.10%</span></td></tr>
</tbody></table>
</div>

<!-- ====== 方案B：同花顺风格 ====== -->
<div class="preview-section">
<h2>方案B — 同花顺 iFinD 风格</h2>
<style>
.t-b {width:100%;border-collapse:collapse;}
.t-b thead th{background:#e8f0fe;color:#1565c0;font-weight:700;padding:10px 14px;text-align:center;border:1px solid #bbdefb;font-size:0.82rem;white-space:nowrap;}
.t-b tbody tr:nth-child(odd){background:#fff;}
.t-b tbody tr:nth-child(even){background:#f5f9ff;}
.t-b tbody tr:hover{background:#e1f5fe !important;}
.t-b td{padding:10px 14px;text-align:center;border:1px solid #e3f2fd;white-space:nowrap;color:#1a237e;font-size:0.82rem;font-weight:500;}
.t-b .nc{text-align:left!important;font-weight:700;color:#0d47a1;}
.t-b .br{display:inline-block;padding:2px 8px;border-radius:4px;background:#fff3e0;color:#bf360c;font-weight:700;font-size:0.78rem;}
.t-b .bg{display:inline-block;padding:2px 8px;border-radius:4px;background:#e0f2f1;color:#004d40;font-weight:700;font-size:0.78rem;}
.t-b .buy{color:#bf360c;font-weight:700;}
.t-b .sell{color:#004d40;font-weight:700;}
.t-b tr.sp td{background:#fce4ec!important;border-left:3px solid #f06292;font-weight:600;color:#880e4f;}
</style>
<table class="t-b">
<thead><tr><th>持股名称</th><th>持股比例</th><th>当前市值</th><th>理想买点</th><th>年内卖点</th><th>当前股价</th><th>年内涨幅</th></tr></thead>
<tbody>
<tr><td class="nc">腾讯控股</td><td>55%</td><td>4,200</td><td class="buy">46,500</td><td class="sell">128,000</td><td>365.500</td><td><span class="br">+18.50%</span></td></tr>
<tr><td class="nc">贵州茅台</td><td>15%</td><td>2,100</td><td class="buy">16,800</td><td class="sell">47,000</td><td>1,680.00</td><td><span class="bg">-5.20%</span></td></tr>
<tr><td class="nc">分众传媒</td><td>12%</td><td>890</td><td class="buy">890</td><td class="sell">1,900</td><td>8.90</td><td><span class="br">+3.10%</span></td></tr>
<tr><td class="nc">古井贡B</td><td>7%</td><td>650</td><td class="buy">790</td><td class="sell">1,900</td><td>79.00</td><td><span class="bg">-12.30%</span></td></tr>
<tr><td class="nc">银华日利</td><td>6%</td><td>100</td><td class="buy">&mdash;</td><td class="sell">&mdash;</td><td>100.235</td><td><span class="br">+0.80%</span></td></tr>
<tr><td class="nc">海康威视</td><td>4%</td><td>320</td><td class="buy">1,920</td><td class="sell">5,700</td><td>32.50</td><td><span class="bg">-8.40%</span></td></tr>
<tr class="sp"><td class="nc">实盘净值</td><td colspan="2">基金净值法</td><td style="border-right:none">周涨幅</td><td style="border-left:none"><span class="bg">-4.38%</span></td><td>0.874</td><td><span class="bg">-13.73%</span></td></tr>
<tr class="sp"><td class="nc">对比基准</td><td colspan="2">沪深300指数基金 510310</td><td style="border-right:none">周涨幅</td><td style="border-left:none"><span class="br">+1.20%</span></td><td>4.321</td><td><span class="br">+3.67%</span></td></tr>
<tr class="sp"><td class="nc">2026/04/25</td><td colspan="2">市值亿元，腾讯古B股价为港币</td><td colspan="2" style="text-align:right">港币汇率</td><td>0.8713</td><td><span class="bg">-2.10%</span></td></tr>
</tbody></table>
</div>

<!-- ====== 方案C：雪球风格 ====== -->
<div class="preview-section">
<h2>方案C — 雪球风格（极简）</h2>
<style>
.t-c {width:100%;border-collapse:collapse;}
.t-c thead th{background:transparent;color:#888;font-weight:500;padding:12px 14px 8px;text-align:center;border:none;border-bottom:2px solid #ddd;white-space:nowrap;font-size:0.8rem;letter-spacing:1px;}
.t-c tbody tr{border-bottom:1px solid #f0f0f0;}
.t-c tbody tr:hover{background:#fafafa;}
.t-c td{padding:12px 14px;text-align:center;white-space:nowrap;color:#333;font-size:0.85rem;}
.t-c .nc{text-align:left!important;font-weight:600;color:#111;}
.t-c .tr{color:#d32f2f;font-weight:600;}
.t-c .tg{color:#388e3c;font-weight:600;}
.t-c .buy{color:#d32f2f;font-weight:700;}
.t-c .sell{color:#388e3c;font-weight:700;}
.t-c tr.sp td{background:#fafafa;font-weight:600;color:#444;}
</style>
<table class="t-c">
<thead><tr><th>持股名称</th><th>持股比例</th><th>当前市值</th><th>理想买点</th><th>年内卖点</th><th>当前股价</th><th>年内涨幅</th></tr></thead>
<tbody>
<tr><td class="nc">腾讯控股</td><td>55%</td><td>4,200</td><td class="buy">46,500</td><td class="sell">128,000</td><td>365.500</td><td class="tr">+18.50%</td></tr>
<tr><td class="nc">贵州茅台</td><td>15%</td><td>2,100</td><td class="buy">16,800</td><td class="sell">47,000</td><td>1,680.00</td><td class="tg">-5.20%</td></tr>
<tr><td class="nc">分众传媒</td><td>12%</td><td>890</td><td class="buy">890</td><td class="sell">1,900</td><td>8.90</td><td class="tr">+3.10%</td></tr>
<tr><td class="nc">古井贡B</td><td>7%</td><td>650</td><td class="buy">790</td><td class="sell">1,900</td><td>79.00</td><td class="tg">-12.30%</td></tr>
<tr><td class="nc">银华日利</td><td>6%</td><td>100</td><td class="buy">&mdash;</td><td class="sell">&mdash;</td><td>100.235</td><td class="tr">+0.80%</td></tr>
<tr><td class="nc">海康威视</td><td>4%</td><td>320</td><td class="buy">1,920</td><td class="sell">5,700</td><td>32.50</td><td class="tg">-8.40%</td></tr>
<tr class="sp"><td class="nc">实盘净值</td><td colspan="2">基金净值法</td><td style="border-right:none">周涨幅</td><td style="border-left:none tg">-4.38%</td><td>0.874</td><td class="tg">-13.73%</td></tr>
<tr class="sp"><td class="nc">对比基准</td><td colspan="2">沪深300指数基金 510310</td><td style="border-right:none">周涨幅</td><td style="border-left:none tr">+1.20%</td><td>4.321</td><td class="tr">+3.67%</td></tr>
<tr class="sp"><td class="nc">2026/04/25</td><td colspan="2">市值亿元，腾讯古B股价为港币</td><td colspan="2" style="text-align:right">港币汇率</td><td>0.8713</td><td class="tg">-2.10%</td></tr>
</tbody></table>
</div>

</body></html>"""

with open('data/raw_data/table_light_preview.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('OK')
