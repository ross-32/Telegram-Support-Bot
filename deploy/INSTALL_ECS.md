# Aster Support Bot - ECS Production Deployment Guide
# 阿里云 Telegram 支持机器人 - ECS 生产部署指南

## 📋 Table of Contents | 目录

- [Prerequisites | 前置要求](#prerequisites)
- [Architecture Overview | 架构概览](#architecture-overview)
- [Step-by-Step Installation | 分步安装](#step-by-step-installation)
- [Security Considerations | 安全考虑](#security-considerations)
- [Secret Rotation | 密钥轮换](#secret-rotation)
- [Monitoring & Troubleshooting | 监控与故障排除](#monitoring--troubleshooting)

---

## Prerequisites | 前置要求

### System Requirements | 系统要求

- Alibaba Cloud ECS instance with CentOS 7+ / Ubuntu 18.04+ / Alibaba Cloud Linux
- 阿里云 ECS 实例，系统为 CentOS 7+ / Ubuntu 18.04+ / 阿里云 Linux
- Python 3.8 or higher installed
- 已安装 Python 3.8 或更高版本
- Internet connectivity for Telegram API
- 可访问互联网以连接 Telegram API

### Required Tools | 必需工具

- `jq` - JSON processor | JSON 处理器
- `aliyun-cli` - Alibaba Cloud CLI | 阿里云命令行工具
- `systemd` - Service manager | 服务管理器

### Cloud Resources | 云资源

- KMS/Secrets Manager secret created with bot configuration
- 已创建包含机器人配置的 KMS/Secrets Manager 密钥
- RAM Role with KMS GetSecretValue permission (preferred) OR AccessKey with minimal permissions
- 具有 KMS GetSecretValue 权限的 RAM 角色（推荐）或具有最小权限的 AccessKey

---

## Architecture Overview | 架构概览

```
┌─────────────────────────────────────────────────────┐
│  Alibaba Cloud ECS Instance                         │
│  阿里云 ECS 实例                                     │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │ systemd (runs as root)                     │    │
│  │ systemd (以 root 运行)                     │    │
│  │                                             │    │
│  │  1. ExecStartPre:                          │    │
│  │     fetch-secrets.sh → KMS/Secrets Manager│    │
│  │     获取密钥脚本 → KMS/密钥管理器          │    │
│  │                                             │    │
│  │  2. Writes env file (root:root 600)        │    │
│  │     写入环境变量文件 (root:root 600)       │    │
│  │                                             │    │
│  │  3. ExecStart:                             │    │
│  │     Drops to asterbot user                 │    │
│  │     降权到 asterbot 用户                   │    │
│  │     ┌──────────────────────────────────┐   │    │
│  │     │  bot.py (non-root)               │   │    │
│  │     │  机器人程序 (非root)             │   │    │
│  │     │  - Reads env via python-dotenv   │   │    │
│  │     │  - 通过 python-dotenv 读取环境   │   │    │
│  │     │  - No plaintext secrets in code  │   │    │
│  │     │  - 代码中无明文密钥              │   │    │
│  │     └──────────────────────────────────┘   │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘

Security Layers | 安全层:
✓ Secrets stored in KMS only | 密钥仅存储在 KMS
✓ No secrets in git repository | Git 仓库中无密钥
✓ No secrets in systemd unit | systemd 单元中无密钥
✓ Env file protected (600, root) | 环境变量文件受保护 (600, root)
✓ App runs as non-root user | 应用以非 root 用户运行
✓ Sandboxing enabled | 启用沙箱
```

---

## Step-by-Step Installation | 分步安装

### Step 1: Create Application User | 步骤1：创建应用用户

```bash
# Create non-privileged user for running the bot
# 创建非特权用户以运行机器人
sudo useradd --system --no-create-home --shell /sbin/nologin asterbot

# Verify user created | 验证用户已创建
id asterbot
```

**Expected output | 期望输出:**
```
uid=XXX(asterbot) gid=XXX(asterbot) groups=XXX(asterbot)
```

---

### Step 2: Create Required Directories | 步骤2：创建必需目录

```bash
# Application directory | 应用目录
sudo mkdir -p /opt/aster-support-bot

# Configuration directory | 配置目录
sudo mkdir -p /etc/aster-support-bot

# Log directory | 日志目录
sudo mkdir -p /var/log/aster-support-bot

# Set ownership | 设置所有权
sudo chown asterbot:asterbot /opt/aster-support-bot
sudo chown asterbot:asterbot /var/log/aster-support-bot
sudo chown root:root /etc/aster-support-bot
sudo chmod 755 /etc/aster-support-bot
```

---

### Step 3: Upload Application Code | 步骤3：上传应用代码

```bash
# Option A: Upload from local machine | 选项A：从本地机器上传
# (Run on your local machine | 在本地机器上运行)
scp -r ./bot.py ./requirements.txt ./CUSTOMER_GUIDE.md ./README.md ./STAFF_GUIDE.md \
    user@your-ecs-ip:/tmp/aster-bot/

# Then on ECS | 然后在 ECS 上:
sudo cp -r /tmp/aster-bot/* /opt/aster-support-bot/
sudo chown -R asterbot:asterbot /opt/aster-support-bot

# Option B: Clone from Git | 选项B：从 Git 克隆
sudo -u asterbot git clone https://github.com/ross-32/Telegram-Support-Bot.git /opt/aster-support-bot
```

**IMPORTANT | 重要:**
- Do NOT upload `.env` file (contains secrets) | 不要上传 `.env` 文件（包含密钥）
- Do NOT upload `venv/` directory | 不要上传 `venv/` 目录
- Do NOT upload `tickets.db` (will be created on first run) | 不要上传 `tickets.db`（首次运行时会创建）

---

### Step 4: Install System Dependencies | 步骤4：安装系统依赖

#### Install jq | 安装 jq

```bash
# CentOS/RHEL | CentOS/RHEL
sudo yum install -y jq

# Ubuntu/Debian | Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y jq

# Verify | 验证
jq --version
```

#### Install Alibaba Cloud CLI | 安装阿里云 CLI

```bash
# Download and install | 下载并安装
wget https://aliyuncli.alicdn.com/aliyun-cli-linux-latest-amd64.tgz
tar -xzf aliyun-cli-linux-latest-amd64.tgz
sudo mv aliyun /usr/local/bin/
sudo chmod +x /usr/local/bin/aliyun

# Verify | 验证
aliyun version
```

#### Configure Alibaba Cloud CLI | 配置阿里云 CLI

**Option A: Use RAM Role (RECOMMENDED) | 选项A：使用 RAM 角色（推荐）**

Attach a RAM role to your ECS instance with the following policy:
为您的 ECS 实例附加具有以下策略的 RAM 角色：

```json
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kms:GetSecretValue"
      ],
      "Resource": [
        "acs:kms:cn-hangzhou:*:secret/aster/telegram_support_bot/config"
      ]
    }
  ]
}
```

Then configure CLI to use the role:
然后配置 CLI 使用该角色：

```bash
# Configure to use ECS RAM role | 配置使用 ECS RAM 角色
sudo aliyun configure set \
  --mode EcsRamRole \
  --region cn-hangzhou
```

**Option B: Use AccessKey (NOT RECOMMENDED for production) | 选项B：使用 AccessKey（生产环境不推荐）**

If you must use AccessKey, create a RAM user with minimal permissions:
如果必须使用 AccessKey，请创建具有最小权限的 RAM 用户：

```bash
# WARNING: AccessKey will be stored on disk!
# 警告：AccessKey 将存储在磁盘上！
# Use only for testing or if RAM role is not available
# 仅用于测试或 RAM 角色不可用时使用

sudo aliyun configure \
  --region cn-hangzhou \
  --access-key-id YOUR_ACCESS_KEY_ID \
  --access-key-secret YOUR_ACCESS_KEY_SECRET

# Secure the config file | 保护配置文件
sudo chmod 600 ~/.aliyun/config.json
```

**Minimal RAM Policy for AccessKey | AccessKey 的最小 RAM 策略:**

Same as above - only `kms:GetSecretValue` on the specific secret.
与上面相同 - 仅对特定密钥的 `kms:GetSecretValue` 权限。

---

### Step 5: Create Python Virtual Environment | 步骤5：创建 Python 虚拟环境

```bash
# Switch to application directory | 切换到应用目录
cd /opt/aster-support-bot

# Create virtual environment | 创建虚拟环境
sudo -u asterbot python3 -m venv venv

# Activate and install dependencies | 激活并安装依赖
sudo -u asterbot bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Verify installation | 验证安装
sudo -u asterbot bash -c "source venv/bin/activate && pip list"
```

**Expected packages | 期望的包:**
- aiogram==3.16.0
- aiohttp==3.10.11
- python-dotenv

---

### Step 6: Create KMS Secret | 步骤6：创建 KMS 密钥

**Using Alibaba Cloud Console | 使用阿里云控制台:**

1. Navigate to KMS > Secrets Manager
   导航到 KMS > 密钥管理器
2. Click "Create Secret" | 点击"创建密钥"
3. Secret Name: `aster/telegram_support_bot/config`
   密钥名称：`aster/telegram_support_bot/config`
4. Secret Type: Generic | 密钥类型：通用
5. Secret Value (JSON format) | 密钥值（JSON 格式）:

```json
{
  "TELEGRAM_BOT_TOKEN": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  "STAFF_GROUP_ID": "-1001234567890",
  "ADMIN_USER_ID": "123456789"
}
```

6. Enable automatic rotation if needed | 如需要，启用自动轮换

**Using CLI | 使用 CLI:**

```bash
# Create secret file | 创建密钥文件
cat > /tmp/secret.json <<'EOF'
{
  "TELEGRAM_BOT_TOKEN": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  "STAFF_GROUP_ID": "-1001234567890",
  "ADMIN_USER_ID": "123456789"
}
EOF

# Create secret in KMS | 在 KMS 中创建密钥
aliyun kms CreateSecret \
  --SecretName aster/telegram_support_bot/config \
  --SecretData "$(cat /tmp/secret.json)" \
  --RegionId cn-hangzhou

# Clean up temporary file | 清理临时文件
shred -u /tmp/secret.json
```

---

### Step 7: Install Deployment Files | 步骤7：安装部署文件

```bash
# Install secret fetcher script | 安装密钥获取脚本
sudo install -o root -g root -m 700 \
  /opt/aster-support-bot/deploy/aster-support-bot-fetch-secrets.sh \
  /usr/local/bin/aster-support-bot-fetch-secrets.sh

# Install systemd service | 安装 systemd 服务
sudo install -o root -g root -m 644 \
  /opt/aster-support-bot/deploy/aster-support-bot.service \
  /etc/systemd/system/aster-support-bot.service

# Create placeholder env file | 创建占位环境变量文件
sudo install -o root -g root -m 600 \
  /opt/aster-support-bot/deploy/aster-support-bot.env.template \
  /etc/aster-support-bot/aster-support-bot.env

# NOTE: This file will be overwritten by fetch-secrets.sh on first start
# 注意：此文件将在首次启动时被 fetch-secrets.sh 覆盖
```

---

### Step 8: Configure Service | 步骤8：配置服务

Edit the systemd service if you need to change KMS parameters:
如果需要更改 KMS 参数，编辑 systemd 服务：

```bash
sudo vim /etc/systemd/system/aster-support-bot.service
```

Update these lines if needed:
如需要，更新这些行：

```ini
Environment="KMS_SECRET_NAME=aster/telegram_support_bot/config"
Environment="KMS_REGION_ID=cn-hangzhou"
Environment="KMS_VERSION_ID="
```

---

### Step 9: Start the Service | 步骤9：启动服务

```bash
# Reload systemd daemon | 重新加载 systemd 守护进程
sudo systemctl daemon-reload

# Enable service to start on boot | 启用服务开机自启
sudo systemctl enable aster-support-bot

# Start the service | 启动服务
sudo systemctl start aster-support-bot

# Check status | 检查状态
sudo systemctl status aster-support-bot
```

**Expected output | 期望输出:**
```
● aster-support-bot.service - Aster Telegram Support Bot
   Loaded: loaded (/etc/systemd/system/aster-support-bot.service; enabled)
   Active: active (running) since ...
```

---

### Step 10: Verify and Monitor | 步骤10：验证和监控

```bash
# View real-time logs | 查看实时日志
sudo journalctl -u aster-support-bot -f

# View last 100 lines | 查看最后 100 行
sudo journalctl -u aster-support-bot -n 100

# View logs since today | 查看今天以来的日志
sudo journalctl -u aster-support-bot --since today

# Check if bot is responding | 检查机器人是否响应
# Open Telegram and send /start to your bot
# 打开 Telegram 并向您的机器人发送 /start
```

**Success indicators | 成功指标:**
```
INFO - Bot starting: @your_bot_username
INFO - Token is set: yes
INFO - Staff group ID: -1001234567890
INFO - Admin user ID: 123456789
INFO - Bot启动: @your_bot_username
```

---

## Security Considerations | 安全考虑

### ✓ Implemented Security Measures | 已实施的安全措施

1. **No Plaintext Secrets in Code or Config | 代码或配置中无明文密钥**
   - All secrets stored in KMS/Secrets Manager only
   - 所有密钥仅存储在 KMS/Secrets Manager

2. **Non-Root Execution | 非 Root 执行**
   - Application runs as `asterbot` user with no login shell
   - 应用以 `asterbot` 用户运行，无登录 shell

3. **Minimal Filesystem Access | 最小文件系统访问**
   - `ProtectSystem=strict` - read-only root filesystem
   - `ProtectSystem=strict` - 只读根文件系统
   - Only specific paths writable
   - 仅特定路径可写

4. **Secure Environment File | 安全环境变量文件**
   - `/etc/aster-support-bot/aster-support-bot.env` protected with 600 permissions
   - `/etc/aster-support-bot/aster-support-bot.env` 以 600 权限保护
   - Owned by root:root
   - 所有者为 root:root
   - Regenerated on each service start
   - 每次服务启动时重新生成

5. **Principle of Least Privilege | 最小权限原则**
   - RAM role/AccessKey has only `kms:GetSecretValue` permission
   - RAM 角色/AccessKey 仅具有 `kms:GetSecretValue` 权限
   - Scoped to specific secret ARN
   - 限定于特定密钥 ARN

6. **No Secret Logging | 无密钥日志**
   - Fetch script never prints secrets to stdout/stderr
   - 获取脚本永不将密钥打印到 stdout/stderr

### Additional Hardening (Optional) | 额外加固（可选）

Uncomment these in the systemd service for stricter sandboxing:
在 systemd 服务中取消注释这些以实现更严格的沙箱：

```ini
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true
LockPersonality=true
MemoryDenyWriteExecute=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
```

**Test thoroughly after enabling! | 启用后彻底测试！**

---

## Secret Rotation | 密钥轮换

### When to Rotate | 何时轮换

- Scheduled rotation (e.g., every 90 days) | 定期轮换（例如，每 90 天）
- After security incident | 安全事件后
- Staff member leaves | 员工离职
- Suspected compromise | 怀疑泄露

### Rotation Procedure | 轮换流程

**Step 1: Create new bot token | 步骤1：创建新的机器人 token**

1. Open @BotFather on Telegram
2. Send `/mybots` → Select your bot → "API Token" → "Revoke current token"
3. Copy new token | 复制新 token

**Step 2: Update KMS secret | 步骤2：更新 KMS 密钥**

```bash
# Prepare new secret JSON | 准备新密钥 JSON
cat > /tmp/new_secret.json <<'EOF'
{
  "TELEGRAM_BOT_TOKEN": "NEW_TOKEN_HERE",
  "STAFF_GROUP_ID": "-1001234567890",
  "ADMIN_USER_ID": "123456789"
}
EOF

# Update secret in KMS | 更新 KMS 中的密钥
aliyun kms UpdateSecret \
  --SecretName aster/telegram_support_bot/config \
  --SecretData "$(cat /tmp/new_secret.json)" \
  --RegionId cn-hangzhou

# Clean up | 清理
shred -u /tmp/new_secret.json
```

**Step 3: Restart service | 步骤3：重启服务**

```bash
# Restart will fetch the new secret automatically
# 重启将自动获取新密钥
sudo systemctl restart aster-support-bot

# Verify | 验证
sudo systemctl status aster-support-bot
sudo journalctl -u aster-support-bot -n 50
```

**Step 4: Verify bot works | 步骤4：验证机器人工作**

- Send `/start` to bot on Telegram
- 在 Telegram 上向机器人发送 `/start`
- Confirm it responds correctly
- 确认响应正确

---

## Monitoring & Troubleshooting | 监控与故障排除

### Service Status | 服务状态

```bash
# Check if service is running | 检查服务是否运行
sudo systemctl status aster-support-bot

# Restart service | 重启服务
sudo systemctl restart aster-support-bot

# Stop service | 停止服务
sudo systemctl stop aster-support-bot

# View service configuration | 查看服务配置
sudo systemctl cat aster-support-bot
```

### Logs | 日志

```bash
# Real-time logs | 实时日志
sudo journalctl -u aster-support-bot -f

# Last 100 lines | 最后 100 行
sudo journalctl -u aster-support-bot -n 100

# Logs with timestamps | 带时间戳的日志
sudo journalctl -u aster-support-bot --since "1 hour ago"

# Export logs to file | 导出日志到文件
sudo journalctl -u aster-support-bot --since today > /tmp/bot-logs.txt
```

### Common Issues | 常见问题

#### Issue 1: Service fails to start | 问题1：服务启动失败

**Symptom | 症状:**
```
● aster-support-bot.service - failed
```

**Solution | 解决方案:**

```bash
# Check detailed error | 检查详细错误
sudo journalctl -u aster-support-bot -n 50

# Common causes | 常见原因:
# 1. Missing dependencies | 缺少依赖
sudo -u asterbot bash -c "cd /opt/aster-support-bot && source venv/bin/activate && pip list"

# 2. KMS fetch failed | KMS 获取失败
sudo /usr/local/bin/aster-support-bot-fetch-secrets.sh

# 3. Permission issues | 权限问题
ls -la /etc/aster-support-bot/
ls -la /opt/aster-support-bot/
```

#### Issue 2: Cannot fetch secret from KMS | 问题2：无法从 KMS 获取密钥

**Symptom | 症状:**
```
[ERROR] Failed to fetch secret from KMS
```

**Solution | 解决方案:**

```bash
# Test KMS access manually | 手动测试 KMS 访问
aliyun kms GetSecretValue \
  --SecretName aster/telegram_support_bot/config \
  --RegionId cn-hangzhou

# Check RAM role/policy | 检查 RAM 角色/策略
# Ensure the role has kms:GetSecretValue permission
# 确保角色具有 kms:GetSecretValue 权限

# Check network connectivity | 检查网络连接
ping -c 3 kms.cn-hangzhou.aliyuncs.com
```

#### Issue 3: Bot not responding | 问题3：机器人无响应

**Symptom | 症状:**
Bot doesn't reply to commands on Telegram
机器人在 Telegram 上不回复命令

**Solution | 解决方案:**

```bash
# Check if process is running | 检查进程是否运行
ps aux | grep bot.py

# Check logs for errors | 检查日志中的错误
sudo journalctl -u aster-support-bot -n 200 | grep -i error

# Verify network connectivity | 验证网络连接
curl -I https://api.telegram.org

# Verify token is correct | 验证 token 是否正确
# Check KMS secret has valid token
# 检查 KMS 密钥是否有有效 token
```

---

## Performance Monitoring | 性能监控

### Resource Usage | 资源使用

```bash
# CPU and Memory | CPU 和内存
sudo systemctl status aster-support-bot

# Detailed process info | 详细进程信息
ps aux | grep bot.py

# Monitor in real-time | 实时监控
top -p $(pgrep -f bot.py)
```

### Database | 数据库

```bash
# Check database size | 检查数据库大小
ls -lh /opt/aster-support-bot/tickets.db

# Backup database | 备份数据库
sudo -u asterbot cp /opt/aster-support-bot/tickets.db \
  /opt/aster-support-bot/tickets_backup_$(date +%Y%m%d).db
```

---

## Maintenance | 维护

### Update Bot Code | 更新机器人代码

```bash
# Stop service | 停止服务
sudo systemctl stop aster-support-bot

# Backup current code | 备份当前代码
sudo cp -r /opt/aster-support-bot /opt/aster-support-bot.backup

# Pull new code | 拉取新代码
cd /opt/aster-support-bot
sudo -u asterbot git pull

# Update dependencies | 更新依赖
sudo -u asterbot bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Start service | 启动服务
sudo systemctl start aster-support-bot

# Verify | 验证
sudo journalctl -u aster-support-bot -f
```

### Backup & Restore | 备份与恢复

```bash
# Backup | 备份
sudo tar czf /backup/aster-support-bot-$(date +%Y%m%d).tar.gz \
  /opt/aster-support-bot/tickets.db \
  /etc/aster-support-bot/

# Restore | 恢复
sudo tar xzf /backup/aster-support-bot-YYYYMMDD.tar.gz -C /
sudo systemctl restart aster-support-bot
```

---

## Uninstallation | 卸载

```bash
# Stop and disable service | 停止并禁用服务
sudo systemctl stop aster-support-bot
sudo systemctl disable aster-support-bot

# Remove service file | 移除服务文件
sudo rm /etc/systemd/system/aster-support-bot.service

# Remove script | 移除脚本
sudo rm /usr/local/bin/aster-support-bot-fetch-secrets.sh

# Remove application files | 移除应用文件
sudo rm -rf /opt/aster-support-bot

# Remove configuration | 移除配置
sudo rm -rf /etc/aster-support-bot

# Remove logs | 移除日志
sudo rm -rf /var/log/aster-support-bot

# Remove user | 移除用户
sudo userdel asterbot

# Reload systemd | 重新加载 systemd
sudo systemctl daemon-reload
```

---

## Security Checklist | 安全检查清单

Before going to production, verify:
投入生产前，验证：

- [ ] Secrets stored only in KMS/Secrets Manager | 密钥仅存储在 KMS/Secrets Manager
- [ ] No secrets in git repository | Git 仓库中无密钥
- [ ] No secrets in systemd service file | systemd 服务文件中无密钥
- [ ] Environment file has 600 permissions | 环境变量文件具有 600 权限
- [ ] Environment file owned by root:root | 环境变量文件所有者为 root:root
- [ ] Bot runs as non-root user | 机器人以非 root 用户运行
- [ ] RAM role uses least privilege principle | RAM 角色使用最小权限原则
- [ ] Security hardening options reviewed | 已审查安全加固选项
- [ ] Logs don't contain secrets | 日志不包含密钥
- [ ] Backup strategy defined | 已定义备份策略
- [ ] Monitoring alerts configured | 已配置监控警报

---

## Support | 支持

For issues or questions:
如有问题或疑问：

- GitHub: https://github.com/ross-32/Telegram-Support-Bot/issues
- Documentation: See README.md, CUSTOMER_GUIDE.md, STAFF_GUIDE.md
- 文档：查看 README.md、CUSTOMER_GUIDE.md、STAFF_GUIDE.md

---

**Production deployment complete! | 生产部署完成！** 🚀
