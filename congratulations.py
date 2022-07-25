import random
import time
import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver


names = ["Александр", "Ян", "Сергей", "Владислав", "Илья", "Алексей", "Татьяна", "Татьяна", "Полина", "Лидия"]
# options = webdriver.ChromeOptions()
# options.add_argument("user-agent= Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36")




def parse_url(name):
    url = "https://yandex.ru/lab/postcard?name=" + name
    # driver = webdriver.Chrome(executable_path="D:\\Library\\Projects PyCharm\\parse mail.ru\\chromedriver.exe",
    #                           options=options)
    # driver.get(url=url)
    # time.sleep(0.5)
    # src = driver.page_source
    req = requests.get(url, timeout=2)
    html = BS(req.content, 'html.parser')
    # text = html.select(".container > p")
    print(name)
    print(html)
    # return text[0].text


def generate_random_name():
    generated_name = names[random.randrange(0, len(names))]
    return generated_name


def generate_congrats():
    new_name = generate_random_name()
    congratulation = parse_url(new_name)
    print(congratulation)
    return congratulation