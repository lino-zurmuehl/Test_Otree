from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'price_game_app'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
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
        if group.round_number > 1: # For every round after the frist one  
            if  group.round_number % 2 == 0: # To make shure the pricing is switching between p1 and p2 every round
                p_prev_round = p2.in_round(p2.round_number - 1) # Get the player of the round before
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
    def get_previous_set_price(self):
        if self.round_number > 1:
            return self.in_round(self.round_number - 1).field_maybe_none('set_price')
        return None  



# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class InitialPricing(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.id_in_group == 1 
    
    form_model = 'player'
    form_fields = ['set_price']


class Pricing(Page):
    @staticmethod
    def is_displayed(player):
        if player.round_number % 2 == 0:
            return player.id_in_group == 1 # Only showing this page to the player whos turn it is to set the pricing
        else:
            return player.id_in_group == 2
        
    form_model = 'player'
    form_fields = ['set_price']

    @staticmethod
    def vars_for_template(player):
        other_player = player.get_others_in_group()[0]
        if player.round_number > 1:  
            previous_round = other_player.in_round(other_player.round_number - 1)
            pricing_other = previous_round.set_price
        else : 
            pricing_other = other_player.field_maybe_none('set_price')
        return {
            'pricing_other': pricing_other
        }

class WaitOtherPage(WaitPage):
    @staticmethod
    def is_displayed(player):
        if player.round_number % 2 == 0:
            return player.id_in_group == 1
        else:
            return player.id_in_group == 2

class WaitResultPage(WaitPage):
    @staticmethod 
    def after_all_players_arrive(group: Group): 
        group.set_payoff(group)

class RoundResults(Page): 
    @staticmethod
    def vars_for_template(self):
        previous_set_price = self.get_previous_set_price()
        return {
            'previous_set_price': previous_set_price,
        }

class GroupPage(WaitPage):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    group_by_arrival_time = True


class GameResults(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    
    @staticmethod
    def vars_for_template(self):
        total_payoff = self.participant.payoff
        return {
            'total_payoff': total_payoff,
        }

#FUNCTIONS
def group_by_arrival_time_method(subsession: Subsession, waiting_players):
    # Dictionary to keep track of potential groups
    d_grouping = {}

    # Iterate over waiting players
    for p in waiting_players:
        if 'past_group_members' not in p.participant.vars:
            p.participant.vars['past_group_members'] = []

        found_group = False 

        # Try to find a group for the player
        for group_id, players_in_my_group in d_grouping.items():
            # Ensure the group has fewer than 2 players before adding another one
            if len(players_in_my_group) < 2 and all(other_p.participant.id_in_session not in p.participant.vars['past_group_members'] for other_p in players_in_my_group):
                players_in_my_group.append(p)
                if len(players_in_my_group) == 2:  # If the group is full, finalize it
                    update_past_group_members(players_in_my_group)
                    return players_in_my_group
                found_group = True
                break

        # If no valid group is found, create a new group
        if not found_group:
            d_grouping[p.participant.id_in_session] = [p]

    if len(waiting_players) >= 2:
        for group in d_grouping.values():
            if len(group) == 2:  # Only return groups of 2 players
                update_past_group_members(group)
                return group

    return None  # No valid group found, continue waiting



def update_past_group_members(group):

    for p in group:
        if 'past_group_members' not in p.participant.vars:
            p.participant.vars['past_group_members'] = []

        for other_p in group:
            if p != other_p and other_p.participant.id_in_session not in p.participant.vars['past_group_members']:
                p.participant.vars['past_group_members'].append(other_p.participant.id_in_session)



page_sequence = [GroupPage, Introduction, InitialPricing, WaitOtherPage, Pricing, WaitResultPage, RoundResults, GameResults]

