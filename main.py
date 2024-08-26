# using https://github.com/Malith-Rukshan/Suno-API
# https://github.com/Monotirg/youtube-upload
from suno import Suno, ModelVersions
from gradio_client import Client
import os
import random
import shutil
import video
import asyncio
import argparse
import librosa
import numpy as np
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from scipy.interpolate import RegularGridInterpolator
import yt_upload as yt
import movis as mv
from movis.imgproc import qimage_to_numpy


async def upload_youtube(vid_to_upload, title, tags):
    channel = yt.Channel(
        user_data_dir="C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data",
        google_profile="Profile 14", # owns the channel
        cookies_path="creds/client_secret.json"
    )
    video = yt.Video(
        video_path=vid_to_upload,
        title=title,
        made_for_kids=False,
        category=yt.category.MUSIC,
        visibility=yt.visibility.PUBLIC,
        tags=tags,
        # schedule=dt.datetime.now() + dt.timedelta(days=1)
    )

    async with channel(youtube_channel=channel, change_language_to_eng=True, enable_logging=False) as upload:
        await upload.upload_video(video)



async def create_song(prompt, instrumentals=False):
  """
  Creates 2 music
  """
  cookie = '''ajs_anonymous_id=071fbd96-8369-484e-a761-8e9dbe0781ff; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8yaXAyQWpKTXdvN1RBNGhxOHYxdnhPUVRFRmIiLCJyb3RhdGluZ190b2tlbiI6IjM2N3hucDEzNXllY3NtazBxcnlrcGo1eWp0czNuaTBnNmNkMHdlNDYifQ.KNPSeGYchl2f6aZPZGMymh-WyxYcM8N1zQp0GwlyfcHKuJlfatPVjM2DDTwvhXwKAxeW_ROvmpG0Wh14Xx94lRdbrzL5k_Y943euw0RQyBkn7EcdKMF2hRW2fh_09h6bCKuAv10xW1XDxr1tcGjKh0GGGPUBmnA7u9K-vnz9yy0KDBbBA9QuvCfGvlJ2xbdiQUwwV84j95-eNTF11tgeeF4gZrJO7vdnkG_QCBaHevAOxMRotysQo2eqEZ_4IaRp8ef-bkEhdwuAFJa6QiA3xXjYnxC5OYv_D7TVIRX0HnkQqtWhz8gfrz-Fj4B5Cb-mQmLGXodcA4yy1ea-GizxwQ; __client_uat=1723465433; _cfuvid=4q7PBFJP.b3JnsUXb3VBRERWCyHLJqKUYVSFMJpz5ZA-1723740343288-0.0.1.1-604800000; __cf_bm=QIXLAuFgfvNdF9EAISiQLMs7RcJtez2VMJHElKoxkNo-1723741284-1.0.1.1-2u7wtfzdmU1om4Q9PecyZx6KgmDr7oBQ9zRwz1gMtKKbKOyXo38cDx_mdoqNWnbMGVei2zQ85YMiwoSjHzXIfQ; mp_26ced217328f4737497bd6ba6641ca1c_mixpanel=%7B%22distinct_id%22%3A%20%221b928f32-69a7-45c2-979a-ec68321619da%22%2C%22%24device_id%22%3A%20%22190824dec6811ea-0463b55e454a24-26001f51-100200-190824dec6811ea%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fsuno.com%2Fcreate%22%2C%22%24initial_referring_domain%22%3A%20%22suno.com%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fsuno.com%2Fcreate%22%2C%22%24initial_referring_domain%22%3A%20%22suno.com%22%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%221b928f32-69a7-45c2-979a-ec68321619da%22%7D'''
  client = Suno(cookie=cookie, model_version=ModelVersions.CHIRP_V3_5)
  # Generate the song
  songs = client.generate(prompt=prompt,
                        is_custom=False, wait_audio=True, make_instrumental=instrumentals)
  # Download the first generated song
  file_path = client.download(songs[0])
  print(f"Song downloaded to: {file_path}")
  return file_path

async def create_image(prompt, seed=0, randomize_seed=True):
  client = Client("black-forest-labs/FLUX.1-schnell")
  result = client.predict(
    prompt=prompt,
		seed=seed,
		randomize_seed=randomize_seed,
		width=1920,
		height=1080,
		num_inference_steps=4,
		api_name="/infer"
    )
  # Get the file path from the result
  file_path = result[0]
  seed = result[1]

  # Specify the destination path
  destination_path = f"images/{seed}.png"
  # Check if the file exists
  if not os.path.exists(destination_path):
      destination_path = destination_path
  else:
      destination_path = f"images/{seed}-{random.randrange(0,99)}.png"

  shutil.move(file_path, destination_path)
  print(f"Image saved to {destination_path}")
  return destination_path

# main
async def main(song_prompt, image_prompt):
  title = "I will heal"
  # song, image = await asyncio.gather(create_song(prompt=song_prompt), create_image(prompt=image_prompt))
  vid_to_upload = video.main(music_path="downloads/SunoMusic-937e6146-91c3-48e0-aa7d-6807ea06ec0d.mp3", bg_image='images/1053476902.png', output_path=f'finalVideos/{' '.join(title.lower().split())}.mp4')
  tags = [f"{title}", "top music"]
  await upload_youtube(vid_to_upload=vid_to_upload, title=f'{title} - Pajos Music', tags=tags )



if __name__ == '__main__':
   song_prompt = "a pop song about healed from a heartbreak"
   image_prompt = "a detailed potrait picture of a beautiful jamaican lady in her 20s with a black baseball cap with headphones on. the background is a bokeh effect of an expensive taste."
   asyncio.run(main(song_prompt=song_prompt,image_prompt=image_prompt))
