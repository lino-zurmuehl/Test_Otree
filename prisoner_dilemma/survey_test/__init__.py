from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'survey_test'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(label = 'Please enter your age')
    name = models.StringField(label = 'Please enter your name')
    german = models.BooleanField( label = 'Are you german?',
        choices = [
            [True,'German'],
            [False,'Other Nationality']
        ]

    )



# PAGES
class MyPage(Page):
    form_model = 'player' # can there also be another model here?
    form_fields = ['age', 'name', 'german']


class Results(Page):
    pass


page_sequence = [MyPage, Results]
