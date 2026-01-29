# 📬 Telegram 票务中继机器人 | Telegram Ticket Relay Bot

一个基于 aiogram 3.x 开发的专业票务系统，用于在多个客户群和员工群之间中继消息，实现高效的客户支持。

A professional ticket system based on aiogram 3.x for relaying messages between multiple customer groups and staff group, enabling efficient customer support.

---

## 🌟 功能特点 | Features

- ✅ **多客户群支持** | **Multiple Customer Groups**: 可同时管理多个客户群 | Manage multiple customer groups simultaneously
- ✅ **票务系统** | **Ticket System**: 自动生成票务ID，追踪每个问题 | Auto-generate ticket IDs, track each issue
- ✅ **全媒体支持** | **Full Media Support**: 文字、图片、视频、文件、语音等所有类型 | Text, images, videos, files, voice, etc.
- ✅ **消息线程** | **Message Threading**: 员工回复自动关联到原问题 | Staff replies auto-link to original questions
- ✅ **用户提及** | **User Mentions**: 回复时自动@原提问用户 | Auto-mention original user in replies
- ✅ **持续对话** | **Continuous Conversation**: 支持同一工单下继续对话 | Continue conversation on same ticket
- ✅ **工单管理** | **Ticket Management**: 关闭/重开工单功能 | Close/reopen ticket functionality
- ✅ **管理员控制** | **Admin Control**: 完善的群组管理功能 | Complete group management
- ✅ **数据持久化** | **Data Persistence**: SQLite数据库存储所有映射关系 | SQLite database stores all mappings
- ✅ **轮询模式** | **Polling Mode**: 无需webhook，部署简单 | No webhook needed, simple deployment
- ✅ **环境变量配置** | **Environment Variables**: 安全的配置管理 | Secure configuration management

---

## 📋 系统要求 | System Requirements

- Python 3.8+
- Telegram Bot Token
- 员工群组 | Staff group
- 至少一个客户群组 | At least one customer group

---

## 🚀 快速开始 | Quick Start

### 1. 安装依赖 | Install Dependencies

```bash
pip install -r requirements.txt
```

包含 | Includes:
- aiogram==3.16.0
- aiohttp==3.10.11
- python-dotenv (可选 | optional)

### 2. 配置环境变量 | Configure Environment Variables

#### 方式 A：使用 .env 文件（推荐）| Method A: Use .env File (Recommended)

创建 `.env` 文件 | Create `.env` file:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
STAFF_GROUP_ID=-1001234567890
ADMIN_USER_ID=123456789
```

然后安装 python-dotenv | Then install python-dotenv:

```bash
pip install python-dotenv
```

#### 方式 B：直接使用环境变量 | Method B: Direct Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export STAFF_GROUP_ID="-1001234567890"
export ADMIN_USER_ID="123456789"
```

#### 如何获取这些信息？ | How to Get These Values?

**📌 获取 Bot Token | Get Bot Token:**
1. 打开 Telegram，搜索 @BotFather | Open Telegram, search @BotFather
2. 发送 `/newbot` 创建新机器人 | Send `/newbot` to create new bot
3. 按提示设置名称和用户名 | Follow prompts to set name and username
4. 复制获得的 Token | Copy the Token you receive

**📌 获取群组ID | Get Group ID:**
1. 将 Bot 添加到群组 | Add bot to group
2. 使用 @userinfobot 或 @getidsbot 在群组中获取群ID | Use @userinfobot or @getidsbot in group to get group ID
3. 群组ID通常是负数 | Group ID is usually negative, format: `-1001234567890`

**📌 获取用户ID | Get User ID:**
1. 打开 @userinfobot 或 @getidsbot | Open @userinfobot or @getidsbot
2. 发送任意消息 | Send any message
3. Bot会返回你的用户ID | Bot will return your user ID
4. 用户ID是正整数 | User ID is positive integer, format: `123456789`

### 3. 关闭隐私模式 ⚠️ | Disable Privacy Mode ⚠️

**这是最重要的一步！Bot需要接收群组所有消息才能检测@提及。**

**This is the most important step! Bot needs to receive all group messages to detect mentions.**

1. 打开 @BotFather | Open @BotFather
2. 选择 `/mybots` → 选择你的Bot | Select `/mybots` → Select your bot
3. 点击 `Bot Settings` | Click `Bot Settings`
4. 点击 `Group Privacy` | Click `Group Privacy`
5. 选择 `Turn Off` （关闭隐私模式）| Select `Turn Off` (disable privacy mode)

### 4. 运行机器人 | Run the Bot

#### 使用 .env 文件 | With .env File

```bash
python bot.py
```

#### 使用环境变量 | With Environment Variables

