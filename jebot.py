import os
import asyncio
from urllib.parse import urlparse
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_dl import YoutubeDL
from opencc import OpenCC
from config import Config

Jebot = Client(
   "YT Downloader",
   api_id=Config.APP_ID,
   api_hash=Config.API_HASH,
   bot_token=Config.TG_BOT_TOKEN,
)

YTDL_REGEX = (r"^((?:https?:)?\/\/)"
              r"?((?:www|m)\.)"
              r"?((?:youtube\.com|youtu\.be|xvideos\.com|pornhub\.com"
              r"|xhamster\.com|xnxx\.com|fb\.watch))"
              r"(\/)([-a-zA-Z0-9()@:%_\+.~#?&//=]*)([\w\-]+)(\S+)?$")
s2tw = OpenCC('s2tw.json').convert


@Jebot.on_message(filters.command("start"))
async def start(client, message):
   if message.chat.type == 'private':
       await message.reply_sticker("data:image/png;base64,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")
       await Jebot.send_message(
               chat_id=message.chat.id,
               text="""<b>Hey There, I'm AnyDL Bot

I can download video or audio from Youtube. Made by @SL_PUNSITH1 🇱🇰

Hit help button to find out more about how to use me</b>""",   
                            reply_markup=InlineKeyboardMarkup(
                                [[
                                        InlineKeyboardButton(
                                            "Help", callback_data="help"),
                                        InlineKeyboardButton(
                                            "Channel", url="https://t.me/SL_PUNSITH1")
                                    ],[
                                      InlineKeyboardButton(
                                            "Source Code", url="https://github.com/Bot361")
                                    ]]
                            ),        
            disable_web_page_preview=True,        
            parse_mode="html")

@Jebot.on_message(filters.command("help"))
async def help(client, message):
    if message.chat.type == 'private':   
        await Jebot.send_message(
               chat_id=message.chat.id,
               text="""<b>AnyDL Bot Help!

Just send a Youtube url to download it in video or audio format!

~ @SL_PUNSITH1</b>""",
        reply_markup=InlineKeyboardMarkup(
                                [[
                                        InlineKeyboardButton(
                                            "Back ⬅", callback_data="start"),
                                        InlineKeyboardButton(
                                            "About ❕", callback_data="about"),
                                  ],[
                                        InlineKeyboardButton(
                                            "Source Code 📦", url="https://github.com/Bot361")
                                    ]]
                            ),        
            disable_web_page_preview=True,        
            parse_mode="html")

@Jebot.on_message(filters.command("about"))
async def about(client, message):
    if message.chat.type == 'private':   
        await Jebot.send_message(
               chat_id=message.chat.id,
               text="""<b>About AnyDL Bot!</b>

<b>😉 Developer:</b> <a href="https://t.me/SL_PUNSITH1">SL_PUNSITH 🇱🇰</a>

<b>⁉ Support:</b> <a href="https://t.me/Musicwold20210">SL_PUNSITH</a>

<b>❤ Channel:</b> <a href="https://t.me/Godzilla_bots">Godzilla BOTs</a>


<b>~ @SL_PUNSITH1</b>""",
     reply_markup=InlineKeyboardMarkup(
                                [[
                                        InlineKeyboardButton(
                                            "Back ⬅", callback_data="help"),
                                        InlineKeyboardButton(
                                            "Source Code 📦", url="https://github.com/Bot361")
                                    ]]
                            ),        
            disable_web_page_preview=True,        
            parse_mode="html")


# https://docs.pyrogram.org/start/examples/bot_keyboards
# Reply with inline keyboard
@Jebot.on_message(filters.private
                   & filters.text
                   & ~filters.edited
                   & filters.regex(YTDL_REGEX))
async def ytdl_with_button(_, message: Message):
    await message.reply_text(
        "**Choose download type 🤗**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Audio 🎵",
                        callback_data="ytdl_audio"
                    ),
                    InlineKeyboardButton(
                        "Video 🎬",
                        callback_data="ytdl_video"
                    )
                ]
            ]
        ),
        quote=True
    )


