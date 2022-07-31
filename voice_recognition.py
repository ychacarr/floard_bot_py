# import pydub
# import speech_recognition as sr
# from aiogram import types
# from aiogram.types import  File
# from pathlib import Path
# from os import path
# from handlers import bot
# from pydub import AudioSegment
# import ffmpeg
# import soundfile
# import subprocess, os
#
#
#
# class FFmpeg:
#     cmds = '\\ffmpeg\\bin\\ffmpeg.exe'
#     cmds_probe = '\\ffmpeg\\bin\\ffprobe.exe'
#
#     def __init__(self, mypath, cut_duration):
#         self.mypath = mypath
#         self.cut_duration = cut_duration
#
#
# def mp3_wav(self, file):
#     if file.endswith('ogg'):
#         output = file[:-4] + ".wav"
#         p = self.Popen(FFmpeg.cmds + " -i " + file + " -acodec pcm_s16le -ac 1 -ar 16000 " + output)
#         p.communicate()
#         os.remove(file)
#         return output
#     else:
#         return file
#
#
# async def handle_file(file: File, file_name: str, path: str):
#     Path(f"{path}").mkdir(parents=True, exist_ok=True)
#     await bot.download_file(file_path=file.file_path, destination=f"{path}/{file_name}")
#     print('recorded')
#
#
# async def speech_recogn(msg: types.Message):
#     pydub.AudioSegment.ffmpeg = "D:\\Library\\Projects PyCharm\\floard_bot_py\\ffmpeg\\fftools"
#
#     # file = await bot.get_file(msg.voice.file_id)
#     # file_path = file.file_path
#     # await bot.download_file(file_path, 'sound.ogg')
#     # # AUDIO_FILE = "123.wav"
#     sound = AudioSegment.from_ogg(r'sound.ogg')
#     sound.export(r'sound.wav', format='wav')
#     # data, samplerate = soundfile.read('sound.ogg')
#     # soundfile.write('1234.wav', data, samplerate, subtype='PCM_16')
#     # file = FFmpeg("D:\\Library\\Projects PyCharm\\floard_bot_py", 2)
#     # sample = sr.AudioFile('sound.wav')
#     #
#     # r = sr.Recognizer()
#     # with sample as source:
#     #     audio = r.record(source)
#     # recognized_text = r.recognize_google(audio, language='ru-RU')
#     # print(recognized_text)
