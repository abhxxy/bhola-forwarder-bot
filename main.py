"""Telegram Userbot for Bhola Updates (Ultra Low-Latency Hybrid Edition).

Guarantees instantaneous delivery (sub-second):
1. Engine A (Passive Socket Push): Listens to real-time MTProto NewMessage & MessageEdited events.
2. Engine B (Active Direct Poller): Fast MTProto GetHistory query every 0.5s to bypass Telegram's broadcast channel push delays.
3. Thread-safe deduplication lock: Ensures every message & edit is processed instantly once without duplicates.
"""
import asyncio
import hashlib
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, MessageNotModifiedError
from telethon.tl.functions.channels import JoinChannelRequest

from transformer import process_message

load_dotenv()

def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


API_ID = int(required_env("API_ID"))
API_HASH = required_env("API_HASH")
SOURCE_CHANNEL = required_env("SOURCE_CHANNEL_ID")
DEST_CHANNEL = required_env("DEST_CHANNEL_ID")
SESSION_NAME = os.getenv("SESSION_NAME", "bhola_session")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL_SECONDS", "0.5"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bhola_forwarder.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("BholaForwarder")

# Track sent message states
# Mapping: source_msg_id -> dest_msg_id
_msg_map = {}
# Mapping: source_msg_id -> text_hash (to detect edits and prevent duplicates)
_processed_hashes = {}
_lock = asyncio.Lock()

def parse_channel_id(val: str | None):
    if not val:
        return None
    val = str(val).strip()
    for prefix in ["https://t.me/", "http://t.me/", "t.me/"]:
        if val.startswith(prefix):
            val = val[len(prefix):]
    val = val.lstrip("@").strip()
    try:
        return int(val)
    except ValueError:
        return val