```bash
TELEGRAM_BOT_TOKEN=xxx STAFF_GROUP_ID=xxx ADMIN_USER_ID=xxx python bot.py
```

看到以下提示说明启动成功 | Success message:

```
INFO - Bot starting: @your_bot_username
INFO - Token is set: yes
INFO - Staff group ID: -1001234567890
INFO - Admin user ID: 123456789
INFO - ⚠️  Important reminders:
INFO -   1. Ensure bot is added to staff group and customer groups
INFO -   2. Disable Privacy Mode in bot settings
...
```

### 5. 添加客户群 | Add Customer Groups

1. 将Bot添加到客户群（给予发送消息权限）| Add bot to customer group (with send message permission)
2. 管理员在客户群中发送命令 | Admin sends command in customer group: `/addgroup`
3. 检查日志确认添加成功 | Check logs to confirm: `Customer group added: ID=xxx, Name=xxx`

---

## 📖 使用指南 | User Guides

我们提供了详细的使用指南：| Detailed user guides available:

- 📘 **[客户使用指南 | Customer Guide](CUSTOMER_GUIDE.md)** - 面向最终用户 | For end users
- 📗 **[员工使用指南 | Staff Guide](STAFF_GUIDE.md)** - 面向客服团队 | For support team

---

## 🔄 工作流程 | Workflow

### 流程图 | Flow Chart

```
客户群 (多个) | Customer Groups (Multiple)
    │
    │  1. 客户提问 | Customer asks
    │     @bot 或 | or /ask
    │
    ├──── 2. Bot转发 ────→  员工群 (1个) | Staff Group (One)
    │     附带票务信息           │
    │     With ticket info       │
    │                            │  3. 员工回复 Wrapper
    │                            │     Staff replies to wrapper
    │
    │←─── 4. Bot转发 ──────────┤
    │     @用户 + 回复            │
    │     Mention user + reply   │
    │
    │  5. 客户收到回复
    │     Customer receives reply
    │     (在原消息下 | Under original message)
    │
    │  6. 客户续聊 (可选)
    │     Customer continues (optional)
    │     回复Bot消息 | Reply to bot message
    │
    ├──── 7. 续聊转发 ────→  员工群
    │                        │
    │                        │  8. 员工关闭工单
    │                        │     Staff closes ticket
    │                        │     /close 或 | or /done
```

### 核心机制 | Core Mechanism

#### Wrapper 工单消息 | Wrapper Ticket Message

员工群会收到包含完整信息的 Wrapper 消息：

Staff group receives wrapper message with complete info:

```
🎫 Ticket #1737456789000
📍 From group: Customer Support Group A
👤 User: @john_doe
──────────────────────────────
How do I reset my password?
```

- 纯文本问题：直接显示在 Wrapper 中 | Plain text: shown directly in wrapper
- 媒体消息：Wrapper 下方作为回复显示原媒体 | Media: shown as reply below wrapper

#### 员工回复规则 | Staff Reply Rules

✅ **必须回复 Wrapper 消息** | **Must reply to wrapper message**  
❌ 不要直接发消息 | Don't send direct messages  
❌ 不要回复媒体副本 | Don't reply to media copy

---

## 🎯 命令说明 | Commands

### 管理员命令 | Admin Commands

仅限配置的 ADMIN_USER_ID 执行 | Only for configured ADMIN_USER_ID

| 命令 Command | 使用场景 Usage | 功能 Function |
|------|---------|------|
| `/addgroup` | 在群组中 In group | 添加当前群为客户群（静默）Add current group as customer group (silent) |
| `/removegroup` | 在群组中 In group | 移除当前客户群 Remove customer group |
| `/listgroups` | 任意位置 Anywhere | 列出所有客户群 List all customer groups |

### 客户命令 | Customer Commands

| 命令 Command | 功能 Function | 示例 Example |
|------|------|------|
| `/ask [内容]` | 提交问题 Submit question | `/ask How to modify order?` |
| `@bot [内容]` | 提及Bot提交问题 Mention bot | `@your_bot Need support` |
| `/t <ticket_id> <内容>` | 续聊指定工单 Continue on ticket | `/t 123456 Follow-up question` |

### 员工命令 | Staff Commands

在员工群回复 Wrapper 消息时使用 | Use when replying to wrapper in staff group

| 命令 Command | 功能 Function |
|------|------|
| `/close` 或 or `/done` | 关闭工单 Close ticket |
| `/reopen` | 重新打开工单 Reopen ticket |

### 通用命令 | General Commands

| 命令 Command | 功能 Function |
|------|------|
| `/start` | 显示使用说明 Show usage instructions |

---

