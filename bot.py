#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Ticket Relay Bot (Wrapper + Continuous Chat + Close Ticket)
Using aiogram 3.x
Features: Forward customer messages to staff group, auto-reply with wrapper mechanism,
          support continuous conversation, close/reopen tickets
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
import sqlite3
import time
import re
import os
from typing import Optional

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

# ======================== Configuration (Environment Variables) ========================
# Required environment variables:
#   TELEGRAM_BOT_TOKEN - Your bot token from @BotFather
#   STAFF_GROUP_ID - Staff group ID (negative integer for groups)
#   ADMIN_USER_ID - Admin's Telegram user ID (positive integer)
#
# Example usage:
#   TELEGRAM_BOT_TOKEN=123456:ABC-DEF... STAFF_GROUP_ID=-1001234567890 ADMIN_USER_ID=123456789 python bot.py
# =======================================================================================

def get_env_config():
    """Load and validate configuration from environment variables"""
    # Get API_TOKEN
    api_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not api_token:
        raise ValueError("Environment variable TELEGRAM_BOT_TOKEN is required but not set")
    
    # Get STAFF_GROUP_ID
    staff_group_id_str = os.getenv('STAFF_GROUP_ID')
    if not staff_group_id_str:
        raise ValueError("Environment variable STAFF_GROUP_ID is required but not set")
    
    try:
        staff_group_id = int(staff_group_id_str)
    except ValueError:
        raise ValueError(f"STAFF_GROUP_ID must be a valid integer, got: {staff_group_id_str}")
    
    # Get ADMIN_USER_ID
    admin_user_id_str = os.getenv('ADMIN_USER_ID')
    if not admin_user_id_str:
        raise ValueError("Environment variable ADMIN_USER_ID is required but not set")
    
    try:
        admin_user_id = int(admin_user_id_str)
    except ValueError:
        raise ValueError(f"ADMIN_USER_ID must be a valid integer, got: {admin_user_id_str}")
    
    return api_token, staff_group_id, admin_user_id


# Load configuration
API_TOKEN, STAFF_GROUP_ID, ADMIN_USER_ID = get_env_config()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database filename
DB_NAME = 'tickets.db'


# ======================== Database Operations ========================

def check_and_migrate_db():
    """Check and migrate database (idempotent operation)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Check if tickets table has status and closed_at fields
    cursor.execute("PRAGMA table_info(tickets)")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Add status field if not exists
    if 'status' not in columns:
        logger.info("Migration: Adding status column")
        cursor.execute("ALTER TABLE tickets ADD COLUMN status TEXT NOT NULL DEFAULT 'open'")
        conn.commit()
    
    # Add closed_at field if not exists
    if 'closed_at' not in columns:
        logger.info("Migration: Adding closed_at column")
        cursor.execute("ALTER TABLE tickets ADD COLUMN closed_at INTEGER DEFAULT NULL")
        conn.commit()
    
    conn.close()
    logger.info("Database migration check completed")


def init_db():
    """Initialize database and create necessary tables"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create customer groups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_groups (
            group_id INTEGER PRIMARY KEY
        )
    ''')
    
    # Create tickets mapping table (with status and closed_at)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            staff_msg_id INTEGER PRIMARY KEY,
            ticket_id INTEGER NOT NULL,
            cust_group_id INTEGER,
            cust_msg_id INTEGER,
            user_id INTEGER,
            username TEXT,
            customer_anchor_msg_id INTEGER,
            status TEXT NOT NULL DEFAULT 'open',
            closed_at INTEGER DEFAULT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialization completed")
    
    # Execute migration check (for existing tables)
    check_and_migrate_db()


def is_customer_group(group_id: int) -> bool:
    """Check if group is in customer groups list"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT group_id FROM customer_groups WHERE group_id = ?', (group_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def add_customer_group(group_id: int) -> bool:
    """Add customer group"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO customer_groups (group_id) VALUES (?)', (group_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to add customer group: {e}")
        return False


def remove_customer_group(group_id: int) -> bool:
    """Remove customer group"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM customer_groups WHERE group_id = ?', (group_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to remove customer group: {e}")
        return False


def get_all_customer_groups() -> list:
    """Get all customer group IDs"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT group_id FROM customer_groups')
    groups = [row[0] for row in cursor.fetchall()]
    conn.close()
    return groups


def save_ticket(staff_msg_id: int, ticket_id: int, cust_group_id: int, 
                cust_msg_id: int, user_id: int, username: str):
    """Save ticket mapping (staff_msg_id is wrapper message ID)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO tickets 
        (staff_msg_id, ticket_id, cust_group_id, cust_msg_id, user_id, username, 
         customer_anchor_msg_id, status, closed_at)
        VALUES (?, ?, ?, ?, ?, ?, NULL, 'open', NULL)
    ''', (staff_msg_id, ticket_id, cust_group_id, cust_msg_id, user_id, username))
    conn.commit()
    conn.close()