async def interactive_setup(client: TelegramClient):
    """Wizard to select source and destination channels if not already set in .env."""
    global SOURCE_CHANNEL, DEST_CHANNEL
    if not SOURCE_CHANNEL or not DEST_CHANNEL:
        print("\n" + "=" * 60)
        print(" CHANNEL SELECTION WIZARD")
        print("=" * 60)
        print("Fetching your joined channels and groups...\n")
        dialog_list = []
        i = 1
        async for dialog in client.iter_dialogs(limit=40):
            if dialog.is_channel or dialog.is_group:
                dialog_list.append(dialog)
                print(f"[{i}] {dialog.name} (ID: {dialog.id})")
                i += 1
        
        print("-" * 60)
        if not SOURCE_CHANNEL:
            choice = input("Enter Source Channel/Group Number [1..N] or ID/Username: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(dialog_list):
                SOURCE_CHANNEL = dialog_list[int(choice) - 1].id
            else:
                SOURCE_CHANNEL = choice
        
        if not DEST_CHANNEL:
            choice = input("Enter Destination (My Channel) Number [1..N] or ID/Username: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(dialog_list):
                DEST_CHANNEL = dialog_list[int(choice) - 1].id
            else:
                DEST_CHANNEL = choice
        
        env_content = (
            f"API_ID={API_ID}\n"
            f"API_HASH={API_HASH}\n"
            f"SOURCE_CHANNEL_ID={SOURCE_CHANNEL}\n"
            f"DEST_CHANNEL_ID={DEST_CHANNEL}\n"
            f"SESSION_NAME={SESSION_NAME}\n"
            f"POLL_INTERVAL_SECONDS={POLL_INTERVAL}\n"
        )
        Path(".env").write_text(env_content, encoding="utf-8")
        print(f"[+] Saved to .env! Source: {SOURCE_CHANNEL} | Dest: {DEST_CHANNEL}")
        print("=" * 60 + "\n")

async def process_and_forward(client: TelegramClient, dst_entity, message, trigger_source: str = "SOCKET"):
    """Thread-safe handler for processing and dispatching messages instantly."""
    raw_text = message.raw_text or ""
    if not raw_text.strip():
        return

    msg_id = message.id
    current_hash = hashlib.md5(raw_text.encode("utf-8")).hexdigest()

    async with _lock:
        # Check if identical message content was already processed
        if _processed_hashes.get(msg_id) == current_hash:
            return

        should_fwd, transformed_text = process_message(raw_text)
        if not should_fwd or not transformed_text:
            # Mark as processed so we don't re-check every polling cycle
            _processed_hashes[msg_id] = current_hash
            return

        start_time = time.perf_counter()
        is_edit = msg_id in _msg_map

        post_time_str = message.date.strftime('%H:%M:%S') if getattr(message, 'date', None) else 'N/A'
        logger.info(f"[⚡] [{trigger_source}] Match on #{msg_id} (Post Time: {post_time_str} UTC) -> Sending...")

        try:
            if is_edit:
                dst_msg_id = _msg_map[msg_id]
                try:
                    await client.edit_message(
                        dst_entity,
                        dst_msg_id,
                        transformed_text,
                        link_preview=False
                    )
                    _processed_hashes[msg_id] = current_hash
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    logger.info(f"[✓] Edited in destination #{dst_msg_id} in {elapsed_ms:.1f}ms!")
                    return
                except MessageNotModifiedError:
                    _processed_hashes[msg_id] = current_hash
                    return
                except Exception:
                    pass

            # Send fresh message
            sent = await client.send_message(
                dst_entity,
                transformed_text,
                link_preview=False
            )
            _msg_map[msg_id] = sent.id
            _processed_hashes[msg_id] = current_hash
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(f"[✓] Sent to destination in {elapsed_ms:.1f}ms! (Source #{msg_id} -> Dest #{sent.id})")

        except FloodWaitError as e:
            logger.warning(f"[!] FloodWait: Sleeping {e.seconds}s...")
            await asyncio.sleep(e.seconds + 1)
            sent = await client.send_message(dst_entity, transformed_text, link_preview=False)
            _msg_map[msg_id] = sent.id
            _processed_hashes[msg_id] = current_hash
        except Exception as e:
            logger.error(f"[X] Failed to send message #{msg_id}: {e}")

async def polling_engine(client: TelegramClient, src_entity, dst_entity):
    """Active background poller running every 0.5s to bypass Telegram channel push delays."""
    logger.info(f"[+] Active Ultra-Fast Poller started (Interval: {POLL_INTERVAL}s)")
    while True:
        try:
            async for msg in client.iter_messages(src_entity, limit=8):
                if msg and msg.raw_text:
                    await process_and_forward(client, dst_entity, msg, trigger_source="POLL-0.5s")
        except Exception as e:
            logger.debug(f"Poller loop check: {e}")
        await asyncio.sleep(POLL_INTERVAL)

async def main():
    global SOURCE_CHANNEL, DEST_CHANNEL

    client = TelegramClient(
        SESSION_NAME,
        API_ID,
        API_HASH,
        device_model="Desktop Ultra",
        system_version="Windows 11",
        app_version="5.5.0",
        sequential_updates=False,
        auto_reconnect=True,
        flood_sleep_threshold=60,
    )

    print("\n" + "=" * 60)
    print("      BHOLA UPDATES TELEGRAM FORWARDER BOT")
    print("=" * 60)
    print("Connecting to Telegram...")

    await client.start()

    me = await client.get_me()
    logger.info(f"Signed in as: {me.first_name} {me.last_name or ''} (@{me.username or 'NoUsername'}) [ID: {me.id}]")

    await interactive_setup(client)

    src_id = parse_channel_id(str(SOURCE_CHANNEL))
    dst_id = parse_channel_id(str(DEST_CHANNEL))

    try:
        src_entity = await client.get_entity(src_id)
    except Exception as e:
        logger.error(f"Could not resolve Source Channel '{src_id}': {e}")
        src_entity = src_id

    try:
        dst_entity = await client.get_entity(dst_id)
    except Exception as e:
        logger.error(f"Could not resolve Destination Channel '{dst_id}': {e}")
        dst_entity = dst_id

    try:
        await client(JoinChannelRequest(src_entity))
        logger.info("[+] Confirmed joined to source channel.")
    except Exception:
        pass

    src_title = getattr(src_entity, 'title', str(src_id))
    dst_title = getattr(dst_entity, 'title', str(dst_id))

    logger.info(f"⚡ ULTRA FAST HYBRID ACTIVE (0.5s): Monitoring [{src_title}] -> Forwarding to [{dst_title}]")
    print("\n[+] Real-time monitoring active (< 0.5s latency). Press Ctrl+C to exit.\n")

    # Engine A: Push Socket Listeners
    @client.on(events.NewMessage(chats=src_entity))
    async def on_new_message(event):
        await process_and_forward(client, dst_entity, event.message, trigger_source="PUSH-SOCKET")

    @client.on(events.MessageEdited(chats=src_entity))
    async def on_message_edited(event):
        await process_and_forward(client, dst_entity, event.message, trigger_source="PUSH-SOCKET-EDIT")

    # Engine B: Active Background Poller (0.5s interval)
    poller_task = asyncio.create_task(polling_engine(client, src_entity, dst_entity))

    try:
        await client.run_until_disconnected()
    finally:
        poller_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped.")