## 📊 数据库结构 | Database Structure

### customer_groups 表 | Table

存储允许的客户群列表 | Stores allowed customer groups

| 字段 Field | 类型 Type | 说明 Description |
|------|------|------|
| group_id | INTEGER | 群组ID（主键）Group ID (Primary Key) |

### tickets 表 | Table

存储票务映射关系 | Stores ticket mappings

| 字段 Field | 类型 Type | 说明 Description |
|------|------|------|
| staff_msg_id | INTEGER | 员工群 Wrapper 消息ID（主键）Staff wrapper message ID (PK) |
| ticket_id | INTEGER | 票务ID Ticket ID |
| cust_group_id | INTEGER | 客户群ID Customer group ID |
| cust_msg_id | INTEGER | 客户消息ID Customer message ID |
| user_id | INTEGER | 用户ID User ID |
| username | TEXT | 用户名 Username |
| customer_anchor_msg_id | INTEGER | 客户群锚点消息ID Customer anchor message ID |
| status | TEXT | 状态 (open/closed) Status (open/closed) |
| closed_at | INTEGER | 关闭时间（毫秒）Closed timestamp (ms) |

---

## 💡 使用场景示例 | Usage Examples

### 场景 1：基础工单流程 | Scenario 1: Basic Ticket Flow

**客户 | Customer:**
```
@support_bot My order #12345 hasn't arrived yet
```

**员工群收到 | Staff Group Receives:**
```
🎫 Ticket #1737456789000
📍 From group: Customer Support
👤 User: @alice
──────────────────────────────
My order #12345 hasn't arrived yet
```

**员工回复 | Staff Replies:**
```
[Reply to wrapper above]
Your order #12345 was shipped yesterday.
Tracking: SF1234567890
Expected: 2-3 days
```

**客户收到 | Customer Receives:**
```
💬 Staff reply (Ticket #1737456789000)
📢 @alice
──────────────────────────────
Your order #12345 was shipped yesterday.
Tracking: SF1234567890
Expected: 2-3 days
```

### 场景 2：持续对话 | Scenario 2: Continued Conversation

**客户回复Bot消息 | Customer Replies to Bot:**
```
[Reply to bot's staff reply message]
Can you help me track it?
```

**员工群收到续聊 | Staff Group Receives Continuation:**
```
💬 Continued message (Ticket #1737456789000)
👤 @alice
────────────────────
Can you help me track it?
```

**员工回复原Wrapper | Staff Replies to Original Wrapper:**
```
[Still reply to the original wrapper with 🎫]
Sure! Track here: https://track.com/SF1234567890
```

### 场景 3：关闭工单 | Scenario 3: Close Ticket

**员工关闭 | Staff Closes:**
```
[Reply to wrapper]
/close
```

**Bot确认 | Bot Confirms:**
```
✅ Ticket #1737456789000 closed
```

**客户尝试续聊 | Customer Tries to Continue:**
```
[Customer replies to bot message]
One more question...

Bot responses:
⚠️ This ticket is closed. Please @bot or /ask to create a new ticket.
```

---

## 🔧 高级配置 | Advanced Configuration

### 修改消息模板 | Modify Message Templates

在 `bot.py` 中找到以下位置修改 | Find and modify in `bot.py`:

**Wrapper 模板 | Wrapper Template:**
```python
wrapper_text = (
    f"🎫 Ticket #{ticket_id}\n"
    f"📍 From group: {message.chat.title}\n"
    f"👤 User: {user_mention}\n"
    f"{'─' * 30}\n"
)
```

**员工回复模板 | Staff Reply Template:**
```python
caption_text = (
    f"💬 Staff reply (Ticket #{ticket['ticket_id']})\n"
    f"📢 {user_mention_link}\n"
    f"{'─' * 30}\n"
)
```

### 日志到文件 | Log to File

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🛡️ 安全建议 | Security Recommendations

1. ✅ 不要将 `.env` 文件提交到版本控制 | Don't commit `.env` to version control
2. ✅ 定期备份 `tickets.db` 数据库 | Regularly backup `tickets.db`
3. ✅ 只给信任的人管理员权限 | Only give admin rights to trusted people
4. ✅ 定期检查客户群列表 | Regularly check customer group list
5. ✅ 为员工群设置合适的权限 | Set appropriate permissions for staff group
6. ✅ 监控Bot日志 | Monitor bot logs
7. ✅ 使用强密码保护服务器 | Use strong passwords for servers

---

## 🚀 部署建议 | Deployment Recommendations

### 本地运行 | Local Run
```bash
python bot.py
```

### 使用 screen（Linux服务器）| Using screen (Linux Server)
```bash
screen -S telegram_bot
python bot.py
# Ctrl+A then D to detach
# screen -r telegram_bot to reattach
```

