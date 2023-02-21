import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor

TELEGRAM_BOT_TOKEN = '5811603637:AAFLZx4ZwPZRTBu3gZId5oCkxWkCzuIkrag'
VK_ACCESS_TOKEN = 'vk1.a.f2qBsgjOMWCQDwq4vZVuP3TqBWLgGM_Fg-BN4xSI9Pxk_ihHYTsEHNyqJvHq1uvS50n4JdB_j9W8sceZQrz31_oZdsYWvlUSC-7MCoOqs_9BkfCKxqO3I9opB3s_VUHAEtHvUPebPP7cqb5XfDztSpq43SK9CkVU5Up3nVVidaX-lybHiFz2TzD2hoR_GAMFs5orJ5xNZhnh48QfScfgNA&expires_in=86400&user_id=38214066
'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply('Hi! Send me a message in the format /download <playlist_name> to download a playlist from VKontakte.')

@dp.message_handler(commands=['download'])
async def download_playlist(message: types.Message):
    chat_id = message.chat.id
    playlist_name = message.text.split(' ')[1]

    playlist = search_for_playlist(playlist_name)
    if not playlist:
        await bot.send_message(chat_id=chat_id, text='Playlist not found.')
        return

    audio_files = get_audio_files(playlist['id'])
    if not audio_files:
        await bot.send_message(chat_id=chat_id, text='Error downloading playlist.')
        return

    for audio_file in audio_files:
        await bot.send_audio(chat_id=chat_id, audio=audio_file)

async def search_for_playlist(playlist_name):
    api_url = f'https://api.vk.com/method/audio.getPlaylists?access_token={VK_ACCESS_TOKEN}&v=5.131'
    response = requests.get(api_url).json()
    playlists = response.get('response', {}).get('items', [])
    playlist = next((p for p in playlists if p['title'].lower() == playlist_name.lower()), None)
    return playlist

async def get_audio_files(playlist_id):
    api_url = f'https://api.vk.com/method/audio.get?access_token={VK_ACCESS_TOKEN}&v=5.131&playlist_id={playlist_id}'
    response = requests.get(api_url).json()
    songs = response.get('response', {}).get('items', [])
    audio_files = []
    for song in songs:
        audio_file = song.get('url')
        if audio_file:
            audio_files.append(audio_file)
    return audio_files

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)