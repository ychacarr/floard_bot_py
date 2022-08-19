# import random
# import time
# import requests
# from bs4 import BeautifulSoup as BS
# from selenium import webdriver


# names = ["Александр", "Ян", "Сергей", "Владислав", "Илья", "Алексей", "Татьяна", "Татьяна", "Полина", "Лидия"]
# # options = webdriver.ChromeOptions()
# # options.add_argument("user-agent= Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
# #                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36")




# def parse_url(name):
#     url = "https://yandex.ru/lab/postcard?name=" + name
#     # driver = webdriver.Chrome(executable_path="D:\\Library\\Projects PyCharm\\parse mail.ru\\chromedriver.exe",
#     #                           options=options)
#     # driver.get(url=url)
#     # time.sleep(0.5)
#     # src = driver.page_source
#     req = requests.get(url, timeout=2)
#     html = BS(req.content, 'html.parser')
#     # text = html.select(".container > p")
#     print(name)
#     print(html)
#     # return text[0].text


# def generate_random_name():
#     generated_name = names[random.randrange(0, len(names))]
#     return generated_name


# def generate_congrats():
#     new_name = generate_random_name()
#     congratulation = parse_url(new_name)
#     print(congratulation)
#     return congratulation

from typing import List
from async_scheduler import Job, Periods
from database import Member
from globals import dp, scheduler
from datetime import datetime

async def create_congrats(member_fullname: str) -> str:
    return f'С днём родждения {member_fullname}!'

async def write_congrats(member_id: int):
    member = Member.get_by_id(member_id)
    congrats = create_congrats(member.full_name)
    await dp.bot.send_message(member.telegram_id, congrats)


def prepare_congratulation_jobs() -> None:
    for member in Member:
        year = datetime.now().year
        birtday = (datetime.strptime(member.birth_date, '%d-%m-%Y').replace(year= year, hour=12, minute=0)).strftime('%d.%m.%y %H:%M')
        scheduler.add_job(Job(f'{member.full_name}_birthday', write_congrats, {'member_id': member.id}, Periods.year, 1, birtday, False))
