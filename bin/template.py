# -*- coding:utf-8 -*-

report_html_header = """
<html>
<style type="text/css">
th{
    background: #a6caf0;
    align:center;
    vertical-align:middle;
}
td{
    background:#bfbfbf;
    font-weight:bold;
    color:green;
}
</style>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
</head>
</body>
<div align="center">
    <p><strong>服务器系统信息</strong></p>
    <table border="0" cellpadding="5" cellspacing="2"  width="50%%">
        <tr>
            <th>监控时间段</th>
            <td>%s</td>
        </tr>
        <tr>
            <th>主机名</th>
            <td>%s</td>
        </tr>
        <tr>
            <th>内核版本</th>
            <td>%s</td>
        </tr>
        <tr>
            <th>CPU</th>
            <td>%s</td>
        </tr>
        <tr>
            <th>内存</th>
            <td>%s</td>
        </tr>
        </table>
        <p></p>
"""

report_resource_html_header = """
    <p><strong>服务器资源使用情况汇总 (%s) </strong></p>
    <table border="0" cellpadding="5" cellspacing="2"  width="60%%">
    <tr>
        <th>Item</th>
        <th>Type</th>
        <th>Min</th>
        <th>Max</th>
        <th>Avg</th>
        <th>90%%小于</th>
    </tr>
"""

report_resource_html_data_mult = """
    <tr>
        <th rowspan="%s">%s</th>
        <td><a href="%s" target="_png">%s%s</a></td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
    </tr>
"""
report_resource_html_data_single = """
    <tr>
        <td><a href="%s" target="_png">%s%s</a></td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
    </tr>
"""

report_html_end = """
    </table>
</body>
</html>
"""