@Jebot.on_callback_query(filters.regex("^ytdl_audio$"))
async def callback_query_ytdl_audio(_, callback_query):
    try:
        url = callback_query.message.reply_to_message.text
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': '%(title)s - %(extractor)s-%(id)s.%(ext)s',
            'writethumbnail': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            message = callback_query.message
            await message.reply_chat_action("typing")
            info_dict = ydl.extract_info(url, download=False)
            # download
            await callback_query.edit_message_text("**📥 Downloading audio... 📥**")
            ydl.process_info(info_dict)
            # upload
            audio_file = ydl.prepare_filename(info_dict)
            task = asyncio.create_task(send_audio(message, info_dict,
                                                  audio_file))
            while not task.done():
                await asyncio.sleep(3)
                await message.reply_chat_action("upload_document")
            await message.reply_chat_action("cancel")
            await message.delete()
    except Exception as e:
        await message.reply_text(e)
    await callback_query.message.reply_to_message.delete()
    await callback_query.message.delete()


async def send_audio(message: Message, info_dict, audio_file):
    basename = audio_file.rsplit(".", 1)[-2]
    # .webm -> .weba
    if info_dict['ext'] == 'webm':
        audio_file_weba = basename + ".weba"
        os.rename(audio_file, audio_file_weba)
        audio_file = audio_file_weba
    # thumbnail
    thumbnail_url = info_dict['thumbnail']
    thumbnail_file = basename + "." + \
        get_file_extension_from_url(thumbnail_url)
    # info (s2tw)
    webpage_url = info_dict['webpage_url']
    title = '@UvinduBro - '+s2tw(info_dict['title'])
    caption = f"<b><a href=\"{webpage_url}\">{title}</a></b>"
    duration = int(float(info_dict['duration']))
    performer = s2tw(info_dict['uploader'])
    await message.reply_audio(audio_file, caption=caption, duration=duration,
                              performer=performer, title=title,
                              parse_mode='HTML', thumb=thumbnail_file)
    os.remove(audio_file)
    os.remove(thumbnail_file)


@Jebot.on_callback_query(filters.regex("^ytdl_video$"))
async def callback_query_ytdl_video(_, callback_query):
    try:
        # url = callback_query.message.text
        url = callback_query.message.reply_to_message.text
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': '%(title)s - %(extractor)s-%(id)s.%(ext)s',
            'writethumbnail': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            message = callback_query.message
            await message.reply_chat_action("typing")
            info_dict = ydl.extract_info(url, download=False)
            # download
            await callback_query.edit_message_text("**📥 Downloading video... 📥**")
            ydl.process_info(info_dict)
            # upload
            video_file = ydl.prepare_filename(info_dict)
            task = asyncio.create_task(send_video(message, info_dict,
                                                  video_file))
            while not task.done():
                await asyncio.sleep(3)
                await message.reply_chat_action("upload_document")
            await message.reply_chat_action("cancel")
            await message.delete()
    except Exception as e:
        await message.reply_text(e)
    await callback_query.message.reply_to_message.delete()
    await callback_query.message.delete()


async def send_video(message: Message, info_dict, video_file):
    basename = video_file.rsplit(".", 1)[-2]
    # thumbnail
    thumbnail_url = info_dict['thumbnail']
    thumbnail_file = basename + "." + \
        get_file_extension_from_url(thumbnail_url)
    # info (s2tw)
    webpage_url = info_dict['webpage_url']
    title = '@UvinduBro - '+s2tw(info_dict['title'])
    caption = f"<b><a href=\"{webpage_url}\">{title}</a></b>"
    duration = int(float(info_dict['duration']))
    width, height = get_resolution(info_dict)
    await message.reply_video(
        video_file, caption=caption, duration=duration,
        width=width, height=height, parse_mode='HTML',
        thumb=thumbnail_file)

    os.remove(video_file)
    os.remove(thumbnail_file)


def get_file_extension_from_url(url):
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


def get_resolution(info_dict):
    if {"width", "height"} <= info_dict.keys():
        width = int(info_dict['width'])
        height = int(info_dict['height'])
    # https://support.google.com/youtube/answer/6375112
    elif info_dict['height'] == 1080:
        width = 1920
        height = 1080
    elif info_dict['height'] == 720:
        width = 1280
        height = 720
    elif info_dict['height'] == 480:
        width = 854
        height = 480
    elif info_dict['height'] == 360:
        width = 640
        height = 360
    elif info_dict['height'] == 240:
        width = 426
        height = 240
    return (width, height)


@Jebot.on_callback_query()
async def button(bot, update):
      cb_data = update.data
      if "help" in cb_data:
        await update.message.delete()
        await help(bot, update.message)
      elif "about" in cb_data:
        await update.message.delete()
        await about(bot, update.message)
      elif "start" in cb_data:
        await update.message.delete()
        await start(bot, update.message)

print(
    """
Bot Started!
Join @UvinduBro
"""
)

Jebot.run()
