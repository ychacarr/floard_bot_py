from async_scheduler import Job, Periods
from database import Member
import globals
from datetime import datetime as dt, timedelta
from aiohttp import ClientSession
import logging
from typing import Optional

log = logging.getLogger('congratulations_module')


async def congrats_from_porfirii(session: ClientSession, base_congrats: str, **kwargs) -> Optional[str]:
    """
    Функция обращается к API сайта https://porfirevich.ru для генерации текста поздравления.

    :base_congrats -- шаблон поздравления передаваемый Порфирьевичу\n
    :length -- задаёт длину генерируемой последовательности (кол-во слов). По умолчанию 50.\n
    """
    generated_text_lenght = 50 if len(kwargs) == 0 else kwargs["length"]
    post_payload = {"prompt": base_congrats, "length": generated_text_lenght}
    log.info('Trying to connect to porfirii API...')
    async with session.post('https://pelevin.gpt.dobro.ai/generate/', json=post_payload) as resp:
        if resp.status == 200:
            log.info(
                'Connection to porfirii API successfull. Generating congratulations.')
            json_data = await resp.json()
            replies_list = json_data.get('replies')
            replies_list.sort(key=len, reverse=True)
            return replies_list[0]
        else:
            log.error(
                f'Connection to porfirii failed! Response status: {resp.status}.')
            return None


async def congrats_from_yandex(session: ClientSession, base_congrats: str, **kwargs) -> Optional[str]:
    """
    Функция обращается к API Yandex Балабобы для генерации текста поздравления.

    :base_congrats -- шаблон поздравления передаваемый Balabobe\n
    :intro -- задаёт стиль генерации (подробнее смотри на сайте Балабобы), по умолчанию 0\n
    """
    balaboba_intro = 0 if len(kwargs) == 0 else kwargs["intro"]
    post_payload = {"query": base_congrats, "intro": balaboba_intro, "filter": 1}
    log.info('Trying to connect to Balaboba API...')
    async with session.post('https://yandex.ru/lab/api/yalm/text3', json=post_payload) as resp:
        if resp.status == 200:
            log.info(
                'Connection to Balaboba API successfull. Generating congratulations.')
            json_data = await resp.json()
            return json_data["text"]
        else:
            log.error(
                f'Connection to Balaboba failed! Response status: {resp.status}.')
            return None


async def congrats_generator(congrats_template: str) -> str:
    """
    Генераторная функция для обращения к API создания поздравлений. Если все API недоступны, возвращает заглушку.

    :congrats_template -- шаблон поздравления, который будет передан API.
    """
    async with ClientSession() as session:
        yield await congrats_from_porfirii(session, congrats_template)
        yield await congrats_from_yandex(session, congrats_template)
        yield "... мои нейронные облака сломались. Поэтому просто всего!"


async def write_congrats(member_id: int):
    """
    Функция отправки поздравления в личный чат участника (Member из БД)

    member_id -- id участника, для которого будет сгенерировано и отправлено поздравление
    """
    member = Member.get_by_id(member_id)
    congrats_text = f"{member.name}! Поздравляю тебя с днём рождения! Желаю, как и всегда, здоровья, счастья и "
    async for congrats in congrats_generator(congrats_text):
        if congrats != None:
            congrats_text += congrats
            break
    if globals.MAIN_CHAT_ID is None:
        await globals.dp.bot.send_message(member.telegram_id, congrats_text)
    else:
        member_tlg_info = await globals.dp.bot.get_chat_member(globals.MAIN_CHAT_ID, member.telegram_id)
        await globals.dp.bot.send_message(globals.MAIN_CHAT_ID, f'@{member_tlg_info.user.username}\n{congrats_text}')


async def write_notification(member_id: int):
    """
    Функция отправки уведомления о приближающемся ДР наполочника.

    member_id -- id участника о дне рождении которого будет отправлено уведомление.\n
    Уведомление отправляется в чат birthday_group_id.\n
    Если birthday_group_id is None, отправка не происходит, ошибка не генерируется.
    """
    member = Member.get_by_id(member_id)
    notification_text = f"Вставайте, вы, долбанные шашлыки! Приближается день рождения наполочника:\n{member.full_name}\n" +\
                        f"Дата ДР:\n{member.birth_date}"
    if member.birthday_group_id is not None:
        await globals.dp.bot.send_message(member.birthday_group_id, notification_text)


def prepare_congratulation(member) -> Job:
    """
    Функция готовит задачу планировщика AsyncScheduler (Job) поздравления наполочника. Поздравление отправляется в 12:00.

    member -- объект Member, наполочника для поздравления\n

    Функция, записываемая в Job.func: congratulations.write_congrats\n
    Имя работы: member.full_name_birthday
    """
    now_year = dt.now().year
    birtday = dt.strptime(member.birth_date, '%d-%m-%Y')
    birtday = birtday.replace(year=now_year, hour=12, minute=0)
    birtday_str = birtday.strftime('%d.%m.%y %H:%M')
    return Job(
        f'{member.full_name}_birthday',
        write_congrats,
        {'member_id': member.id},
        Periods.year,
        1,
        birtday_str,
        False
    )


def prepare_birthday_notification(member, period: timedelta = timedelta(weeks=2)):
    """
    Функция готовит задачу планировщика AsyncScheduler (Job) уведомления о ДР наполочника. Уведомление отправляется за period от даты дня рождения.

    member -- объект Member, наполочника для отправки уведомления\n
    period -- объект datetime.timedelta значение смещения даты отправки уведомления (смещение происходит от даты ДР). Значение по умолчанию 2 недели.\n

    Функция, записываемая в Job.func: congratulations.write_notification\n
    Имя работы: member.full_name_birthday_notification
    """
    now_year = dt.now().year
    birtday = dt.strptime(member.birth_date, '%d-%m-%Y')
    birtday = (birtday - period)
    birtday = birtday.replace(year=now_year, hour=12, minute=0)
    notification_date_str = birtday.strftime('%d.%m.%y %H:%M')
    return Job(
        f'{member.full_name}_birthday_notification',
        write_notification,
        {'member_id': member.id},
        Periods.year,
        1,
        notification_date_str,
        False
    )


def prepare_congratulation_jobs() -> None:
    """
    Функция для всех наполочников с непустым telegram_id в БД вызывает prepare_congratulation_job и добавляет созданную работу в список globals.scheduler.

    Если у наполочника задан birthday_group_id, вызывает prepare_birthday_notification_job и добавляет работу в список globals.scheduler
    """
    for member in Member:
        if member.telegram_id is not None:
            globals.scheduler.add_job(prepare_congratulation(member))
        if member.birthday_group_id is not None:
            globals.scheduler.add_job(prepare_birthday_notification(member))
