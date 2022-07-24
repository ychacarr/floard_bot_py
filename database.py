from peewee import *

DBFile = SqliteDatabase('./floardbase.db')

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

    @property
    def full_name(self):
        return f'{self.name} {self.surname}'

    class Meta:
        table_name = 'Member'

class Preference(BaseModel):
    game = ForeignKeyField(column_name='GameID', field='id', model=Game, null=True)
    level = IntegerField(column_name='Level', default=2)
    member = ForeignKeyField(column_name='MemberID', field='id', model=Member, null=True)

    class Meta:
        table_name = 'Preference'
        indexes = (
            (('member', 'game'), True),
        )
        primary_key = CompositeKey('game', 'member')

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