def get_ticket(staff_msg_id: int) -> Optional[dict]:
    """Get ticket info by staff group wrapper message ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT staff_msg_id, ticket_id, cust_group_id, cust_msg_id, user_id, username, 
               customer_anchor_msg_id, status, closed_at
        FROM tickets 
        WHERE staff_msg_id = ?
    ''', (staff_msg_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'staff_msg_id': result[0],
            'ticket_id': result[1],
            'cust_group_id': result[2],
            'cust_msg_id': result[3],
            'user_id': result[4],
            'username': result[5],
            'customer_anchor_msg_id': result[6],
            'status': result[7],
            'closed_at': result[8]
        }
    return None


def get_ticket_by_customer_anchor(chat_id: int, anchor_msg_id: int) -> Optional[dict]:
    """Get ticket info by customer group anchor message ID (for continued conversation)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT staff_msg_id, ticket_id, cust_group_id, cust_msg_id, user_id, username, 
               customer_anchor_msg_id, status, closed_at
        FROM tickets 
        WHERE cust_group_id = ? AND customer_anchor_msg_id = ?
    ''', (chat_id, anchor_msg_id))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'staff_msg_id': result[0],
            'ticket_id': result[1],
            'cust_group_id': result[2],
            'cust_msg_id': result[3],
            'user_id': result[4],
            'username': result[5],
            'customer_anchor_msg_id': result[6],
            'status': result[7],
            'closed_at': result[8]
        }
    return None


def get_ticket_by_id(ticket_id: int) -> Optional[dict]:
    """Get ticket info by ticket_id (for /t command)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT staff_msg_id, ticket_id, cust_group_id, cust_msg_id, user_id, username, 
               customer_anchor_msg_id, status, closed_at
        FROM tickets 
        WHERE ticket_id = ?
    ''', (ticket_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'staff_msg_id': result[0],
            'ticket_id': result[1],
            'cust_group_id': result[2],
            'cust_msg_id': result[3],
            'user_id': result[4],
            'username': result[5],
            'customer_anchor_msg_id': result[6],
            'status': result[7],
            'closed_at': result[8]
        }
    return None


