import os
import re
import asyncio
from telethon import TelegramClient
from yt_dlp import YoutubeDL
from config import *

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/:"*?<>|]+', '_', name)

def load_links():
    if not os.path.exists(LINKS_PATH):
        return []
    with open(LINKS_PATH, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_links(remaining):
    with open(LINKS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(remaining))

def get_ydl_opts(safe_title):
    return {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f"{TEMP_DIR}/{safe_title}.%(ext)s",
        'noplaylist': True,
        'quiet': True,
        'restrictfilenames': True,
        'cachedir': False,
    }

async def main():
    os.makedirs(TEMP_DIR, exist_ok=True)
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    links = load_links()
    if not links:
        await client.send_message(SUPERGROUP_ID, "ℹ️ Нет ссылок для обработки.", reply_to=TOPIC_ID)
        await client.disconnect()
        return

    success_count = 0
    error_count = 0
    processed_links = []
    remaining_links = []

    for url in links:
        try:
            with YoutubeDL() as ydl_probe:
                info = ydl_probe.extract_info(url, download=False)

            title_original = info.get("title", "video")
            safe_title = sanitize_filename(title_original)
            filename = f"{TEMP_DIR}/{safe_title}.mp4"
            ydl_opts = get_ydl_opts(safe_title)

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if not os.path.exists(filename):
                await client.send_message(SUPERGROUP_ID, f"⚠️ Не найден файл:\n{url}", reply_to=TOPIC_ID)
                error_count += 1
                remaining_links.append(url)
                continue

            await client.send_file(
                SUPERGROUP_ID,
                filename,
                caption=title_original,
                reply_to=TOPIC_ID
            )
            os.remove(filename)
            success_count += 1
            processed_links.append(url)

        except Exception as e:
            await client.send_message(SUPERGROUP_ID, f"⚠️ Ошибка:\n{url}\n{e}", reply_to=TOPIC_ID)
            error_count += 1
            remaining_links.append(url)

    save_links(remaining_links)

    summary = (
        "✅ Завершено:\n"
        f"🟢 Успешно: {success_count}\n"
        f"🔴 Ошибок: {error_count}\n"
        f"🕒 Осталось ссылок: {len(remaining_links)}"
    )
    await client.send_message(SUPERGROUP_ID, summary, reply_to=TOPIC_ID)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
