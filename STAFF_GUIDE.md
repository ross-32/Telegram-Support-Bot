# 👨‍💼 员工使用指南 | Staff Guide

## 🌟 欢迎 | Welcome

本指南帮助客服团队成员高效使用票务中继系统。

This guide helps support team members efficiently use the ticket relay system.

---

## 📋 系统概述 | System Overview

### 工作流程 | Workflow

```
客户群 | Customer Group    →    员工群 | Staff Group
      ↓                              ↓
  客户提问                        收到 Wrapper 工单
  Customer asks                  Receive wrapper ticket
      ↓                              ↓
      ↓                         员工回复 Wrapper
      ↓                         Staff replies to wrapper
      ↓                              ↓
  收到回复 ← ─ ─ ─ ─ ─ ─ ─ ─ ─ 自动转发
  Receive reply              Auto-forwarded
```

### 关键概念 | Key Concepts

- **Wrapper 工单消息 | Wrapper Ticket Message**: 包含工单信息的文本消息
- **Ticket ID**: 唯一的工单编号，格式如 `#1737456789000`
- **Reply 回复**: 必须使用 Telegram 的"回复"功能
- **Anchor 锚点**: 用于追踪同一工单的后续对话

---

## 🎯 核心操作 | Core Operations

### 1️⃣ 接收新工单 | Receive New Ticket

当客户提问时，您会在员工群看到：

When a customer asks a question, you'll see in the staff group:

```
🎫 Ticket #1737456789000
📍 From group: Customer Support Group A
👤 User: @john_doe
──────────────────────────────
How do I reset my password?
```

**Wrapper 消息说明 | Wrapper Message Explanation:**
- 第一行：工单号 | Line 1: Ticket number
- 第二行：来自哪个客户群 | Line 2: Which customer group
- 第三行：哪个用户 | Line 3: Which user
- 分隔线后：客户的问题 | After divider: Customer's question

**如果是媒体消息 | If Media Message:**

Wrapper 下方会有原始图片/文件/视频等（作为回复）。

Original image/file/video will appear below wrapper (as a reply).

### 2️⃣ 回复工单 | Reply to Ticket

**⚠️ 重要：必须回复 Wrapper 消息！**  
**⚠️ Important: Must Reply to Wrapper Message!**

#### 正确方式 | Correct Way ✅

1. 找到包含 `🎫 Ticket #xxx` 的 Wrapper 消息
2. 点击该消息的"回复" | Click "Reply" on that message
3. 输入您的回答 | Type your answer
4. 发送 | Send

```
您的回复 | Your reply:
Hello! To reset your password:
1. Click "Forgot Password" on login page
2. Enter your registered email
3. Check your email for verification code
4. Set new password
```

#### 错误方式 | Wrong Way ❌

- ❌ 直接在群里发消息（不 reply）
- ❌ Sending messages directly in the group (without replying)
- ❌ 回复媒体副本消息（如果有）
- ❌ Reply to media copy message (if any)
- ❌ 回复其他员工的消息
- ❌ Reply to other staff messages

#### 确认成功 | Confirmation

回复发送后，Bot 会确认：

After sending reply, bot will confirm:

```
Bot: ✅ Reply sent to customer group
```

### 3️⃣ 处理续聊消息 | Handle Continued Messages

客户可能在同一工单下继续提问。您会看到：

Customers may continue asking on the same ticket. You'll see:

```
💬 Continued message (Ticket #1737456789000)
👤 @john_doe
────────────────────
I didn't receive the verification email
```

**处理方式 | How to Handle:**

**仍然回复原始的 Wrapper 消息（带 🎫 的那条）！**

**Still reply to the original Wrapper message (the one with 🎫)!**

### 4️⃣ 关闭工单 | Close Ticket

问题解决后，关闭工单：

After issue is resolved, close the ticket:

#### 关闭命令 | Close Commands

回复 Wrapper 消息，发送：

Reply to Wrapper message and send:

```
/close
```

或 | or

```
/done
```

**效果 | Effect:**
- Bot 确认：`✅ Ticket #xxx closed`
- 客户无法继续在该工单下提问
- Customer cannot continue on this ticket
- 如客户回复会提示工单已关闭
- If customer replies, will be notified ticket is closed

