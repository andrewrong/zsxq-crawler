# 知识星球内容爬虫

一个用于爬取知识星球内容并自动转发到 Telegram 的爬虫工具。支持多群组管理、定时爬取、内容格式化等功能。

## 功能特点

- 支持多群组配置和管理
- 自动爬取知识星球内容（首页和精华）
- 定时任务调度
- Telegram 消息推送
- 支持图片和文件转发
- 完整的错误处理和日志记录
- 状态持久化

## 环境要求

- Python 3.8+
- 知识星球账号 Cookie
- Telegram Bot Token
- Telegram Chat ID

## 安装

1. 克隆仓库：
```bash
git clone <repository-url>
cd <repository-name>
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

1. 创建 `.env` 文件并设置必要的环境变量：

```ini
# Telegram 配置
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 知识星球配置
ZSXQ_COOKIE=your_cookie

# 群组配置（JSON 格式）
ZSXQ_GROUPS={
    "group_id1": {
        "is_crawl_home": true,
        "thread_ids": {
            "home": "thread_id1",
            "digest": "thread_id2"
        }
    },
    "group_id2": {
        "is_crawl_home": false,
        "thread_ids": {
            "home": "thread_id3",
            "digest": "thread_id4"
        }
    }
}

# 爬取间隔（分钟）
CRAWL_INTERVAL_MINUTES=60
```

### 配置说明

- `TELEGRAM_BOT_TOKEN`: Telegram 机器人 token
- `TELEGRAM_CHAT_ID`: Telegram 聊天 ID
- `ZSXQ_COOKIE`: 知识星球登录 cookie
- `ZSXQ_GROUPS`: 群组配置（JSON 格式）
  - `group_id`: 知识星球群组 ID
  - `is_crawl_home`: 是否爬取首页内容
  - `thread_ids`: 不同内容类型的线程 ID
    - `home`: 首页内容线程 ID
    - `digest`: 精华内容线程 ID
- `CRAWL_INTERVAL_MINUTES`: 爬取间隔（分钟）

## 使用方法

1. 运行爬虫：
```bash
python crawl.py
```

2. 运行定时调度器：
```bash
python run_scheduler.py
```

## 项目结构

```
.
├── README.md
├── requirements.txt
├── config.py
├── crawl.py
├── run_scheduler.py
└── src/
    ├── crawlers/
    │   └── zsxq_crawler.py
    ├── formatters/
    │   └── message_formatter.py
    ├── notifiers/
    │   └── telegram_notifier.py
    ├── scheduler/
    │   └── crawl_scheduler.py
    └── utils/
        └── group_config.py
```

## 主要模块说明

- `crawl.py`: 主爬虫脚本
- `run_scheduler.py`: 定时调度器入口
- `config.py`: 配置管理
- `src/crawlers/`: 爬虫实现
- `src/formatters/`: 消息格式化
- `src/notifiers/`: 消息通知
- `src/scheduler/`: 定时调度
- `src/utils/`: 工具类

## 注意事项

1. Cookie 安全
   - 请妥善保管您的知识星球 Cookie
   - 不要将包含 Cookie 的配置文件提交到版本控制系统

2. 爬取频率
   - 建议设置合理的爬取间隔，避免频繁请求
   - 默认间隔为 60 分钟

3. Telegram 限制
   - 注意 Telegram API 的调用频率限制
   - 大量消息发送可能需要适当延时

## 错误处理

- 所有错误都会被记录到日志
- 重要错误会通过 Telegram 通知
- 程序会自动重试失败的请求

## 日志

- 日志格式：`%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- 日志级别：INFO
- 输出：标准输出

## 贡献

欢迎提交 Issue 和 Pull Request

## 许可证

MIT License 