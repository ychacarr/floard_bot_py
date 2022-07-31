import time
from bs4 import BeautifulSoup as BS
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument("user-agent= Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36")


def parse_url(name):
    url = "https://yandex.ru/lab/postcard?name=" + name
    driver = webdriver.Chrome(executable_path="chromedriver.exe",
                              options=options)
    driver.get(url=url)
    time.sleep(0.1)
    src = driver.page_source
    html = BS(src, 'html.parser')
    text = html.select(".container > p")
    first_text = text[0].text
    final_text = replace_8_march_text(first_text)
    return final_text


def replace_8_march_text(first_remarks):
    if 'весенний' in first_remarks:
        first_remarks = first_remarks.replace("весенний", '')
    elif 'Весенний' in first_remarks:
        first_remarks = first_remarks.replace("Весенний", '')

    if "С 8 Марта" in first_remarks:
        text = first_remarks.replace("8 Марта", 'С праздником')
        return text
    elif "8 марта" in first_remarks:
        text = first_remarks.replace("8 марта", 'праздник')
        return text
    elif "8 Марта" in first_remarks:
        text = first_remarks.replace("8 Марта", 'праздник')
        return text
    elif "восьмое марта" in first_remarks:
        text = first_remarks.replace("восьмое марта", 'празднество')
        return text


def generate_congrats(name):
    congratulation = parse_url(name)
    return congratulation