### 5️⃣ 重新打开工单 | Reopen Ticket

如需重新打开已关闭的工单：

To reopen a closed ticket:

回复 Wrapper 消息，发送：

Reply to Wrapper message and send:

```
/reopen
```

**效果 | Effect:**
- Bot 确认：`✅ Ticket #xxx reopened`
- 客户可以继续在该工单下对话
- Customer can continue conversation on this ticket

---

## 📝 完整操作示例 | Complete Example

### 场景：处理密码重置问题 | Scenario: Password Reset Issue

**步骤 1：收到工单 | Step 1: Receive Ticket**

```
员工群显示 | Staff group shows:

🎫 Ticket #1737456789000
📍 From group: Customer Support Group
👤 User: @alice
──────────────────────────────
I can't login, forgot my password
```

**步骤 2：回复工单 | Step 2: Reply to Ticket**

```
您（点击回复 Wrapper）| You (reply to wrapper):

Hello! I can help you with that.
To reset your password:
1. Go to https://example.com/reset
2. Enter your email address
3. Check your email for the reset link
4. Click the link and set a new password

Let me know if you need any help!
```

**步骤 3：客户继续提问 | Step 3: Customer Continues**

```
员工群显示 | Staff group shows:

💬 Continued message (Ticket #1737456789000)
👤 @alice
────────────────────
I didn't receive the email
```

**步骤 4：再次回复 | Step 4: Reply Again**

```
您（仍然回复原 Wrapper）| You (still reply to original wrapper):

No problem! Please check:
1. Your spam/junk folder
2. Make sure you entered the correct email

If still not received, I can manually reset it.
What's your registered email?
```

**步骤 5：问题解决，关闭工单 | Step 5: Issue Resolved, Close Ticket**

```
您（回复 Wrapper）| You (reply to wrapper):

/close
```

```
Bot 确认 | Bot confirms:
✅ Ticket #1737456789000 closed
```

---

## 🎨 支持的回复类型 | Supported Reply Types

您可以回复任何类型的内容：

You can reply with any type of content:

✅ **纯文本 | Plain Text**
```
Just type your text answer
```

✅ **图片 + 说明 | Image + Caption**
```
Attach image → Add caption → Send
```

✅ **视频教程 | Video Tutorial**
```
Attach video → Send as reply
```

✅ **文件 | Files**
```
Attach document → Send as reply
```

✅ **语音消息 | Voice Message**
```
Record voice → Send as reply
```

---

## ⚠️ 重要注意事项 | Important Notes

### ✅ 正确操作 | Do's

1. **始终回复 Wrapper** | Always Reply to Wrapper
   - 寻找带 🎫 Ticket #xxx 的消息
   - Look for message with 🎫 Ticket #xxx

2. **及时回复** | Reply Promptly
   - 尽快响应客户问题
   - Respond to customer questions ASAP

3. **使用关闭命令** | Use Close Commands
   - 问题解决后使用 /close
   - Use /close after issue is resolved

4. **保持专业** | Stay Professional
   - 友好、耐心、清晰
   - Friendly, patient, clear

### ❌ 避免错误 | Don'ts

1. **不要直接发消息** | Don't Send Direct Messages
   - ❌ 在群里直接发，不 reply
   - ❌ Send in group without replying

2. **不要回复错误的消息** | Don't Reply to Wrong Message
   - ❌ 回复媒体副本而非 Wrapper
   - ❌ Reply to media copy instead of wrapper

3. **不要忘记关闭** | Don't Forget to Close
   - ❌ 问题解决后不关闭工单
   - ❌ Leave tickets open after resolution

---

## 📊 工单状态管理 | Ticket Status Management

### Open 状态 | Open Status

- 工单活跃，可以继续对话
- Ticket is active, conversation can continue
- 客户可以回复和续聊
- Customer can reply and continue

### Closed 状态 | Closed Status

- 工单已关闭，问题已解决
- Ticket is closed, issue resolved
- 客户回复会收到提示
- Customer reply will get notification
- 可以使用 /reopen 重新打开
- Can use /reopen to reopen

---

## 💡 最佳实践 | Best Practices

### 1. 快速响应 | Quick Response

- 尽量在 5-10 分钟内首次回复
- Try to give first reply within 5-10 minutes
- 如果需要时间调查，告知客户
- If investigation needed, inform customer

