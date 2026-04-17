#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东雪数据查询 - 整合东方财富+雪球
支持股票行情、K线、基金信息、板块资金流向、热门排行、条件选股等
"""

import json
import sys
import os
import time
import urllib.request
import urllib.parse
from datetime import datetime


# ============== 通用配置 ==============
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/147.0.0.0 Safari/537.36"
)

MARKET_MAP = {
    'sh': '1',  # 沪市
    'sz': '0',  # 深市
}


# ============== 东方财富模块 ==============
class EastMoneyAPI:
    """东方财富API"""
    
    @staticmethod
    def parse_stock_code(code):
        """解析股票代码为东方财富格式"""
        code = str(code).strip().lower()
        if '.' in code:
            return code
        if code.isdigit():
            if code.startswith('6'):
                return f'1.{code}'
            else:
                return f'0.{code}'
        prefix = code[:2]
        if prefix in MARKET_MAP:
            return f'{MARKET_MAP[prefix]}{code[2:]}'
        raise ValueError(f'无法解析股票代码: {code}')
    
    @staticmethod
    def request_json(url, referer='https://quote.eastmoney.com/'):
        """发送请求并返回JSON"""
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', UA)
            if referer:
                req.add_header('Referer', referer)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                # 检查东方财富API的错误码
                if isinstance(data, dict):
                    err_code = data.get('ErrCode') or data.get('ErrorCode')
                    if err_code and err_code != 0 and err_code != '0':
                        err_msg = data.get('ErrMsg') or data.get('ErrorMessage') or '未知错误'
                        print(f'API错误 [{err_code}]: {err_msg}')
                        return None
                return data
        except Exception as e:
            print(f'请求异常: {e}')
            return None
    
    @classmethod
    def get_stock_quote(cls, code, detail=False):
        """获取股票行情"""
        secid = cls.parse_stock_code(code)
        fields = 'f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18'
        if detail:
            fields += ',f9,f20,f21,f23,f29,f100,f101,f162,f163,f170,f171,f173'
        
        url = f'https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields={fields}&secids={secid}&_={int(time.time() * 1000)}'
        data = cls.request_json(url)
        if data and data.get('data') and data['data'].get('diff'):
            return data['data']['diff'][0]
        return None
    
    @classmethod
    def get_sector_fund_flow(cls, sector_type='industry', key_type='today'):
        """获取板块资金流向"""
        key_map = {'today': 'f62', '5day': 'f164', '10day': 'f174'}
        code_map = {
            'industry': 'm:90+s:4',
            'concept': 'm:90+e:4',
            'theme': 'm:90+t:3',
            'region': 'm:90+t:1',
        }
        key = key_map.get(key_type, 'f62')
        code = code_map.get(sector_type, 'm:90+s:4')
        url = f'https://data.eastmoney.com/dataapi/bkzj/getbkzj?key={key}&code={code}'
        data = cls.request_json(url)
        if data and data.get('data'):
            return data['data']
        return None
    
    @classmethod
    def get_fund_info(cls, fund_code):
        """获取基金信息"""
        import random
        device_id = str(random.randint(100000, 999999))
        url = f'https://fundmobapi.eastmoney.com/FundMNewApi/FundMNFInfo?plat=Android&appType=ttjj&product=EFund&Fcodes={fund_code}&deviceid={device_id}&version=6.4.8'
        data = cls.request_json(url, referer='https://fund.eastmoney.com/')
        if data and data.get('Datas'):
            datas = data['Datas']
            if isinstance(datas, list) and len(datas) > 0:
                return datas[0]
            elif isinstance(datas, dict):
                return datas
        return None
    
    @classmethod
    def get_fund_estimate(cls, fund_code):
        """获取基金估值"""
        url = f'https://fundgz.1234567.com.cn/js/{fund_code}.js'
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', UA)
            req.add_header('Referer', 'https://fund.eastmoney.com/')
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8')
                start = content.find('(')
                end = content.rfind(')')
                if start != -1 and end != -1:
                    return json.loads(content[start + 1:end])
        except Exception as e:
            print(f'请求异常: {e}')
        return None
    
    @classmethod
    def search_fund(cls, keyword):
        """搜索基金"""
        encoded = urllib.parse.quote(keyword)
        url = f'https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx?m=9&key={encoded}'
        data = cls.request_json(url, referer='https://fund.eastmoney.com/')
        if data and data.get('Datas'):
            return data['Datas'][:10]
        return None


# ============== 雪球模块 ==============
class XueqiuAPI:
    """雪球API"""
    
    def __init__(self):
        self.session = self._create_session()
    
    def _create_session(self):
        """创建会话并预热cookie"""
        session = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor()
        )
        headers = {'User-Agent': UA, 'Referer': 'https://xueqiu.com/hq'}
        req = urllib.request.Request('https://xueqiu.com/hq', headers=headers)
        try:
            session.open(req, timeout=20)
        except:
            pass
        return session
    
    def request_json(self, url, params=None):
        """发送请求并返回JSON"""
        if params:
            query = urllib.parse.urlencode(params)
            url = f'{url}?{query}'
        
        headers = {
            'User-Agent': UA,
            'Referer': 'https://xueqiu.com/hq',
            'Accept': 'application/json,text/plain,*/*',
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with self.session.open(req, timeout=20) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f'请求异常: {e}')
            return None
    
    @staticmethod
    def parse_stock_code(code):
        """解析股票代码为雪球格式"""
        code = str(code).strip().upper()
        if code.startswith(('SH', 'SZ', 'HK')):
            return code
        if code.isdigit():
            if code.startswith('6'):
                return f'SH{code}'
            elif code.startswith('3') or code.startswith('0'):
                return f'SZ{code}'
            else:
                return f'SH{code}'
        prefix = code[:2]
        if prefix in ['SH', 'SZ', 'HK']:
            return code
        raise ValueError(f'无法解析股票代码: {code}')
    
    def get_stock_quote(self, code):
        """获取股票行情"""
        symbol = self.parse_stock_code(code)
        url = 'https://stock.xueqiu.com/v5/stock/quote.json'
        data = self.request_json(url, {'symbol': symbol, 'extend': 'detail'})
        if data and data.get('error_code') == 0:
            return data.get('data', {}).get('quote', {})
        return None
    
    def get_kline(self, code, period='day', count=30):
        """获取K线数据"""
        symbol = self.parse_stock_code(code)
        url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json'
        begin = int(time.time() * 1000) - (count * 86400 * 1000)
        period_map = {
            'day': 'day', 'week': 'week', 'month': 'month',
            '5m': '5m', '15m': '15m', '30m': '30m', '60m': '60m',
        }
        data = self.request_json(url, {
            'symbol': symbol,
            'begin': begin,
            'period': period_map.get(period, 'day'),
            'type': 'before',
            'count': -count,
        })
        if data and data.get('error_code') == 0:
            return data.get('data', {})
        return None
    
    def get_hot_stocks(self, stock_type=11):
        """获取热门股票"""
        url = 'https://stock.xueqiu.com/v5/stock/hot_stock/list.json'
        data = self.request_json(url, {'size': 30, 'type': stock_type})
        if data and data.get('error_code') == 0:
            raw = data.get('data', {})
            return raw.get('items', [])
        return []
    
    def get_fund_feed(self, page=1):
        """获取基金动态"""
        url = 'https://xueqiu.com/statuses/fundx/public/list.json'
        data = self.request_json(url, {'source': 'fund_public', 'page': page})
        if data:
            return data.get('list', []), data.get('has_next_page', False)
        return [], False
    
    def get_screener(self, pe_max=None, mcap_min=None, pct_min=None):
        """条件选股"""
        url = 'https://stock.xueqiu.com/v5/stock/screener/quote/list.json'
        params = {
            'page': 1, 'size': 30,
            'order_by': 'percent', 'order': 'desc',
            'exchange': 'CN', 'market': 'CN', 'type': 11,
        }
        if pe_max: params['pe_ttm_max'] = pe_max
        if mcap_min: params['market_capital_min'] = mcap_min
        if pct_min: params['percent_min'] = pct_min
        data = self.request_json(url, params)
        if data and data.get('error_code') == 0:
            return data.get('data', {})
        return {}


# ============== 格式化输出 ==============
def format_quote(data, source=''):
    """格式化股票行情"""
    if not data:
        print(f'获取行情失败')
        return
    
    print(f"\n{'='*60}")
    if source:
        print(f"【{source}】")
    print(f"{'='*60}")
    
    # 东方财富格式
    if 'f14' in data:
        name = data.get('f14', 'N/A')
        code = data.get('f12', 'N/A')
        price = data.get('f2', 0)
        change_pct = data.get('f3', 0)
        change_amt = data.get('f4', 0)
        volume = data.get('f5', 0)
        amount = data.get('f6', 0)
        amplitude = data.get('f7', 0)
        turnover = data.get('f8', 0)
        pe = data.get('f9', 0)
        high = data.get('f15', 0)
        low = data.get('f16', 0)
        open_price = data.get('f17', 0)
        prev_close = data.get('f18', 0)
        total_mv = data.get('f20', 0)
        float_mv = data.get('f21', 0)
        pb = data.get('f23', 0)
    # 雪球格式
    else:
        name = data.get('name', 'N/A')
        code = data.get('code', 'N/A')
        price = data.get('current', 0)
        change_pct = data.get('percent', 0)
        change_amt = data.get('chg', 0)
        volume = data.get('volume', 0)
        amount = data.get('amount', 0)
        amplitude = data.get('amplitude', 0)
        turnover = data.get('turnover_rate', 0)
        pe = data.get('pe_ttm', 0)
        high = data.get('high', 0)
        low = data.get('low', 0)
        open_price = data.get('open', 0)
        prev_close = data.get('last_close', 0)
        total_mv = data.get('market_capital', 0)
        float_mv = data.get('float_market_capital', 0)
        pb = data.get('pb', 0)
    
    print(f"\n  {name} ({code})")
    print(f"  {'─'*50}")
    print(f"  当前价:      {price}")
    print(f"  涨跌幅:      {change_pct}%")
    print(f"  涨跌额:      {change_amt}")
    print(f"  成交量:      {volume:,}")
    print(f"  成交额:      {amount:,.2f}")
    print(f"  振幅:        {amplitude}%")
    print(f"  换手率:      {turnover}%")
    print(f"  最高:        {high}")
    print(f"  最低:        {low}")
    print(f"  今开:        {open_price}")
    print(f"  昨收:        {prev_close}")
    print(f"  市盈率(TTM):  {pe}")
    print(f"  市净率:      {pb}")
    print(f"  总市值:      {total_mv/100000000:.2f} 亿" if total_mv else "  总市值:      N/A")
    print(f"  流通市值:    {float_mv/100000000:.2f} 亿" if float_mv else "  流通市值:    N/A")


def format_kline(data):
    """格式化K线数据"""
    if not data:
        print('获取K线失败')
        return
    
    items = data.get('item', [])
    columns = data.get('column', [])
    
    print(f"\n{'='*60}")
    print(f"雪球K线数据")
    print(f"{'='*60}")
    
    for item in items[-10:]:
        print(f"\n  日期: {datetime.fromtimestamp(item[0]/1000).strftime('%Y-%m-%d')}")
        for i, col in enumerate(columns):
            if i == 0: continue
            print(f"    {col}: {item[i]}")


def format_sector_flow(data, key_type='today'):
    """格式化板块资金流向"""
    if not data or 'diff' not in data:
        print('获取板块资金流向失败')
        return
    
    items = data['diff'][:20]
    print(f"\n{'='*60}")
    print(f"东方财富板块资金流向 ({key_type})")
    print(f"{'='*60}")
    
    for item in items:
        name = item.get('f14', 'N/A')
        code = item.get('f12', 'N/A')
        flow = item.get('f62', 0)
        print(f"  {name} ({code}): {flow:,}")


def format_fund_info(data, source='东方财富'):
    """格式化基金信息"""
    if not data:
        print('获取基金信息失败')
        return
    
    print(f"\n{'='*60}")
    print(f"【{source}】基金信息")
    print(f"{'='*60}")
    
    # 东方财富格式
    if 'FCODE' in data:
        name = data.get('SHORTNAME', 'N/A')
        code = data.get('FCODE', 'N/A')
        nav = data.get('NAV', 'N/A')
        acc_nav = data.get('ACCNAV', 'N/A')
        nav_chg = data.get('NAVCHGRT', 'N/A')
        pdate = data.get('PDATE', 'N/A')
    else:
        name = data.get('name', 'N/A')
        code = data.get('fundcode', 'N/A')
        nav = data.get('dwjz', 'N/A')
        acc_nav = 'N/A'
        nav_chg = data.get('gszzl', 'N/A')
        pdate = data.get('jzrq', 'N/A')
    
    print(f"\n  {name} ({code})")
    print(f"  净值日期:  {pdate}")
    print(f"  单位净值:  {nav}")
    if acc_nav != 'N/A':
        print(f"  累计净值:  {acc_nav}")
    print(f"  日增长率:  {nav_chg}%")


def format_fund_feed(items, has_next=False):
    """格式化基金动态"""
    print(f"\n{'='*60}")
    print(f"雪球基金动态")
    print(f"{'='*60}")
    
    for item in items[:10]:
        desc = item.get('description', '')[:100]
        created = item.get('created_at', 0)
        date_str = datetime.fromtimestamp(created/1000).strftime('%Y-%m-%d %H:%M') if created else 'N/A'
        print(f"\n  时间: {date_str}")
        print(f"  内容: {desc}")
    
    if has_next:
        print(f"\n  [有更多数据]")


def format_fund_search(items):
    """格式化基金搜索结果"""
    print(f"\n{'='*60}")
    print(f"东方财富基金搜索")
    print(f"{'='*60}")
    
    for item in items[:10]:
        base = item.get('FundBaseInfo', item)
        name = base.get('SHORTNAME') or item.get('NAME') or 'N/A'
        code = base.get('FCODE') or item.get('CODE') or 'N/A'
        ftype = base.get('FTYPE') or item.get('CATEGORYDESC') or 'N/A'
        dwjz = base.get('DWJZ') or base.get('NAV') or 'N/A'
        pdate = base.get('PDATE') or base.get('FSRQ') or 'N/A'
        jjgs = base.get('JJGS') or 'N/A'
        
        print(f"\n  {name} ({code})")
        print(f"    类型: {ftype}")
        print(f"    最新净值: {dwjz}")
        print(f"    净值日期: {pdate}")
        print(f"    基金公司: {jjgs}")


def format_hot_stocks(items):
    """格式化热门股票"""
    print(f"\n{'='*60}")
    print(f"雪球热门股票")
    print(f"{'='*60}")
    
    if not items:
        print("暂无数据")
        return
    
    for i, stock in enumerate(items[:20], 1):
        print(f"\n  {i:2d}. {stock.get('name', 'N/A')} ({stock.get('code', 'N/A')})")
        print(f"      当前价: {stock.get('current', 'N/A')}  涨幅: {stock.get('percent', 'N/A')}%")


def format_screener(data):
    """格式化选股结果"""
    if not data:
        print('选股失败')
        return
    
    stocks = data.get('list', [])
    count = data.get('count', 0)
    
    print(f"\n{'='*60}")
    print(f"雪球条件选股 (共 {count} 条)")
    print(f"{'='*60}")
    
    for i, stock in enumerate(stocks[:20], 1):
        print(f"\n  {i:2d}. {stock.get('name', 'N/A')} ({stock.get('symbol', 'N/A')})")
        print(f"      当前价: {stock.get('current', 'N/A')}  涨幅: {stock.get('percent', 'N/A')}%")
        print(f"      市盈率: {stock.get('pe_ttm', 'N/A')}  市值: {stock.get('market_capital', 'N/A')}")


# ============== 主入口 ==============
def main():
    if len(sys.argv) < 2:
        print("用法: python dongxue_api.py <command> [args]")
        print("\n可用命令:")
        print("  quote <code>              - 查询股票行情（双平台对比）")
        print("    --source <platform>     - 指定平台 (eastmoney/xueqiu)")
        print("  kline <code> [period]     - 查询K线 (day/week/month/5m/15m/30m/60m)")
        print("  fund <code>               - 查询基金信息")
        print("  estimate <code>           - 查询基金估值")
        print("  search <keyword>          - 搜索基金")
        print("  feed [page]               - 查询基金动态")
        print("  bkzj <type> [key]         - 板块资金流向 (industry/concept/theme/region)")
        print("  hot [type]                - 热门股票 (11=美股, 10=港股)")
        print("  screener                  - 条件选股")
        print("    --pe_max <value>        - 最大市盈率")
        print("    --mcap_min <value>      - 最小市值")
        print("    --pct_min <value>       - 最小涨幅")
        print("\n示例:")
        print("  python dongxue_api.py quote 300058")
        print("  python dongxue_api.py kline 300058 day")
        print("  python dongxue_api.py fund 018957")
        print("  python dongxue_api.py estimate 018957")
        print("  python dongxue_api.py search 中航")
        print("  python dongxue_api.py feed")
        print("  python dongxue_api.py bkzj industry")
        print("  python dongxue_api.py hot")
        print("  python dongxue_api.py screener --pe_max 20")
        sys.exit(1)

    command = sys.argv[1]
    xq = XueqiuAPI()

    if command == 'quote':
        if len(sys.argv) < 3:
            print("请提供股票代码")
            sys.exit(1)
        code = sys.argv[2]
        
        source = None
        if '--source' in sys.argv:
            idx = sys.argv.index('--source')
            if idx + 1 < len(sys.argv):
                source = sys.argv[idx + 1].lower()
        
        if source == 'eastmoney':
            data = EastMoneyAPI.get_stock_quote(code, detail=True)
            format_quote(data, '东方财富')
        elif source == 'xueqiu':
            data = xq.get_stock_quote(code)
            format_quote(data, '雪球')
        else:
            # 双平台对比
            em_data = EastMoneyAPI.get_stock_quote(code, detail=True)
            xq_data = xq.get_stock_quote(code)
            format_quote(em_data, '东方财富')
            format_quote(xq_data, '雪球')

    elif command == 'kline':
        if len(sys.argv) < 3:
            print("请提供股票代码")
            sys.exit(1)
        code = sys.argv[2]
        period = sys.argv[3] if len(sys.argv) > 3 else 'day'
        data = xq.get_kline(code, period)
        format_kline(data)

    elif command == 'fund':
        if len(sys.argv) < 3:
            print("请提供基金代码")
            sys.exit(1)
        code = sys.argv[2]
        data = EastMoneyAPI.get_fund_info(code)
        format_fund_info(data)

    elif command == 'estimate':
        if len(sys.argv) < 3:
            print("请提供基金代码")
            sys.exit(1)
        code = sys.argv[2]
        data = EastMoneyAPI.get_fund_estimate(code)
        format_fund_info(data, '基金估值')

    elif command == 'search':
        if len(sys.argv) < 3:
            print("请提供搜索关键词")
            sys.exit(1)
        keyword = sys.argv[2]
        items = EastMoneyAPI.search_fund(keyword)
        format_fund_search(items)

    elif command == 'feed':
        page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        items, has_next = xq.get_fund_feed(page)
        format_fund_feed(items, has_next)

    elif command == 'bkzj':
        sector_type = sys.argv[2] if len(sys.argv) > 2 else 'industry'
        key_type = sys.argv[3] if len(sys.argv) > 3 else 'today'
        data = EastMoneyAPI.get_sector_fund_flow(sector_type, key_type)
        format_sector_flow(data, key_type)

    elif command == 'hot':
        stock_type = int(sys.argv[2]) if len(sys.argv) > 2 else 11
        items = xq.get_hot_stocks(stock_type)
        format_hot_stocks(items)

    elif command == 'screener':
        pe_max = None
        mcap_min = None
        pct_min = None
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--pe_max' and i + 1 < len(sys.argv):
                pe_max = float(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--mcap_min' and i + 1 < len(sys.argv):
                mcap_min = float(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--pct_min' and i + 1 < len(sys.argv):
                pct_min = float(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        data = xq.get_screener(pe_max, mcap_min, pct_min)
        format_screener(data)

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
