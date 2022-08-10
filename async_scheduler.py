import ast
import asyncio
import datetime
from inspect import iscoroutinefunction
import logging
from typing import Any, Awaitable, Callable, Dict, List
import copy
import sys

# ToDo:
#       1. Список неименованных параметров (args) в конструкторе Job.
#       4. Использовать Pickle для параметров функций
# Done:
#       2. Переместить куда-нибудь check_year.
#       3. Механизм прерывания сна, в случае добавления новой работы.


log = logging.getLogger('async_scheduler')

class Periods:
    """
    Класс-словарь инкапсулирующий возможные периоды для класса Job.

    Использование: см. класс Job
    """
    once = 'once'
    minute = 'minute'
    hour = 'hour'
    day = 'day'
    week = 'week'
    month = 'month'
    year = 'year'

class Job:
    """
    Класс инкапсулирующий некоторую периодиескую|разовую работу.
    Период задается в виде строки (возможные значения см. в классе Periods).
    Количество промежутков периода задается в виде целого числа (>= 0).
    Время и дата представляются в виде строки в формате 'дд.мм.гг ЧЧ:ММ'.
    Суть работы (то, что нужно будет выполнить в указанное время) представлена в виде async функции.

    Использование:
        Для создания разовой работы (т.е. которая будет выполнена единожды в 10.08.22 12:00) с некоторой функцией some_func и параметрами:\n
            arg1 = 1, arg2 = 'something', arg3 = 2.3\n
        необходимо вызвать следующий конструктор:\n
        Job('first_job', some_func, {'arg1': 1, 'arg2': 'something', 'arg3': 2.3}, Periods.once, str_datetime='10.08.22 12:00')

        Для создания периодической работы с периодом выполнения каждые 3 минуты (начиная с 10.08.22 10:00) с функцией my_func и параметрами:\n
            testing = 3\n
        необходимо вызвать следующий конструктор:\n
        Job('second_job', my_func, {'testing': 3}, Periods.minute, 3, '10.08.22 10:00')

        Для создания периодической работы с периодом выполнения каждый год (начиная с 10.08.22 10:00) с функцией f без параметров необходимо 
        вызвать следующий конструктор:\n
        Job('third_job', f, period_name= Periods.year, period_amount= 1, str_datetime= '10.08.22 10:00')\n

        В объекте работы есть свойство need_backup, которое определяет нужно ли записывать эту работу в backup файл AsyncSchedule. Если задача создаётся
        динамически (т.е. при возникновении некоторого события, которое определяется только во время работы программы), то это свойство следует задать как True 
        (установлено по умолчанию), в противном случае (если работа создаётся и заносится в расписание каждый раз при старте программы) следует пометить работу 
        как незаписываемую в backup файл.
    Объект класса Job не отслеживает текущее время и не выполняется сам по себе! Для добавления работы в очередь выполнения используйте класс AsyncScheduler.
    """

    def __init__(self, name:str, 
                func:Callable[[], Awaitable[None]],
                kwargs:Dict[str, Any] = None,
                period_name:str = None, 
                period_amount:int = 0,
                str_datetime:str|None = None,
                need_backup: bool = True):
        """
        Создаёт новый объект Job.

        name -- наименование работы;\n
        func -- async функция, которая будет вызвана в назначенные дату и время;\n
        kwargs -- словарь, содержащий наименования и значения параметров с которыми будет вызвана функция func;\n
        period_name -- строка из множества: 'once', 'minute', 'hour', 'day', 'week', 'month', 'year';\n
        period_amount -- целое число >= 0. Значение 0 допустимо только в сочетании с периодом 'once'!;\n
        str_datetime -- строка в формате 'дд.мм.гг ЧЧ:ММ'. В случае несовпадения формата выбрасывается исключение;
        need_backup -- bool определяющий необходимость заносить работу в backup файл.

        Если строка str_datetime = None, в качестве времени указывается datetime.now() (т.е. текущие дата и время).\n
        Если переданная функция func не является async функцией, выбрасывается исключение.
        """
        self._name = name
        self._func = None
        self._func_kwargs = None
        self.func_set(func, kwargs)
        self._period_name = None
        self._period_amount = 0
        self.period_amount_set(period_amount)
        self.period_name_set(period_name)
        self._need_backup = need_backup

        if (str_datetime == None):
            str_datetime = datetime.datetime.now().strftime('%d.%m.%y %H:%M')
        self._datetime = datetime.datetime.strptime(str_datetime, '%d.%m.%y %H:%M')

        if ((datetime.datetime.now().replace(second=0, microsecond=0)) > self._datetime):
            if (self._period_name != 'once'):
                self.next_datetime()
            else:
                raise ValueError('async_scheduler.Job() error. str_datetime should be in future.')

    def _check_year(in_year):
        """
        Проверяет год на переполнение.
        """
        if (in_year > datetime.datetime.max.year):
            raise OverflowError('async_scheduler.Job.next_datetime() error. End of time!')

    def unpack_from_str(in_str:str):
        """
        Создаёт новый объект Job из строки.

        Строка должна удовлетворять формату:\n
        str|str|str|dict{str, Any}|str|int|str\n
        Значения:\n
        имя_работы|имя_функции|наименование_модуля_функции|параметры функции|название_периода|интервал|дата_начала
        """
        data = in_str.split('|')
        if (len(data) == 7):
            func = getattr(sys.modules[data[2]], data[1])
            kwargs = None
            if (data[3] != 'None'):
                kwargs = ast.literal_eval(data[3])
            if (data[6].endswith('\n')):
                data[6] = data[6].removesuffix('\n')
            return Job(data[0], func, kwargs, data[4], int(data[5]), data[6])
        else:
            raise ValueError('async_scheduler.Job.unpack_from_str error. Unknown data format.')

    def pack_to_str(self)->str:
        """
        Пакует объект Job в строку. Используется для записи объекта в файл.
        """
        str_datetime = self._datetime.strftime('%d.%m.%y %H:%M')
        return f'{self._name}|{self._func.__name__}|{self._func.__module__}|{self._func_kwargs}|{self._period_name}|{self._period_amount}|{str_datetime}'
    
    def __repr__(self) -> str:
        """
        Преобразование объекта в строковое представление (используется при выводе объекта в консоль).\n

        Формирует строку вида:\n
            'Job наименование_работы|дата_и_время'
        """
        return f'Job {self._name}|{self._datetime}'

    def next_datetime(self)->bool:
        """
        На основе period_name и period_amount вычисляет сладующие дату и время выполнения работы. Записывает новые значения в объект.

        Возвращает:\n
            True - в случае успешного перехода к следующим дате и времени\n
            False - если period_name = 'once'
        """
        if (self._period_name == 'once'):
            return False
        elif (self._period_name == 'year'):
            new_year = self._datetime.year + self._period_amount
            Job._check_year(new_year)
            self._datetime = self._datetime.replace(year=new_year)
            return True
        elif (self._period_name == 'month'):
            new_year = self._datetime.year
            month_offset = self._period_amount
            if (self._period_amount >= 12):
                new_year = self._datetime.year + (self._period_amount // 12)
                Job._check_year(new_year)
                self._datetime = self._datetime.replace(year=new_year)
                month_offset = self._period_amount - (12 * (self._period_amount // 12))

            new_month = self._datetime.month + month_offset
            if (new_month > 12):
                new_year = self._datetime.year + (new_month // 12)
                Job._check_year(new_year)
                self._datetime = self._datetime.replace(year= new_year)
                new_month = new_month - 12 * (new_month // 12)
            self._datetime = self._datetime.replace(month=new_month)
            return True
        elif (self._period_name == 'week'):
            self._datetime += datetime.timedelta(weeks=self._period_amount)
            return True
        elif (self._period_name == 'day'):
            self._datetime += datetime.timedelta(days=self._period_amount)
            return True
        elif (self._period_name == 'hour'):
            self._datetime += datetime.timedelta(hours=self._period_amount)
            return True
        elif (self._period_name == 'minute'):
            self._datetime += datetime.timedelta(minutes=self._period_amount)
            return True
        raise ValueError('async_scheduler.Job() error. Unknown _period_name.')

    def __lt__(self, other)->bool:
        """
        Оператор less than (self < obj).

        Сравнение объектов Job происходит по значению job_datetime.
        """
        if (isinstance(other, Job)):
            return self._datetime < other._datetime
        elif (isinstance(other, datetime.datetime)):
            return self._datetime < other
        raise ValueError('async_scheduler.Job.__lt__. Other should be a Job or datetime object.')
    
    def __eq__(self, other)->bool:
        """
        Оператор equal (self == obj).

        Сравнение объектов Job происходит по значению job_datetime.
        """
        if (isinstance(other, Job)):
            return self._datetime == other._datetime
        elif (isinstance(other, datetime.datetime)):
            return self._datetime == other
        raise ValueError('async_scheduler.Job.__eq__. Other should be a Job or datetime object.')

    @property
    def job_datetime(self)->datetime.datetime:
        """
        Возвращает время и дату работы.
        """
        return copy.deepcopy(self._datetime)

    def job_datetime_set(self, datetime_str:str):
        """
        Задает новые дату и время.\n

        datetime_str -- строка в формате 'дд.мм.гг ЧЧ:ММ'. В случае несовпадения формата выбрасывается исключение.
        """
        self._datetime = datetime.datetime.strptime(datetime_str, '%d.%m.%y %H:%M')
    
    @property
    def need_backup(self) -> bool:
        return self._need_backup

    @property
    def name(self)->str:
        """
        Возвращает имя работы.
        """
        return self._name
    
    # def name_set(self, new_name:str):
    #     """
    #     Задает новое имя для работы.
    #     """
    #     self._name = new_name
    
    @property
    def func(self)->Callable[[], Awaitable[None]]:
        """
        Возвращает функцию, сохраненную в объекте Job.
        """
        return self._func

    def func_set(self, func:Callable[[], Awaitable[None]], kwargs:Dict[str, Any] = None):
        """
        Задает новую функцию, которая будет вызвана в job_datetime.

        func -- async функция, которая будет вызвана в назначенные дату и время;\n
        kwargs -- словарь, содержащий наименования и значения параметров с которыми будет вызвана функция func.\n
        """
        if (iscoroutinefunction(func)):
            self._func = func
            if (kwargs == None):
                self._func_kwargs = None
            elif (isinstance(kwargs, dict)):
                self._func_kwargs = kwargs
            else:
                ValueError('async_scheduler.Job.func_set error. Unknown typeof args. Should be dict or None.')
        else:
            raise ValueError('async_scheduler.Job.func_set error. func should be a coroutine function.')
    
    @property
    def period_name(self)->str:
        """
        Возвращает наименование периода.
        """
        return self._period_name

    def period_name_set(self, new_period: str):
        """
        Задает новый период выполнения работы.

        new_period -- строка из множества: 'once', 'minute', 'hour', 'day', 'week', 'month', 'year';\n
        """
        if (new_period == 'once' or new_period == None):
            self._period_name = 'once'
        elif (new_period in ['minute', 'hour', 'day', 'week', 'month', 'year']):
            if (self._period_amount <= 0):
                raise ValueError('async_scheduler.Job.period_name_set() error. period_amount can be zero only when period_name = \'once\'.')
            else:
                self._period_name = new_period
        else:
            raise ValueError('async_scheduler.Job.period_name_set() error. Unknown period_name.')

    @property
    def period_amount(self)->int:
        """
        Возвращает интервал выполнения работы.
        """
        return self._period_amount
    
    def period_amount_set(self, new_amount: int):
        """
        Задает новый интервал выполнения работы.

        new_amount -- целое число >= 0. Значение 0 допустимо только в сочетании с периодом 'once'!
        """
        if (new_amount < 0):
            raise ValueError('async_scheduler.Job.period_amount_set() error. period_amount can\'t be less than zero.')
        elif (new_amount == 0 and (self._period_name != 'once') and (self._period_name != None)):
            raise ValueError('async_scheduler.Job.period_amount_set() error. period_amount can be zero only when period_name = \'once\'.')
        else:
            self._period_amount = new_amount

    @property
    def coroutine_func(self):
        """
        Создает новый объект корутины (Coroutine) из функции func и параметров kwargs объекта Job.
        """
        res = None
        if (self._func_kwargs != None):
            res = self._func(**self._func_kwargs)
        else:
            res = self._func()
        return res
    
    def do_job(self, loop:asyncio.AbstractEventLoop = None):
        """
        Добавляет новое задание (task) с корутиной работы в цикл событий asyncio.

        loop -- цикл событий в котором будет выполнена функция Job.\n
        Если loop = None, будет использован текущий запущенный цикл (asyncio.get_running_loop()). 
        """
        job_loop = None
        if (loop != None):
            job_loop = loop
        else:
            job_loop = asyncio.get_running_loop()
        job_loop.create_task(self.coroutine_func)

class AsyncScheduler:
    """
    Класс инкапсулирующий планировщик выполнения работ.

    Содержит список работ. Уникальность работы в списке определяется имнем. Существование двух работ с одинаковыми именами не допускается.
    (При добавлении новой работы, если в расписании уже существует работа с таким именем, новая игнорируется).\n

    Добавление работы с "просроченным" сроком выполнения невозможно. (будет выброшено исключение)\n
    Выполнение работ реализовано в виде добавления новых задач (task) в запущенный цикл asyncio. Все задачи будут гарантированно добавлены в цикл,
    будут ли они все выполнены - зависит от состояния цикла и работы asyncio.\n
    Ожидание до времени срабатывания следующей работы выполнено через asyncio.sleep. Планировщик не имеет жестко заданного интервала ожидания,
    вместо этого время ожидания рассчитывается на основе вычитания:\n
        время выполнения следующей задачи - текущее время\n
    Вычитание дат и времени реализовано через стандартный модуль datetime. Текущее время получается с помощью datetime.now()\n
    Если в момент ожидания следующей работы в расписание добавляется новая работа, планировщик прерывает сон, добавляет работу и перезапускает цикл ожидания.\n

    Реализована функция записи невыполненных работ в файл с возможностью их последующего восстановления. (может пригодиться в случае аварийного завершения программы)
    
    Использование:\n
        Класс предусматривает два варианта запуска планировщика:\n
            Вызов .run()\n
            Вызов .add_to_loop()\n
        Вызов .run() запускает цикл ожидания прямо внутри себя. Дальнейший код (расположенный за вызовом .run будет выполнен только после того
        как цикл завершится). Использовать .run стоит в том случае, если планировщик является основной задачей (task) всего приложения. Пример:\n
            async main():\n
                scheduler = AsyncScheduler(someList)\n
                await scheduler.run()\n
                ...код здесь будет выполнен только после завершения работы цикла планировщика (т.е. когда очередь задач будет пуста, если в расписании есть
                хотя бы одна периодиеская задача, цикл остановится только через системное прерывание)\n
        Вызов .add_to_loop() создает в существующем цикле новую asyncio задачу с функцией self.run(). После срабатывания, интерпретатор продолжит выполнять
        инструкции расположенные за вызовом .add_to_loop(). Планировщик запустится только после запуска основного цикла событий (т.е. только после вызова
        asyncio.run_untill_complete() или asyncio.run_forever()). Если код после вызова .add_to_loop() не запускает цикл, планировщик не будет запущен. Пример:\n
            async main():\n
                scheduler = AsyncScheduler(someList)\n
                loop = asyncio.get_event_loop()\n
                scheduler.add_to_loop(loop)\n
                ...здесь код, добавляющий другие задачи в цикл loop и\или выполняющий иные инструкции...\n
                loop.run_untill_complete() - цикл планировщика задач начнет выполнение с этого момента\n
        Возможна ситуация, когда некоторая задача, запускающая цикл событий, перехватывает все исключения и прерывания, не давая планировщику отработать функцию
        записи невыполненных работ в файл (пример: использование планировщика вместе с ботом aiogram). В таком случае в main есть смысл добавить строку вида:\n
            scheduler.do_backup()\n
        Чтобы функция точно сработала её можно добавить в блок finaly. Пример:\n
            ...код main...\n
            try:\n
                ...код добавления задач в цикл событий asyncio и запуск цикла...\n
            finaly:\n
                scheduler.do_backup()\n
    """
    def __init__(self, jobs:List[Job] = None, backup_flag:bool = False, backup_filename:str = None):
        """
        Создает новый объект AsyncScheduler.

        jobs -- список, содержащий объекты Job
        backup_flag -- включение/отключение записи в файл невыполненных работ
        backup_filename -- название файла для записи
        """
        self._loop_task = None
        self._stopped = False
        self._jobs = []
        for job in jobs:
            self.add_job(job)
        self._jobs.sort()
        self._backup_file = None
        if (backup_flag):
            if (backup_filename != None):
                self._backup_file = backup_filename
                try:
                    with open(backup_filename, 'r', encoding='utf-8') as backup:
                        for line in backup:
                            temp_job = Job.unpack_from_str(line)
                            try:
                                self.add_job(temp_job)
                            except ValueError:
                                pass
                except FileNotFoundError:
                    pass
            else:
                raise ValueError('async_scheduler.AsyncScheduler.__init__ error. backup_filename can\'t be None when backup_flag = True.')

    def do_backup(self):
        """
        Записывает все невыполненные работы в файл.

        Файл для записи задается при создании объекта. Если файл не был задан, .do_backup() выбросит ValueError.
        """
        if (self._backup_file != None):
            if (len(self._jobs) > 0):
                log.info(f'Writing backup file as {self._backup_file}')
                with open(self._backup_file, 'w', encoding='utf-8') as backup:
                    for job in self._jobs:
                        if (job.need_backup):
                            backup.write(job.pack_to_str())
                            backup.write('\n')
        else:
            raise ValueError('async_scheduler.AsyncScheduler._do_backup error. Missing backup filename. self._backup_file = None.')

    async def run(self):
        """
        Запускает цикл планировщика задач.

        Цикл будет работать до тех пока не выполнится хотя бы одно из следующих условий:\n
            1. Все задачи выполнены, очередь задач пуста;\n
            2. Получено системное прерывание (KeyboardInterrupt|SystemExit);\n
            3. Получен сигнал отмены задачи asyncio (task.cancel());\n
            4. В планировщик добавлена новая задача.\n
        Во всех случаях, кроме последнего, планировщик остановится, выполнит вызовет .do_backup(), если это необходимо, и заврешит работу.\n
        В 4 случае планировщик остановится, но вызов .do_backup() произведен не будет.
        """
        try:
            if (self._loop_task != None):
                log.warning(f'Waiting while old cycle stopping...Can\'t start now.')
                while (self._loop_task != None):
                    asyncio.sleep(0)
            log.info(f'Started. Jobs in schedule: {len(self._jobs)}')
            running_loop = asyncio.get_running_loop()
            self._loop_task = asyncio.current_task(running_loop)
            self._stopped = False
            while True:
                if (len(self._jobs) > 0):
                    now_datetime = datetime.datetime.now().replace(second=0, microsecond=0)
                    time_to_wait = 0
                    if (now_datetime == self._jobs[0]):
                        done_jobs = []
                        for i in range(0, len(self._jobs)):
                            if (now_datetime == self._jobs[i]):
                                self._jobs[i].do_job(running_loop)
                                if (not(self._jobs[i].next_datetime())):
                                    done_jobs.append(i)
                                    # del self._jobs[i]
                                    # i -= 1
                                continue
                            if (self._jobs[i] < now_datetime):
                                break
                        for i in done_jobs:
                            del self._jobs[i]
                        self._jobs.sort()
                        continue
                    else:
                        if (now_datetime > self._jobs[0]):
                            del self._jobs[0]
                            continue
                        else:
                            # используется datetime.datetime.now() так как в now_datetime отброшены секунды и микросекунды, что приводит к неправильным расчётам
                            # т.е. xx:05:00 - yy:04:00 = zz:01:00 - ожидание в минуту, несмотря на то, что текущее время может быть yy:04:40 и ждать нужно лишь
                            # оставшиеся 20 секунд
                            time_to_wait = (self._jobs[0].job_datetime - datetime.datetime.now().replace(microsecond=0)).seconds
                    await asyncio.sleep(time_to_wait)
                else:
                    log.info(f'All jobs done.')
                    break
        except (KeyboardInterrupt, SystemExit):
            log.warning(f'KeyboardInterrupt|SystemExit. Exiting...')
            pass
        except asyncio.CancelledError:
            if (not self._stopped):
                log.warning(f'Interrupted via task.cancel(). Exiting...')
                raise
            else:
                log.info(f'Stopped via .stop(). Exiting...')
        finally:
            self._loop_task = None
            if (not self._stopped):
                if (self._backup_file != None and len(self._jobs) != 0):
                    log.info(f'Writing data to backup file.')
                    self.do_backup()
                log.info(f'Goodbye!')
            return None

    def _search_name(self, name:str)->int|None:
        """
        Выполняет поиск по списку работ. Критерий поиска - имя работы.

        name -- строка, содеражая имя работы.\n
        Возвращает индекс найденной работы, если поиск успешен, None в ином случае.
        """
        if (name != None and len(name) != 0):
            for i in range(len(self._jobs)):
                if (self._jobs[i].name == name):
                    return i
        return None

    def add_to_loop(self, loop:asyncio.AbstractEventLoop = None):
        """
        Добавляет планировщик в качестве новой задачи в цикл событий asyncio.

        loop -- объект цикла событий, в котором будет создана новая задача.\n
        Если loop = None, в качестве цикла будет использован цикл, полученный через asyncio.get_event_loop().
        """
        if (loop != None):
            loop.create_task(self.run())
        else:
            get_loop = asyncio.get_event_loop()
            get_loop.create_task(self.run())
    
    def add_job(self, job:Job)->bool:
        """
        Добавляет в планировщик новую работу.

        job -- объект Job, представляющий новую работу.\n
        Если в списке работ планировщика уже есть работа с совпадающим именем, новая работа добавлена не будет.\n
        Возвращает:\n
            True - если работа была добавлена.\n
            False - в ином случае.\n
        Если на момент добавления работы, цикл планировщика уже запущен, он будет перезапущен посредством вызова .stop и последующего вызова .add_to_loop
        """
        if (isinstance(job, Job)):
            if (self._search_name(job.name) == None):
                if (datetime.datetime.now().replace(second=0, microsecond=0) > job.job_datetime):
                    raise ValueError('async_scheduler.AsyncScheduler.add_job error. Job datetime is in the past.')
                self._jobs.append(job)
                if (self._loop_task != None):
                    self.stop()
                    self._jobs.sort()
                    self.add_to_loop(asyncio.get_running_loop())
                    return True
                self._jobs.sort()
                return True
            log.warning(f'add_job collision. Job has not been added! Collision job name: {job.name}')
        return False
    
    def delete_job(self, name:str)->bool:
        """
        Удаляет работу из списка планировщика.

        name -- имя работы, которую необходимо удалить.\n
        Возвращает:\n
            True - в случае, если работа с указанным name была найдена и удалена.\n
            False - если работы с именем name нет.\n
        Не перезапускает цикл планировщика.
        """
        job_index = self._search_name(name)
        if (job_index != None):
            del self._jobs[job_index]
            return True
        log.warning(f'delete_job. Nothing has been deleted')
        return False
    
    def stop(self):
        """
        Останавливает запущенный цикл планировщика.

        Если цикл не был запущен, ничего не делает.
        """
        if (self._loop_task != None):
            self._loop_task.cancel()
            self._stopped = True