### 2. 清晰沟通 | Clear Communication

- 使用简单易懂的语言
- Use simple, clear language
- 分步骤说明解决方案
- Explain solutions step by step
- 必要时提供链接或截图
- Provide links or screenshots when needed

### 3. 完整跟进 | Complete Follow-up

- 确认问题是否真正解决
- Confirm issue is actually resolved
- 询问是否还有其他问题
- Ask if there are other issues
- 然后再关闭工单
- Then close the ticket

### 4. 记录重要信息 | Record Important Info

- 对于复杂问题，在回复中记录关键信息
- For complex issues, record key info in replies
- 方便后续查看工单历史
- Helpful for reviewing ticket history

### 5. 团队协作 | Team Collaboration

- 如果需要其他同事帮助，在 Wrapper 下讨论
- If need colleague's help, discuss under wrapper
- 所有回复都会记录在同一工单下
- All replies are recorded under the same ticket

---

## ❓ 常见问题 | FAQ

### Q1: 如何判断应该回复哪条消息？

**A:** 寻找包含 `🎫 Ticket #xxx` 的消息，那就是 Wrapper，必须回复它。

**A:** Look for message containing `🎫 Ticket #xxx`, that's the wrapper, must reply to it.

### Q2: 客户发了续聊消息，我应该怎么做？

**A:** 仍然回复原始的 Wrapper（带 🎫 的那条），不要回复续聊消息本身。

**A:** Still reply to original wrapper (the one with 🎫), don't reply to continued message itself.

### Q3: 我回复后，Bot 没有确认？

**A:** 检查：
- 是否回复了正确的 Wrapper 消息？
- Are you replying to correct wrapper message?
- Bot 是否在线？
- Is bot online?
- 查看 Bot 日志是否有错误
- Check bot logs for errors

### Q4: 多个工单同时处理会混淆吗？

**A:** 不会！每个工单都有唯一的 Ticket ID，回复对应的 Wrapper 即可。

**A:** No! Each ticket has unique Ticket ID, just reply to corresponding wrapper.

### Q5: 可以由多个员工回复同一工单吗？

**A:** 可以！所有员工都可以回复同一个 Wrapper，客户会收到所有回复。

**A:** Yes! All staff can reply to same wrapper, customer will receive all replies.

### Q6: 如何查看历史工单？

**A:** 在员工群向上滚动查看之前的 Wrapper 消息和回复历史。

**A:** Scroll up in staff group to view previous wrapper messages and reply history.

### Q7: 工单关闭后还能回复吗？

**A:** 可以！回复 Wrapper 并发送 `/reopen` 重新打开工单即可。

**A:** Yes! Reply to wrapper and send `/reopen` to reopen the ticket.

---

## 🔧 故障排查 | Troubleshooting

### 问题：回复后客户没收到 | Issue: Customer Didn't Receive Reply

**检查清单 | Checklist:**
- [ ] 是否回复了 Wrapper 消息（带 🎫 的）？
- [ ] Did you reply to wrapper message (with 🎫)?
- [ ] Bot 是否显示"✅ Reply sent"？
- [ ] Did bot show "✅ Reply sent"?
- [ ] Bot 是否在客户群中？
- [ ] Is bot in customer group?
- [ ] Bot 是否有发送权限？
- [ ] Does bot have send permission?

### 问题：找不到 Wrapper 消息 | Issue: Cannot Find Wrapper Message

**解决方法 | Solution:**
- 向上滚动群消息
- Scroll up group messages
- 搜索 "Ticket #" 关键词
- Search for "Ticket #" keyword
- 检查是否已被删除
- Check if deleted

### 问题：/close 命令无效 | Issue: /close Command Not Working

**检查 | Check:**
- 是否回复了 Wrapper？
- Are you replying to wrapper?
- 命令是否完整（/close 或 /done）？
- Is command complete (/close or /done)?
- 检查 Bot 日志
- Check bot logs

---

## 📞 需要帮助？ | Need Help?

如果遇到任何技术问题：

If you encounter any technical issues:

1. 查看本指南 | Check this guide
2. 联系系统管理员 | Contact system administrator
3. 查看 Bot 运行日志 | Check bot logs

---

