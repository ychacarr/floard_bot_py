from async_scheduler import Job, Periods
from database import Member
from globals import dp, scheduler
from datetime import datetime
import aiohttp
import logging
from random import randint

log = logging.getLogger('congratulations_module')

async def congrats_from_yandex(name: str) -> str:
    exclude_words = {'весенний': '', 
                    'Весенний': '',
                    '8 марта': 'день рождения',
                    '8 Марта': 'день рождения',
                    'C 8 марта': 'С днём рождения',
                    'С международным женским днем': 'С днем рождения',
                    'Международный женский день': 'день рождения',
                    'восьмое марта': 'день рождения'}
    url = 'https://yandex.ru/lab/api/postcard?name=' + name
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            congrats_text = data.get('text')
            for key in exclude_words:
                if key in congrats_text:
                    congrats_text = congrats_text.replace(key, exclude_words[key])
            return congrats_text


async def congrats_from_porfirii(name: str) -> str:
    session_header = {  'Connection': 'keep-alive', 
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                        'Content-Type': 'text/plain;charset=UTF-8',
                        'Accept': '*/*',
                        'Origin': 'https://porfirevich.ru',
                        'Sec-Fetch-Site': 'croos-site',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Dest': 'empty',
                        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
                    }
    congrats_text = f'{name}' + '! Поздравляю тебя с днём рождения! Желаю, как и всегда, здоровья, счастья и'
    post_payload = ('{\"prompt\": \"' + congrats_text + '\", \"length\": 50}').encode(encoding='utf-8')
    log.info('Trying to connect to porfirii API...')
    async with aiohttp.ClientSession(headers=session_header) as session:
        async with session.post('https://pelevin.gpt.dobro.ai/generate/', data=post_payload) as resp:
            if resp.status == 200:
                log.info('Connection to porfirii API successfull. Generating congratulations.')
                json_data = await resp.json()
                congrats_text += json_data.get('replies')[randint(0, 2)]
                return congrats_text
            else:
                log.error(f'Connection to porfirii failed! Response status: {resp.status}.')
                raise Exception('Response status != 200. Can\'t generate congratulations!')

async def create_congrats(member_name: str) -> str:
    congrats = f'{member_name}' + '! Поздравляю тебя с днём рождения! Желаю, как и всегда, здоровья, счастья и ... мои нейронные облака сломались. Поэтому просто всего!'
    try:
        congrats = await congrats_from_porfirii(member_name)
    except Exception:
        pass
    finally:
        return congrats

async def write_congrats(member_id: int):
    member = Member.get_by_id(member_id)
    congrats = await create_congrats(member.name)
    await dp.bot.send_message(member.telegram_id, congrats)


def prepare_congratulation_jobs() -> None:
    for member in Member:
        year = datetime.now().year
        birtday = (datetime.strptime(member.birth_date, '%d-%m-%Y').replace(year= year, hour=12, minute=0)).strftime('%d.%m.%y %H:%M')
        scheduler.add_job(Job(f'{member.full_name}_birthday', write_congrats, {'member_id': member.id}, Periods.year, 1, birtday, False))