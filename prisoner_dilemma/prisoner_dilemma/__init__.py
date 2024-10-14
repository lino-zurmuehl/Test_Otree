from otree.api import *  
  
doc = """This is a practice round of a prisoners dilemma"""  
  
class C(BaseConstants):  
    NAME_IN_URL = 'prisoner_dilemma'  
    PLAYERS_PER_GROUP = 2  
    NUM_ROUNDS = 1  
    payoff_matrix = {  
        'cooperate': {'cooperate': (3, 3), 'betray': (0, 5)},  
        'betray': {'cooperate': (5, 0), 'betray': (1, 1)}  
    }  
  
class Subsession(BaseSubsession):  
    pass  
  
class Group(BaseGroup):  # before i had it as a function in this class and called it in the ResultWaitPage but it didnt work
    @staticmethod
    def payoff_function(group):
        player_list = group.get_players() #what would be the best page to do this?
        p1 = player_list[0] 
        p2 = player_list[1]
        payoff_matrix = C.payoff_matrix  
        p1.payout = payoff_matrix[p1.decision][p2.decision][0]  
        p2.payout = payoff_matrix[p1.decision][p2.decision][1] 

class Player(BasePlayer):  
    decision = models.StringField(  
        label="Will you betray your partner or keep silent?",  
        choices=["betray", "cooperate"],  
        widget=widgets.RadioSelect,  
        doc="Player's Decision"  
    )  
    payout = models.CurrencyField()  # this worked only as payout not payoff bc payoff is already difined right?
  
# PAGES  
class Decision_Page(Page):  
    form_model = 'player'  
    form_fields = ['decision']  
  
class ResultsWaitPage(WaitPage):  
    @staticmethod  # why do we need staticmethod everytime?
    def after_all_players_arrive(group: Group):  #this i don't really get: Is there a smarter way to call the function? 
        group.payoff_function(group)
  
class Results(Page):  
    pass   
  
page_sequence = [Decision_Page, ResultsWaitPage, Results]  