def update_customer_anchor(staff_msg_id: int, customer_anchor_msg_id: int):
    """Update customer group anchor message ID (called after staff reply)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tickets 
        SET customer_anchor_msg_id = ?
        WHERE staff_msg_id = ?
    ''', (customer_anchor_msg_id, staff_msg_id))
    conn.commit()
    conn.close()


def close_ticket_by_staff_msg_id(staff_msg_id: int) -> bool:
    """Close ticket (by staff group wrapper message ID)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        closed_at = int(time.time() * 1000)
        cursor.execute('''
            UPDATE tickets 
            SET status = 'closed', closed_at = ?
            WHERE staff_msg_id = ?
        ''', (closed_at, staff_msg_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to close ticket: {e}")
        return False


def reopen_ticket_by_staff_msg_id(staff_msg_id: int) -> bool:
    """Reopen ticket (by staff group wrapper message ID)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tickets 
            SET status = 'open', closed_at = NULL
            WHERE staff_msg_id = ?
        ''', (staff_msg_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to reopen ticket: {e}")
        return False


# ======================== Bot Initialization ========================

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# ======================== General Command Handlers ========================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command, show usage instructions"""
    help_text = (
        "👋 Welcome to the Ticket Relay Bot!\n\n"
        "📌 **Customer Usage** (in configured customer groups):\n"
        "• Method 1: @bot_username + your question\n"
        "• Method 2: /ask + your question\n"
        "• Supports text, images, videos, files, voice, etc.\n\n"
        "💬 **Continue Conversation**:\n"
        "• Reply to bot's staff reply message\n"
        "• Or use command: /t <ticket_id> <content>\n\n"
        "📌 **Admin Commands** (admin only):\n"
        "• /addgroup - Add current group as customer group\n"
        "• /removegroup - Remove current group\n"
        "• /listgroups - List all customer groups\n\n"
        "📌 **Staff Reply Method** (in staff group):\n"
        "• Use Reply function on the wrapper ticket message\n"
        "• Support replying with any content type\n"
        "• System will auto-forward to customer and mention original user\n\n"
        "🔒 **Close Ticket** (staff group):\n"
        "• Reply to wrapper and send /close or /done to close ticket\n"
        "• Reply to wrapper and send /reopen to reopen ticket\n\n"
        "💡 Need help? Contact administrator"
    )
    await message.reply(help_text, parse_mode=ParseMode.MARKDOWN)


# ======================== Admin Command Handlers ========================

@dp.message(Command("addgroup"))
async def cmd_addgroup(message: Message):
    """Add current group as customer group (admin only, silent in groups)"""
    # Check if admin
    if message.from_user.id != ADMIN_USER_ID:
        return
    
    # Must be executed in group
    if message.chat.type not in ['group', 'supergroup']:
        await message.reply("❌ This command can only be used in groups")
        return
    
    group_id = message.chat.id
    group_name = message.chat.title or "Unknown"
    
    if add_customer_group(group_id):
        # Silent mode: log only, no message to group to avoid spam
        logger.info(f"Customer group added: ID={group_id}, Name={group_name}")
        # No reply to avoid group spam
    else:
        # Only reply on error
        await message.reply("❌ Failed to add group, please check logs")


@dp.message(Command("removegroup"))
async def cmd_removegroup(message: Message):
    """Remove current group (admin only)"""
    if message.from_user.id != ADMIN_USER_ID:
        return
    
    if message.chat.type not in ['group', 'supergroup']:
        await message.reply("❌ This command can only be used in groups")
        return
    
    group_id = message.chat.id
    
    if remove_customer_group(group_id):
        await message.reply(f"✅ Successfully removed customer group\nGroup ID: {group_id}")
        logger.info(f"Removed customer group: {group_id}")
    else:
        await message.reply("❌ Failed to remove group, please check logs")


@dp.message(Command("listgroups"))
async def cmd_listgroups(message: Message):
    """List all customer groups (admin only)"""
    if message.from_user.id != ADMIN_USER_ID:
        return
    
    groups = get_all_customer_groups()
    
    if not groups:
        await message.reply("📋 No customer groups")
        return
    
    group_list = "\n".join([f"• {group_id}" for group_id in groups])
    await message.reply(
        f"📋 Customer Groups ({len(groups)} total):\n\n{group_list}"
    )


# ======================== Continue Conversation Command Handler ========================

@dp.message(Command("t", "ticket"))
async def cmd_ticket_continue(message: Message):
    """Handle /t or /ticket command (continue conversation on specified ticket)"""
    # Must be in customer group
    if message.chat.type not in ['group', 'supergroup']:
        return
    
    if not is_customer_group(message.chat.id):
        return
    
    # Parse command: /t <ticket_id> <content>
    text = message.text
    parts = text.split(maxsplit=2)
    
    if len(parts) < 3:
        await message.reply("❌ Invalid format\nCorrect format: /t <ticket_id> <content>")
        return
    
    try:
        ticket_id = int(parts[1])
    except ValueError:
        await message.reply("❌ Ticket ID must be a number")
        return
    
    content = parts[2]
    
    # Find ticket
    ticket = get_ticket_by_id(ticket_id)
    
    if not ticket:
        await message.reply("❌ Ticket does not exist")
        return
    
    # Check if same customer group
    if ticket['cust_group_id'] != message.chat.id:
        await message.reply("❌ This ticket does not belong to current group")
        return
    
    # Check if ticket is closed
    if ticket['status'] == 'closed':
        await message.reply(
            "⚠️ This ticket is closed. Please @bot or /ask to create a new ticket."
        )
        return
    
    # Forward continued message to staff group
    await forward_continue_message_to_staff(message, ticket, content, is_text_only=True)


# ======================== Customer Question Handlers ========================

async def check_bot_mentioned(message: Message, bot_username: str) -> bool:
    """Check if message mentions the bot"""
    # Check /ask command
    if message.text and message.text.startswith('/ask'):
        return True
    
    # Check message entities for bot mention
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                # Extract mentioned username
                if message.text:
                    mention_text = message.text[entity.offset:entity.offset + entity.length]
                    if f"@{bot_username}" == mention_text:
                        return True
    
    # Check if text contains @bot_username (compatibility)
    if message.text and f"@{bot_username}" in message.text:
        return True
    
    # Check caption for bot mention
    if message.caption:
        if f"@{bot_username}" in message.caption:
            return True
        # Check caption_entities
        if message.caption_entities:
            for entity in message.caption_entities:
                if entity.type == "mention":
                    mention_text = message.caption[entity.offset:entity.offset + entity.length]
                    if f"@{bot_username}" == mention_text:
                        return True
    
    return False


async def forward_to_staff(message: Message):
    """
    Forward customer message to staff group (Wrapper mechanism)
    First send wrapper ticket message, then copy original message as reply based on content type
    """
    try:
        # Generate ticket ID (using timestamp)
        ticket_id = int(time.time() * 1000)
        
        # Get user info
        user = message.from_user
        username = user.username or user.full_name
        user_mention = f"@{user.username}" if user.username else user.full_name
        
        # Get message content type
        content_type = message.content_type
        
        # Build wrapper text
        wrapper_text = (
            f"🎫 Ticket #{ticket_id}\n"
            f"📍 From group: {message.chat.title}\n"
            f"👤 User: {user_mention}\n"
            f"{'─' * 30}\n"
        )
        
        # Add content summary or full text based on content type
        if content_type == 'text':
            # Plain text message: include full content in wrapper
            wrapper_text += message.text
            
        elif content_type == 'photo':
            # Photo message
            if message.caption:
                wrapper_text += f"📷 Photo attachment\nCaption: {message.caption}"
            else:
                wrapper_text += "📷 Photo attachment"
                
        elif content_type == 'video':
            # Video message
            if message.caption:
                wrapper_text += f"🎬 Video attachment\nCaption: {message.caption}"
            else:
                wrapper_text += "🎬 Video attachment"
                
        elif content_type == 'document':
            # Document message
            file_name = message.document.file_name if message.document.file_name else "Unnamed file"
            if message.caption:
                wrapper_text += f"📎 File attachment: {file_name}\nCaption: {message.caption}"
            else:
                wrapper_text += f"📎 File attachment: {file_name}"
                
        elif content_type == 'voice':
            # Voice message
            duration = message.voice.duration if message.voice.duration else 0
            wrapper_text += f"🎤 Voice message ({duration}s)"
            
        elif content_type == 'audio':
            # Audio message
            if message.audio.title:
                wrapper_text += f"🎵 Audio: {message.audio.title}"
            else:
                wrapper_text += "🎵 Audio attachment"
                
        elif content_type == 'video_note':
            # Video note (circular)
            wrapper_text += "🎥 Video message"
            
        elif content_type == 'sticker':
            # Sticker
            wrapper_text += f"🎭 Sticker: {message.sticker.emoji if message.sticker.emoji else ''}"
            
        elif content_type == 'animation':
            # GIF animation
            wrapper_text += "🎞️ GIF animation"
            
        else:
            # Other types
            wrapper_text += f"📦 {content_type} type message"
        
        # 1. First send wrapper message to staff group
        wrapper_msg = await bot.send_message(STAFF_GROUP_ID, wrapper_text)
        
        # 2. If not plain text, copy original message as reply under wrapper
        if content_type != 'text':
            try:
                await bot.copy_message(
                    chat_id=STAFF_GROUP_ID,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                    reply_to_message_id=wrapper_msg.message_id
                )
            except Exception as e:
                logger.warning(f"Failed to copy media message: {e}")
                # Even if copy fails, wrapper contains basic info
        
        # 3. Save ticket mapping (using wrapper message_id)
        save_ticket(
            staff_msg_id=wrapper_msg.message_id,
            ticket_id=ticket_id,
            cust_group_id=message.chat.id,
            cust_msg_id=message.message_id,
            user_id=user.id,
            username=username
        )
        
        # 4. No success confirmation to customer group (stay silent)
        # Removed customer reply to avoid spam
        
        logger.info(f"Created ticket #{ticket_id}: user {username} (group {message.chat.id}), type {content_type}")
        
    except Exception as e:
        logger.error(f"Failed to forward message to staff group: {e}", exc_info=True)
        # Only send error message to customer on exception
        await message.reply("❌ System error, please try again later")


async def forward_continue_message_to_staff(message: Message, ticket: dict, 
                                            text_content: str = None, is_text_only: bool = False):
    """
    Forward customer continued message to staff group (as reply under corresponding wrapper)
    
    Args:
        message: Customer message object
        ticket: Ticket info dictionary
        text_content: Plain text content (for /t command)
        is_text_only: Whether text only (for /t command)
    """
    try:
        # Get user info
        user = message.from_user
        username = user.username or user.full_name
        user_mention = f"@{user.username}" if user.username else user.full_name
        
        # Build continued message header (short version)
        continue_header = (
            f"💬 Continued message (Ticket #{ticket['ticket_id']})\n"
            f"👤 {user_mention}\n"
            f"{'─' * 20}\n"
        )
        
        if is_text_only:
            # /t command: plain text continuation
            full_text = continue_header + text_content
            await bot.send_message(
                STAFF_GROUP_ID,
                full_text,
                reply_to_message_id=ticket['staff_msg_id']
            )
        else:
            # Reply continuation: support text and media
            content_type = message.content_type
            
            if content_type == 'text':
                # Plain text continuation
                full_text = continue_header + message.text
                await bot.send_message(
                    STAFF_GROUP_ID,
                    full_text,
                    reply_to_message_id=ticket['staff_msg_id']
                )
            else:
                # Media continuation: send header first, then copy media
                await bot.send_message(
                    STAFF_GROUP_ID,
                    continue_header,
                    reply_to_message_id=ticket['staff_msg_id']
                )
                await bot.copy_message(
                    chat_id=STAFF_GROUP_ID,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                    reply_to_message_id=ticket['staff_msg_id']
                )
        
        logger.info(f"Forwarded continued message: Ticket #{ticket['ticket_id']}, user {username}")
        
    except Exception as e:
        logger.error(f"Failed to forward continued message: {e}", exc_info=True)
        await message.reply("❌ Failed to forward continued message")


async def check_and_handle_continue_message(message: Message) -> bool:
    """
    Check and handle continued message
    
    Returns:
        bool: True if continued message, False otherwise
    """
    # Ignore bot's own messages
    if message.from_user.is_bot:
        return False
    
    # Check if reply message
    if not message.reply_to_message:
        return False
    
    # Check if replying to bot message
    if not message.reply_to_message.from_user.is_bot:
        return False
    
    # Try to extract ticket_id from replied message
    reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
    
    # Match "Ticket #<number>"
    match = re.search(r'Ticket #(\d+)', reply_text)
    
    if not match:
        return False
    
    # Find ticket by anchor message ID
    anchor_msg_id = message.reply_to_message.message_id
    ticket = get_ticket_by_customer_anchor(message.chat.id, anchor_msg_id)
    
    if not ticket:
        # Cannot find corresponding ticket
        bot_info = await bot.get_me()
        await message.reply(
            "❌ Ticket not found\n"
            f"Please use /t <ticket_id> <content> or @{bot_info.username} to ask again"
        )
        return True  # Intent to continue conversation, even if not found
    
    # Check if ticket is closed
    if ticket['status'] == 'closed':
        bot_info = await bot.get_me()
        await message.reply(
            "⚠️ This ticket is closed. Please @bot or /ask to create a new ticket."
        )
        return True
    
    # Found ticket and not closed, forward continued message
    await forward_continue_message_to_staff(message, ticket)
    
    return True


# ======================== Staff Reply Handler ========================

@dp.message(F.chat.id == STAFF_GROUP_ID)
async def handle_staff_reply(message: Message):
    """Handle staff group replies (must reply to wrapper message)"""
    # Detailed log: confirm trigger and mapping key
    logger.info(
        f"Received staff reply: chat={message.chat.id}, "
        f"msg_id={message.message_id}, "
        f"reply_to={message.reply_to_message.message_id if message.reply_to_message else None}, "
        f"from={message.from_user.id}"
    )
    
    # Must be reply message
    if not message.reply_to_message:
        logger.debug("Staff message is not a reply, skipping")
        return
    
    # Get replied message ID (should be wrapper message_id)
    wrapper_msg_id = message.reply_to_message.message_id
    
    # Query ticket info
    ticket = get_ticket(wrapper_msg_id)
    
    if not ticket:
        logger.debug(f"Message {wrapper_msg_id} is not a wrapper ticket message")
        return
    
    logger.info(
        f"Found ticket mapping: ticket_id={ticket['ticket_id']}, "
        f"cust_group={ticket['cust_group_id']}, "
        f"cust_msg={ticket['cust_msg_id']}, "
        f"status={ticket['status']}"
    )
    
    # Check if close command
    if message.text:
        text_lower = message.text.lower().strip()
        
        # /close or /done command: close ticket
        if text_lower in ['/close', '/done']:
            if close_ticket_by_staff_msg_id(wrapper_msg_id):
                await message.reply(f"✅ Ticket #{ticket['ticket_id']} closed")
                logger.info(f"Closed ticket #{ticket['ticket_id']}")
            else:
                await message.reply("❌ Failed to close, please check logs")
            return
        
        # /reopen command: reopen ticket
        if text_lower == '/reopen':
            if ticket['status'] == 'open':
                await message.reply(f"ℹ️ Ticket #{ticket['ticket_id']} is already open")
                return
            
            if reopen_ticket_by_staff_msg_id(wrapper_msg_id):
                await message.reply(f"✅ Ticket #{ticket['ticket_id']} reopened")
                logger.info(f"Reopened ticket #{ticket['ticket_id']}")
            else:
                await message.reply("❌ Failed to reopen, please check logs")
            return
    
    # Normal reply: forward to customer group
    try:
        # Build reply header (using ticket_id from database)
        user_mention_link = f"[{ticket['username']}](tg://user?id={ticket['user_id']})"
        caption_text = (
            f"💬 Staff reply (Ticket #{ticket['ticket_id']})\n"
            f"📢 {user_mention_link}\n"
            f"{'─' * 30}\n"
        )
        
        # Get message content type
        content_type = message.content_type
        
        # Add original text to caption (if exists)
        if message.text:
            caption_text += message.text
        elif message.caption:
            caption_text += message.caption
        
        # Check if message type supports caption
        unsupported_caption_types = ['video_note', 'sticker']
        
        # Used to record customer group anchor message ID
        customer_anchor_msg = None
        
        if content_type == 'text':
            # Plain text reply
            customer_anchor_msg = await bot.send_message(
                ticket['cust_group_id'],
                caption_text,
                reply_to_message_id=ticket['cust_msg_id'],
                parse_mode=ParseMode.MARKDOWN
            )
        elif content_type in unsupported_caption_types:
            # Types that don't support caption: send text message first, then copy original
            customer_anchor_msg = await bot.send_message(
                ticket['cust_group_id'],
                caption_text,
                reply_to_message_id=ticket['cust_msg_id'],
                parse_mode=ParseMode.MARKDOWN
            )
            await bot.copy_message(
                chat_id=ticket['cust_group_id'],
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_to_message_id=ticket['cust_msg_id']
            )
        else:
            # Types that support caption: use copy_message with caption
            try:
                customer_anchor_msg = await bot.copy_message(
                    chat_id=ticket['cust_group_id'],
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                    caption=caption_text,
                    reply_to_message_id=ticket['cust_msg_id'],
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                # If copy_message with caption fails, fallback
                logger.warning(f"copy_message with caption failed, using fallback: {e}")
                customer_anchor_msg = await bot.send_message(
                    ticket['cust_group_id'],
                    caption_text,
                    reply_to_message_id=ticket['cust_msg_id'],
                    parse_mode=ParseMode.MARKDOWN
                )
                await bot.copy_message(
                    chat_id=ticket['cust_group_id'],
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                    reply_to_message_id=ticket['cust_msg_id']
                )
        
        # Update customer group anchor message ID (for continued conversation routing)
        if customer_anchor_msg:
            update_customer_anchor(wrapper_msg_id, customer_anchor_msg.message_id)
            logger.info(f"Updated anchor: staff_msg={wrapper_msg_id}, anchor={customer_anchor_msg.message_id}")
        
        # Confirm success in staff group
        await message.reply("✅ Reply sent to customer group")
        
        logger.info(f"Staff replied to ticket #{ticket['ticket_id']} for user {ticket['username']} successfully")
        
    except Exception as e:
        logger.error(f"Failed to send reply to customer group: {e}", exc_info=True)
        await message.reply(f"❌ Send failed: {str(e)}")


# ======================== Customer Message Handler ========================

@dp.message(F.chat.type.in_(['group', 'supergroup']), F.chat.id != STAFF_GROUP_ID)
async def handle_customer_message(message: Message):
    """
    Handle customer group messages (check if customer group and bot mentioned)
    Note: Explicitly exclude STAFF_GROUP_ID to avoid conflict with staff reply handler
    """
    # Must be in customer group
    if not is_customer_group(message.chat.id):
        return
    
    # Ignore bot's own messages
    if message.from_user.is_bot:
        return
    
    # First check if continued message
    if await check_and_handle_continue_message(message):
        return
    
    # Get bot info
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    
    # Check if bot mentioned or /ask command (create new ticket)
    if await check_bot_mentioned(message, bot_username):
        await forward_to_staff(message)


# ======================== Main Entry Point ========================

async def main():
    """Main function"""
    # Initialize database
    init_db()
    
    # Get bot info
    bot_info = await bot.get_me()
    
    # Check if token is set (without printing token value)
    token_status = "yes" if API_TOKEN else "no"
    
    logger.info(f"Bot starting: @{bot_info.username}")
    logger.info(f"Token is set: {token_status}")
    logger.info(f"Staff group ID: {STAFF_GROUP_ID}")
    logger.info(f"Admin user ID: {ADMIN_USER_ID}")
    logger.info("=" * 50)
    logger.info("⚠️  Important reminders:")
    logger.info("  1. Ensure bot is added to staff group and customer groups")
    logger.info("  2. Disable Privacy Mode in bot settings")
    logger.info("     Visit @BotFather -> Bot Settings -> Group Privacy -> Turn Off")
    logger.info("  3. Use /addgroup command in customer groups (silent mode)")
    logger.info("  4. Staff must reply to wrapper ticket message (not media copy)")
    logger.info("  5. Customers can reply to bot messages or use /t command to continue")
    logger.info("  6. Staff can use /close /done to close tickets, /reopen to reopen")
    logger.info("=" * 50)
    
    # Start polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please set required environment variables:")
        logger.error("  TELEGRAM_BOT_TOKEN, STAFF_GROUP_ID, ADMIN_USER_ID")
