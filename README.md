# 东雪数据查询 Skill

整合东方财富和雪球两大平台API,提供全面的A股市场数据查询。

## 功能

- ✅ 股票实时行情(双平台对比)
- ✅ K线历史数据(雪球提供)
- ✅ 基金信息查询(东方财富)
- ✅ 基金估值(东方财富)
- ✅ 基金动态(雪球)
- ✅ 板块资金流向(东方财富)
- ✅ 热门股票排行(雪球)
- ✅ 条件选股(雪球)

## 安装

无需安装额外依赖,使用Python标准库即可运行。

要求:Python 3.6+

## 使用方法

### 1. 查询股票行情

```bash
# 双平台对比(默认)
python dongxue_api.py quote 300058

# 指定平台
python dongxue_api.py quote 300058 --source eastmoney
python dongxue_api.py quote 300058 --source xueqiu
```

### 2. 查询K线数据

```bash
python dongxue_api.py kline 300058 day
python dongxue_api.py kline 300058 week
python dongxue_api.py kline 300058 month
python dongxue_api.py kline 300058 5m
```

### 3. 查询基金信息

```bash
# 基金净值
python dongxue_api.py fund 018957

# 基金估值
python dongxue_api.py estimate 018957

# 搜索基金
python dongxue_api.py search 中航
```

### 4. 查询基金动态

```bash
python dongxue_api.py feed
```

### 5. 查询板块资金流向

```bash
python dongxue_api.py bkzj industry      # 行业板块
python dongxue_api.py bkzj concept 5day  # 概念板块(5日)
python dongxue_api.py bkzj region        # 地域板块
```

### 6. 查询热门股票

```bash
python dongxue_api.py hot
```

### 7. 条件选股

```bash
# 默认筛选
python dongxue_api.py screener

# 按条件筛选
python dongxue_api.py screener --pe_max 20
python dongxue_api.py screener --pe_max 20 --mcap_min 10000000000
```

## 输出示例

### 双平台行情对比
```
============================================================
【东方财富】
============================================================

  蓝色光标 (300058)
  ──────────────────────────────────────────────────
  当前价:      18.0
  涨跌幅:      4.65%
  涨跌额:      0.8
  成交量:      7,392,313
  成交额:      13,022,534,767.86
  振幅:        8.6%
  换手率:      21.25%
  最高:        18.22
  最低:        16.74
  今开:        16.96
  昨收:        17.2
  市盈率(TTM):  287.64
  市净率:      8.19
  总市值:      646.24 亿
  流通市值:    626.03 亿

============================================================
【雪球】
============================================================

  蓝色光标 (300058)
  ──────────────────────────────────────────────────
  当前价:      18.0
  涨跌幅:      4.65%
  ...
```

## 在 AI 编程工具中使用

### OpenClaw

1. **安装 Skill**
   - 将本仓库上传到 GitHub
   - 在 OpenClaw 对话中发送: `github.com/你的用户名/你的仓库名/skill.md 帮我安装这个技能`
   - OpenClaw 会自动识别并安装此 Skill

2. **使用方式**
   - 在对话中直接提问,例如: "查询蓝色光标的股票行情"
   - OpenClaw 会自动调用 `dongxue_api.py` 执行查询并返回结果

3. **示例对话**
   ```
   用户: 帮我查一下300058的行情
   AI: [自动执行 python dongxue_api.py quote 300058]
   ```

### Claude Code

1. **安装 Skill**
   - 将本仓库克隆到本地
   - 在 Claude Code 中,SKILL.md 文件会被自动识别
   - 确保 SKILL.md 和 dongxue_api.py 在同一目录

2. **使用方式**
   - 在 Claude Code 会话中,使用自然语言请求
   - 例如: "Use the dongxue skill to check stock quote for 300058"
   - Claude Code 会读取 SKILL.md 并执行相应的 Python 命令

3. **示例对话**
   ```
   User: Check the fund estimate for 018957
   Claude: [Executes python dongxue_api.py estimate 018957]
   ```

### Codex CLI

1. **安装 Skill**
   - 将本仓库克隆到本地
   - Codex 会自动识别项目中的 SKILL.md 文件
   - 无需额外配置,确保文件结构完整即可

2. **使用方式**
   - 在 Codex CLI 中直接提问
   - 例如: "查询板块资金流向,行业板块"
   - Codex 会根据 SKILL.md 的描述调用对应命令

3. **示例对话**
   ```
   User: Show me hot stocks
   Codex: [Runs python dongxue_api.py hot]
   ```

## 注意事项

- 无需用户提供Cookie,脚本自动获取
- 请求频率建议控制在每秒1次以内
- 东方财富基金信息接口有访问频率限制,被限流时会返回"网络繁忙"提示,等待15-30分钟后自动恢复
- Windows系统下命令行输出中文可能显示为乱码,但不影响功能正常使用

## 项目结构

```
东雪数据/
├── dongxue_api.py      # 主程序(整合东方财富+雪球)
├── README.md           # 说明文档
├── SKILL.md            # AI工具Skill描述文件
└── test.md             # 测试报告
```

## 技术架构

- **纯Python标准库** - 无需安装第三方依赖
- **双平台整合** - 东方财富 + 雪球
- **统一输出格式** - 美化排版,易于阅读
- **错误处理完善** - 自动检测API限流等异常情况

## 许可证

MIT License