### 使用 systemd（Linux服务）| Using systemd (Linux Service)

创建 `/etc/systemd/system/telegram-bot.service` | Create service file:
```ini
[Unit]
Description=Telegram Ticket Relay Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot
Environment="TELEGRAM_BOT_TOKEN=your_token"
Environment="STAFF_GROUP_ID=your_staff_group"
Environment="ADMIN_USER_ID=your_admin_id"
ExecStart=/usr/bin/python3 /path/to/bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务 | Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### 使用 Docker | Using Docker

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

CMD ["python", "bot.py"]
```

运行 | Run:
```bash
docker build -t telegram-bot .
docker run -d \
  --name telegram-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e STAFF_GROUP_ID=your_staff_group \
  -e ADMIN_USER_ID=your_admin_id \
  telegram-bot
```

---

## ❓ 常见问题 | FAQ

### Q1: Bot在群组中无法接收@提及？ | Bot Can't Receive Mentions in Group?

**A:** 请确保 | Please ensure:
1. Bot的隐私模式已关闭 | Bot's privacy mode is disabled (@BotFather → Group Privacy → Turn Off)
2. Bot在群组中有发送消息的权限 | Bot has permission to send messages in group
3. 重启Bot后重新测试 | Restart bot and test again

### Q2: 环境变量未设置错误？ | Environment Variable Not Set Error?

**A:** 
```bash
# 方式1：直接运行时设置 | Method 1: Set when running
TELEGRAM_BOT_TOKEN=xxx STAFF_GROUP_ID=xxx ADMIN_USER_ID=xxx python bot.py

# 方式2：使用 .env 文件 | Method 2: Use .env file
# Create .env file with variables, then:
python bot.py
```

### Q3: 员工回复后客户没收到？ | Customer Didn't Receive Staff Reply?

**A:** 检查 | Check:
1. 员工是否回复了 Wrapper 消息（带 🎫 的）| Did staff reply to wrapper (with 🎫)?
2. Bot 是否显示"✅ Reply sent"？ | Did bot show "✅ Reply sent"?
3. Bot在客户群是否有发送权限 | Does bot have send permission in customer group?
4. 查看Bot日志是否有错误 | Check bot logs for errors

### Q4: /addgroup 后没有确认消息？ | No Confirmation After /addgroup?

**A:** 这是正常的！为避免群聊刷屏，成功添加时不显示消息。检查日志确认。

**A:** This is normal! To avoid group spam, no message on success. Check logs to confirm.

### Q5: 如何备份数据？ | How to Backup Data?

**A:** 
```bash
# 备份数据库 | Backup database
cp tickets.db tickets_backup_$(date +%Y%m%d).db

# 定期备份建议 | Regular backup recommendation
# Add to crontab:
0 2 * * * cp /path/to/tickets.db /path/to/backups/tickets_$(date +\%Y\%m\%d).db
```

---

## 📞 技术支持 | Technical Support

如有问题或建议 | For issues or suggestions:

1. 检查本文档的"常见问题"部分 | Check "FAQ" section in this document
2. 阅读使用指南 | Read user guides:
   - [客户使用指南 | Customer Guide](CUSTOMER_GUIDE.md)
   - [员工使用指南 | Staff Guide](STAFF_GUIDE.md)
3. 查看Bot运行日志 | Check bot logs
4. 检查aiogram官方文档 | Check aiogram docs: https://docs.aiogram.dev/

---

## 📄 许可证 | License

本项目仅供学习和个人使用。

This project is for learning and personal use only.

---

## 🔄 更新日志 | Changelog

### v2.0.0 (2026-01-29)
- ✨ 环境变量配置 | Environment variable configuration
- ✨ Wrapper 工单机制 | Wrapper ticket mechanism
- ✨ 持续对话支持 | Continuous conversation support
- ✨ 工单关闭/重开 | Ticket close/reopen
- ✨ 全英文输出 | Full English output
- ✨ 静默添加群组 | Silent group addition
- ✨ 中英文文档 | Bilingual documentation

### v1.0.0 (2026-01-21)
- ✨ 初始版本发布 | Initial release
- ✅ 支持多客户群管理 | Multiple customer groups support
- ✅ 完整的票务系统 | Complete ticket system
- ✅ 支持所有媒体类型 | All media types support
- ✅ 消息线程功能 | Message threading
- ✅ 用户提及功能 | User mention feature

---

## 🎉 感谢使用 | Thank You

**祝使用愉快！** | **Happy using!** 🎉

如有任何问题，请查看日志文件或联系开发者。

For any questions, please check log files or contact the developer.
