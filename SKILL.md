---
name: dongxue
description: 查询中国股票市场数据，整合东方财富和雪球两大平台。支持股票行情、K线历史、基金信息、板块资金流向、热门排行、条件选股等。Use when querying Chinese stock market data from EastMoney and Xueqiu APIs.
---

# 东雪数据查询

整合东方财富和雪球两大平台API，提供全面的A股市场数据查询。

## 功能

- **股票实时行情** - 东方财富+雪球双源数据对比
- **K线历史数据** - 雪球提供（日K/周K/月K/分钟K）
- **基金信息** - 东方财富提供（净值/估值/搜索）
- **基金动态** - 雪球提供（用户动态/观点）
- **板块资金流向** - 东方财富提供（行业/概念/地域）
- **热门股票** - 雪球提供（A股/港股/美股排行）
- **条件选股** - 雪球提供（按市盈率/市值/涨跌幅筛选）

## 使用方法

### 1. 查询股票行情

```bash
# 双平台对比
python dongxue_api.py quote 300058

# 指定平台
python dongxue_api.py quote 300058 --source eastmoney
python dongxue_api.py quote 300058 --source xueqiu
```

### 2. 查询K线数据（雪球）

```bash
python dongxue_api.py kline 300058 day
python dongxue_api.py kline 300058 week
python dongxue_api.py kline 300058 month
```

### 3. 查询基金信息（东方财富）

```bash
# 基金净值
python dongxue_api.py fund 018957

# 基金估值
python dongxue_api.py estimate 018957

# 搜索基金
python dongxue_api.py search 中航
```

### 4. 查询基金动态（雪球）

```bash
python dongxue_api.py feed
```

### 5. 查询板块资金流向（东方财富）

```bash
python dongxue_api.py bkzj industry
python dongxue_api.py bkzj concept 5day
```

### 6. 查询热门股票（雪球）

```bash
python dongxue_api.py hot
```

### 7. 条件选股（雪球）

```bash
python dongxue_api.py screener --pe_max 20
```
