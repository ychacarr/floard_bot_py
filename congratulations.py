from async_scheduler import Job, Periods
from database import Member
import globals
from datetime import datetime, timedelta
import aiohttp
import logging
from random import randint

log = logging.getLogger('congratulations_module')

async def congrats_from_yandex(name: str) -> str:
    # Текст поздравления слишком сильно завязан на 8 марта и в целом на поздравлении лица женского рода. "Чистить" текст от 8 марта слишком запаристо.
    # Поэтому эта функция не используется в коде, возможно в будущем её можно будет приспособить для генерации поздравления с 8 марта.
    exclude_words = {'весенний': '', 
                    'Весенний': '',
                    '8 марта': 'праздник',
                    '8 Марта': 'праздник',
                    'C 8 марта': 'С днём рождения',
                    'С международным женским днем': 'С днем рождения',
                    'Международный женский день': 'день рождения',
                    'восьмое марта': 'празднество'}
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
    """
    Функция обращается к API сайта https://porfirevich.ru для генерации текста поздравления.

    name -- имя именинника\n
    """
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
                replies_list = json_data.get('replies')
                replies_list.sort(key=lambda str_item: len(str_item), reverse=True)
                congrats_text += replies_list[0]
                return congrats_text
            else:
                log.error(f'Connection to porfirii failed! Response status: {resp.status}.')
                raise Exception('Response status != 200. Can\'t generate congratulations!')

async def create_congrats(member_name: str) -> str:
    """
    Генерация текста поздравления с днем рождения. 
    
    member_name -- имя именниника\n
    Поздравление генерируется в любом случае, даже если сервер нейросети выдал ошибку.
    """
    congrats = f'{member_name}' + '! Поздравляю тебя с днём рождения! Желаю, как и всегда, здоровья, счастья и ... мои нейронные облака сломались. Поэтому просто всего!'
    try:
        congrats = await congrats_from_porfirii(member_name)
    except Exception:
        pass
    finally:
        return congrats

async def write_congrats(member_id: int):
    """
    Функция отправки поздравления в личный чат участника (Member из БД)

    member_id -- id участника, для которого будет сгенерировано и отправлено поздравление
    """
    member = Member.get_by_id(member_id)
    congrats = await create_congrats(member.name)
    if globals.MAIN_CHAT_ID is None:
        await globals.dp.bot.send_message(member.telegram_id, congrats)
    else:
        member_tlg_info = await globals.dp.bot.get_chat_member(globals.MAIN_CHAT_ID, member.telegram_id)
        await globals.dp.bot.send_message(globals.MAIN_CHAT_ID, f'@{member_tlg_info.user.username}\n{congrats}')

async def write_notification(member_id: int):
    """
    Функция отправки уведомления о приближающемся ДР наполочника.

    member_id -- id участника о дне рождении которого будет отправлено уведомление.\n
    Уведомление отправляется в чат birthday_group_id.\n
    Если birthday_group_id is None, отправка не происходит, ошибка не генерируется.
    """
    member = Member.get_by_id(member_id)
    if member.birthday_group_id is not None:
        await globals.dp.bot.send_message(member.birthday_group_id, f'Вставайте, вы, долбанные шашлыки! Приближается день рождения наполочника:\n{member.full_name}\n' +
                                            f'Дата ДР:\n{member.birth_date}.')

def prepare_congratulation_job(member) -> Job:
    """
    Функция готовит задачу планировщика AsyncScheduler (Job) поздравления наполочника. Поздравление отправляется в 12:00.

    member -- объект Member, наполочника для поздравления\n

    Функция, записываемая в Job.func: congratulations.write_congrats\n
    Имя работы: member.full_name_birthday
    """
    year = datetime.now().year
    birtday = (datetime.strptime(member.birth_date, '%d-%m-%Y').replace(year= year, hour=12, minute=0)).strftime('%d.%m.%y %H:%M')
    return Job(f'{member.full_name}_birthday', write_congrats, {'member_id': member.id}, Periods.year, 1, birtday, False)

def prepare_birthday_notification_job(member, period: timedelta = timedelta(weeks=2)):
    """
    Функция готовит задачу планировщика AsyncScheduler (Job) уведомления о ДР наполочника. Уведомление отправляется за period от даты дня рождения.

    member -- объект Member, наполочника для отправки уведомления\n
    period -- объект datetime.timedelta значение смещения даты отправки уведомления (смещение происходит от даты ДР). Значение по умолчанию 2 недели.\n

    Функция, записываемая в Job.func: congratulations.write_notification\n
    Имя работы: member.full_name_birthday_notification
    """
    year = datetime.now().year
    birtday = (datetime.strptime(member.birth_date, '%d-%m-%Y').replace(year= year, hour=12, minute=0))
    birtday = birtday - period
    return Job(f'{member.full_name}_birthday_notification', write_notification, {'member_id': member.id}, Periods.year, 1, birtday.strftime('%d.%m.%y %H:%M'), False)
    
def prepare_congratulation_jobs() -> None:
    """
    Функция для всех наполочников с непустым telegram_id в БД вызывает prepare_congratulation_job и добавляет созданную работу в список globals.scheduler.

    Если у наполочника задан birthday_group_id, вызывает prepare_birthday_notification_job и добавляет работу в список globals.scheduler
    """
    for member in Member:
        if member.telegram_id is not None:
            globals.scheduler.add_job(prepare_congratulation_job(member))
        if member.birthday_group_id is not None:
            globals.scheduler.add_job(prepare_birthday_notification_job(member))