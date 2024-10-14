from price_game_app import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'price_game_app2'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 8
    min_price = 1
    max_price = 10
    market = 60


class Subsession(BaseSubsession):
   pass


class Group(BaseGroup):
    round_payoff = models.CurrencyField()
    low_price = models.CurrencyField()

    @staticmethod
    def set_payoff(group):
        p1, p2 = group.get_players()
        if group.round_number > 1: # for every round after the frist one  
            if  group.round_number % 2 == 0: # to make shure the pricing is switching between p1 and p2 every round
                p_prev_round = p2.in_round(p2.round_number - 1) # get the player of the round before
                p_this_round = p1
                p_passive = p2
            else:
                p_prev_round = p1.in_round(p1.round_number - 1)
                p_this_round = p2
                p_passive = p1

            low_price = min(p_this_round.set_price, p_prev_round.set_price)
            group.low_price = low_price

            if low_price == p_this_round.set_price and p_this_round.set_price < p_prev_round.set_price:
                group.round_payoff = low_price * C.market
                p_this_round.payoff = group.round_payoff
            elif low_price == p_prev_round.set_price and p_prev_round.set_price < p_this_round.set_price:
                group.round_payoff = low_price * C.market
                p_passive.payoff = group.round_payoff

            else:
                group.round_payoff = low_price * C.market / 2
                p1.payoff = group.round_payoff
                p2.payoff = group.round_payoff
            
        else : # this is for the first round only
            low_price = min(p1.set_price, p2.set_price) 
            group.low_price = low_price
            if low_price == p1.set_price and p1.set_price < p2.set_price:
                group.round_payoff = low_price * C.market
                p1.payoff = group.round_payoff
            elif low_price == p2.set_price and p2.set_price < p1.set_price:
                group.round_payoff = low_price * C.market
                p2.payoff = group.round_payoff
            else:
                group.round_payoff = low_price * C.market / 2
                p1.payoff = group.round_payoff
                p2.payoff = group.round_payoff

      
            

class Player(BasePlayer):
    set_price = models.IntegerField( 
        min = C.min_price,
        max = C.max_price,
        label = "For which price do you want to sell your Product?"
    )
