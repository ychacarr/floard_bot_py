from ast import List
from re import T
from telnetlib import GA
from peewee import *
from random import randint

DBFile = SqliteDatabase('./data/floardbase.db')

class BaseModel(Model):
    class Meta:
        database = DBFile

class ActionType(BaseModel):
    id = AutoField(column_name='ID', null=False)
    name = TextField(column_name='Name', unique=True)

    class Meta:
        table_name = 'ActionType'

class Duration(BaseModel):
    id = AutoField(column_name='ID', null=False)
    name = TextField(column_name='Name', unique=True)

    class Meta:
        table_name = 'Duration'

class Game(BaseModel):
    action_type = ForeignKeyField(column_name='ActionType', field='id', model=ActionType)
    duration = ForeignKeyField(column_name='Duration', field='id', model=Duration)
    id = AutoField(column_name='ID', null=False)
    is_convers = BooleanField(column_name='IsConvers', default=False)
    max_amount = IntegerField(column_name='MaxAmount')
    min_amount = IntegerField(column_name='MinAmount')
    name = TextField(column_name='Name', unique=True)

    @property
    def duration_name(self):
        return Duration.get_by_id(self.duration).name
    
    @property
    def action_type_name(self):
        return ActionType.get_by_id(self.action_type).name

    def __str__(self):
        return f'{self.name}'

    class Meta:
        table_name = 'Game'

class Member(BaseModel):
    birth_date = DateField(column_name='BirthDate')
    birthday_group_id = BigIntegerField(column_name='BirthdayGroupID', null=True, unique=True)
    id = AutoField(column_name='ID', null=False)
    is_active = BooleanField(column_name='IsActive', default=True)
    name = TextField(column_name='Name')
    nickname = TextField(column_name='Nickname', null=True, unique=True)
    surname = TextField(column_name='Surname')
    telegram_id = BigIntegerField(column_name='TelegramID', null=True, unique=True)
    sex = TextField(column_name='Sex')

    @property
    def full_name(self):
        return f'{self.name} {self.surname}'

    class Meta:
        table_name = 'Member'

class Preference(BaseModel):
    game_id = ForeignKeyField(column_name='GameID', field='id', model=Game, null=True)
    level = IntegerField(column_name='Level', default=2)
    member_id = ForeignKeyField(column_name='MemberID', field='id', model=Member, null=True)

    class Meta:
        table_name = 'Preference'
        indexes = (
            (('member_id', 'game_id'), True),
        )
        primary_key = CompositeKey('game_id', 'member_id')

class KekNoun(BaseModel):
    id = AutoField(column_name='ID', null=False)
    male = TextField(column_name='Male', unique=True, null=False)
    feminine = TextField(column_name='Feminine', unique=True, null=False)

    def get_random(sex:str) -> str:
        """
        Возвращает рандомное существительное. Род задаётся параметром sex.

        sex -- 'М' или 'Ж' задаёт род существительного
        """
        rand_el = KekNoun.get_by_id(randint(1, len(KekNoun)))
        if (sex == 'М'):
            return rand_el.male
        else:
            return rand_el.feminine

    class Meta:
        table_name = 'KekNoun'

class KekAdjective(BaseModel):
    id = AutoField(column_name='ID', null=False)
    male = TextField(column_name='Male', unique=True, null=False)
    feminine = TextField(column_name='Feminine', unique=True, null=False)

    def get_random(sex:str) -> str:
        """
        Возвращает рандомное прилагательное. Род задаётся параметром sex.

        sex -- 'М' или 'Ж' задаёт род прилагательного
        """
        rand_el = KekAdjective.get_by_id(randint(1, len(KekAdjective)))
        if (sex == 'М'):
            return rand_el.male
        else:
            return rand_el.feminine

    class Meta:
        table_name = 'KekAdjective'

def add_preferences_with_Member(member_in, level_in = 2):
    """
    Функция создаёт в таблице предпочтений (Preference) записи с id участника (member_in.id), id игры и уровнем level.
    В качестве id игры используются поочередно id всех игр, существующих в таблице Game.
    
    Предполагаемый сценарий использования: при добавлении в БД нового пользователя ему можно добавить предпочтения ко всем играм.
    Уровень предпочтения для всех игр в таком случае окажется равным level_in (по умолчанию = 2, т.е. нейтральный)
    """
    for i_game in Game:
        Preference.insert(game= i_game.id, member= member_in.id, level= level_in).execute()

def add_preferences_with_Game(game_in, level_in = 2):
    """
    Функция создаёт в таблице предпочтений (Preference) записи с id игры (game_in.id), id участника и уровнем level.
    В качестве id участника используются поочередно id всех участников, существующих в таблице Member.
    
    Предполагаемый сценарий использования: при добавлении в БД новой игры с ней можно добавить предпочтения у всех участников.
    Уровень предпочтения этой игры для каждого участника таком случае окажется равным level_in (по умолчанию = 2, т.е. нейтральный)
    """
    for i_member in Member:
        Preference.insert(game= game_in.id, member= i_member.id, level= level_in).execute()

def choose_a_game(members:list[Member], srch_dur:int = None, srch_action:int = None, srch_convers:bool = None)->list[list[Game]]:
    """
    Функция находит игры, подходящие заданным критериям и участникам.

    Возвращает список списков, где:
        первый элемент содержит список игр, которые удовлетворяют всем критериям (будет пуст, если таких нет);
        
        второй элемент пока является пустым списком (нужен для последующих фич (актуально на 25.07)).
    """
    members_ids = []
    members_count = len(members)
    for member in members:
        members_ids.append(member.id)
    members_ids_str = ', '.join(map(str, members_ids))

    sql_str = f'SELECT DISTINCT Game.*\
                FROM (Preference JOIN Game on Preference.GameID = Game.ID) AS X\
                WHERE (X.MinAmount <= {members_count} AND X.MaxAmount >= {members_count})'
    if (srch_dur != None):
        sql_str += f' AND X.Duration = {srch_dur}'
    if (srch_action != None):
        sql_str += f' AND X.ActionType = {srch_action}'
    if (srch_convers != None):
        sql_str += f' AND X.IsConvers = {int(srch_convers)}'
    sql_str += f' AND NOT EXISTS(\
                        SELECT *\
                        FROM Preference AS Y\
                        WHERE X.ID = Y.GameID AND Y.MemberID in ({members_ids_str}) AND Level = 0\
                    )'

    query_prefered = Game.raw(sql=sql_str)
    query_not_prefered = []
    result = [query_prefered, query_not_prefered]

    return result