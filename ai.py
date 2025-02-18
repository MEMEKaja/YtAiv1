import os
import random
import openai
import yt_dlp
from telegram import Bot
from slugify import slugify  # Untuk membersihkan nama file

# Set OpenAI API Key dan Token Telegram dari Environment Variables
openai.api_key = os.getenv("OPENAI_API_KEY")
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

# Fungsi untuk mengunduh video dari channel YouTube
def download_video_from_channel(channel_url, output_folder):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(channel_url, download=False)  # Hanya ambil info video
        videos = info_dict.get('entries', [])  # Dapatkan daftar video dari channel

        if not videos:
            print("Tidak ada video yang ditemukan.")
            return None, None

        random_video = random.choice(videos)  # Pilih video acak
        video_url = random_video.get('webpage_url')  # Gunakan webpage_url
        video_title = random_video.get('title', 'video_tanpa_judul')  # Ambil judul

        safe_title = slugify(video_title)  # Bersihkan nama file
        output_path = f"{output_folder}/{safe_title}.mp4"

        ydl.download([video_url])  # Download video
        return safe_title, output_path

# Fungsi untuk mengedit metadata video dengan OpenAI
def edit_video_metadata(title, description):
    prompt = f"Edit the following video title and description: \nTitle: {title}\nDescription: {description}\nMake it more engaging and SEO-friendly."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    edited_title = response.choices[0].text.strip()
    return edited_title

# Fungsi untuk mengirim video ke grup Telegram
def send_video_to_telegram(video_path, chat_id):
    with open(video_path, 'rb') as video_file:
        bot.send_video(chat_id, video_file)

# Fungsi utama untuk memilih dan memproses video
def process_video(channel_url, output_folder, chat_id):
    video_title, video_path = download_video_from_channel(channel_url, output_folder)
    if not video_title or not video_path:
        print("Gagal mengunduh video.")
        return

    print(f"Video downloaded: {video_title}")
    
    # Mengedit metadata video
    description = "Deskripsi video default."
    edited_title = edit_video_metadata(video_title, description)
    print(f"Edited Title: {edited_title}")
    
    # Mengirim video ke grup Telegram
    send_video_to_telegram(video_path, chat_id)
    print(f"Video sent to Telegram group with ID: {chat_id}")

# Jalankan bot dengan channel YouTube yang ditentukan
channel_url = 'https://youtube.com/@romchan25?si=Ufz7MyO1KezXXs8m'  # Ganti dengan URL channel
process_video(channel_url, 'output_folder_path', -1002101465769)  # Ganti dengan ID grup Telegram
