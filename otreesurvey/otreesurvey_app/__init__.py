from otree.api import *
import json

doc = """
Your app description
"""

max_length=30

def distance(a,b):
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5

class C(BaseConstants): 
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    LIKERT11 = list(range(0,11)) + [-999]
    LIKERT5_string = ["Strongly\nAgree","Agree","Neutral","Disagree","Strongly\nDisagree"] + ["Refuse/Don't know"]
    LIKERT5_string = [
        (1, 'Strongly agree'),
        (2, 'Agree'),
        (3, 'Neutral'),
        (4, 'Disagree'),
        (5, 'Strongly disagree'),
        (-999, "----Refuse/Don't know----"),
    ]
    LIKERT5 = [1,2,3,4,5] + [-999]
    SLIDER = list(range(0,101)) +  [-999]
    QUESTIONS_SC =["climate_concern", 
                   "gay_adoption", 
                    "migration_enriches_culture",
                   "govt_reduce_inequ"]
    questiontext = [
        'I am very concerned about climate change.', 
        'Gay and lesbian couples should have the same rights to adopt children as couples consisting of a man and a woman.', 
        'It is enriching for cultural life in Germany when migrants come here.', 
        'The state should take measures to reduce income differences more than before.'
        ]
    QUESTIONS =questiontext# [f"{q} (1 agree strongly - 7 disagree strongly)" for q in  questions]
    CHECKTEXT = lambda which: f"To what extent does this actually reflect your perception of political similarity?"
    REASONTEXT ="Please briefly describe why (in two to three sentences)" 
    NFRIENDS = 3
    NPS = 4
    P_OPS =  {
    "P1": [0,0, 0,-1],  # LIB
    "P2": [0, -1, 0, -1], # climate-hoax RIGHT 
    "P3": [1, 1, 1, 1], # LEFT
    "P4": [0,  0, -1, 0], # RIGHT
    }
    c = "worried about climate change."
    g = "equal rights to adopt children for gay/lesbian couples."
    m = "migration enriches cultural life in Germany."
    i = "more state measures to reduce income differences."
    P_OP_RESPONSE = {"climate_concern": 
                     {-1: "is not at all "+c, 0:"is somewhat "+c, 1:"is extremely "+c},"gay_adoption": 
                     {-1: "strongly disapproves "+g, 0:"is neutral about "+g, 1:"strongly approves "+g}, 
                     "migration_enriches_culture":
                     {-1: "strongly disagrees that "+m, 0:"has a neutral position on whether "+m, 1:"strongly agrees that "+m}, 
                     "govt_reduce_inequ": 
                     {-1: "strongly opposes "+i, 0:"is neutral about "+i, 1:"strongly supports "+i}
                    }

    # NEW: QUESTIONS
    MAIN_QUESTION_1 = "Some countries are implementing a tax on CO₂ to combat climate change. Do you have any thoughts on such a proposal?"

    FOLLOWUP_QUESTIONS = [
        "Tell me more about why you think so.",
        "What do you think that some of your social contacts think about this?",
        "What do you think the party that you feel closest to thinks about such a proposal?",
        "Is there anything that would change your mind about this issue?",
    ]

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


def make_field(label):
    return models.StringField(
        choices=C.LIKERT5_string,
        label=label,
        widget=widgets.RadioSelect,
    )

def make_slider(label):
    return models.IntegerField(
        choices=C.SLIDER,
        label=label,
        widget=widgets.RadioSelectHorizontal,
    )

def define_friend(label):
    return  models.LongStringField(label=label)


class Player(BasePlayer):
    age = models.IntegerField(label='How old are you?', min=18, max=100)
    feel_closest = models.StringField(label='Do you feel yourself closer to one of the political parties than the others?',
                                     choices=["yes", "no", "refuse to say"],
                                     widget=widgets.RadioSelectHorizontal)
    feel_closest_party = models.StringField(label='Which party do you feel closest to?',
                                     choices=["CDU/CSU", "AfD", "SPD", "Grüne", "Linke", "BSW", "FDP", "other", "refuse to say"],
                                     widget=widgets.RadioSelectHorizontal, 
                                     blank=True)
    how_polarised = models.StringField(label='People sometimes say that the public polarises on political issues. Would you agree?',
                                     choices=["Strongly Agree", "Somewhat Agree", "Somewhat Disagree", "Strongly Disagree"],
                                     widget=widgets.RadioSelect)
    
    #################################
    #####  OWN POLITICAL OPINIONS   #####
    #################################
    own_climate_concern= make_field(C.QUESTIONS[0])
    own_gay_adoption= make_field(C.QUESTIONS[1])
    own_govt_reduce_inequ=  make_field(C.QUESTIONS[2])
    own_migration_enriches_culture=  make_field(C.QUESTIONS[3])

    #################################
    #####  MAP POSITIONS   #####
    #################################
    positionsTest = models.LongStringField()  # Stores JSON data of positions
    positions = models.LongStringField()  # Stores JSON data of positions
    edges = models.LongStringField()  # Added for edges

    #################################
    #####  CHecks   #####
    #################################
    for toCheck in ["f1f2", "P1P2"]:
        exec(f"check_self_{toCheck} = models.StringField(        choices=['not at all','somewhat','very much'],label=C.CHECKTEXT('your friends'),widget=widgets.RadioSelectHorizontal,blank=True)")
        exec(f"reason_{toCheck} =  models.LongStringField(label=C.REASONTEXT)")
    del toCheck

    isTrainingPassed = models.BooleanField(initial=False)#
    isTrainingCondFvC = models.BooleanField(initial=False)#
    isTrainingCondSelfvFC = models.BooleanField(initial=False)#
    isTrainingCondSvFC = models.BooleanField(initial=False)#
    trainingMessageConfirmed = models.BooleanField(initial=False)#
    isTrainingCondSvF = models.BooleanField(initial=False)#
    current_friend = models.IntegerField(initial=1)  
    ps_placed = models.IntegerField(initial=0)  
    
    # for questions
    main_q1_response = models.LongStringField(label="", blank=False)  # Will use dynamic label
    q1_followup1 = models.LongStringField(label="", blank=False)
    q1_followup2 = models.LongStringField(label="", blank=False)
    q1_followup3 = models.LongStringField(label="", blank=False)
    q1_followup4 = models.LongStringField(label="", blank=False)

    # labels
    label_1 = models.StringField(
        label="", 
        blank=False,
        max_length=max_length)
    label_2 = models.StringField(
        label="", 
        blank=True,
        max_length=max_length)
    label_3 = models.StringField(
        label="", 
        blank=True,
        max_length=max_length)
    label_4 = models.StringField(
        label="", 
        blank=True,
        max_length=max_length)
    label_5 = models.StringField(
        label="", 
        blank=True,
        max_length=max_length)

#################################
#####  FRIENDS' POLITICAL OPINIONS   #####
#################################
for f in range(1,C.NFRIENDS+1):
    setattr(Player, f"friend{f}", define_friend(f"Contact {f}"))
    for q in C.QUESTIONS_SC:
        setattr(Player, f"f{f}_{q}", make_field(''))

for f in ["GreenVoter", "AfDVoter"]:
    for q in C.QUESTIONS_SC:
        setattr(Player, f"{f}_{q}", make_field(''))

# PAGES
class Introduction(Page):
    pass

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'feel_closest', 'feel_closest_party', "how_polarised"]

class Friends(Page):
    form_model = 'player'
    form_fields = [f"friend{n}" for n in range(1, C.NFRIENDS+1)]

    @staticmethod
    def vars_for_template(player:Player):
        return {"nfriends":C.NFRIENDS}

class FriendOpinions(Page):
    form_model = "player"
    @staticmethod
    def get_form_fields(player):
        return [f"f{player.current_friend}_{q}" for q in C.QUESTIONS_SC]
        
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.current_friend +=1

    @staticmethod
    def vars_for_template(player):
        # d = {f'question_{q_sc}': q for q_sc, q in zip(C.QUESTIONS_SC, C.QUESTIONS)}
        d = {"friend_name": getattr(player, f"friend{player.current_friend}")}
        d["fields"] = [f"f{player.current_friend}_{q}" for q in C.QUESTIONS_SC]
        d["questions"] = C.questiontext
        d["field_question_pairs"] = list(zip(d["fields"], d["questions"]))
        return d

    @staticmethod
    def is_displayed(player):
        return player.current_friend <= C.NFRIENDS  

class Green_Opinions(Page):
    form_model = 'player'
    form_fields =  [f"GreenVoter_{q}" for q in C.QUESTIONS_SC]
    @staticmethod
    def vars_for_template(player: Player): 
        return {f'question_{q_sc}': q for q_sc, q in zip(C.QUESTIONS_SC, C.QUESTIONS)}
   
class AfD_Opinions(Page):
    form_model = 'player'
    form_fields = [f"AfDVoter_{q}" for q in C.QUESTIONS_SC]
    @staticmethod
    def vars_for_template(player: Player): 
        return {f'question_{q_sc}': q for q_sc, q in zip(C.QUESTIONS_SC, C.QUESTIONS)}
   

class Opinions(Page):
    form_model = 'player'
    form_fields = [f"own_{q}" for q in C.QUESTIONS_SC]
    @staticmethod
    def vars_for_template(player: Player): 
        return {f'question_{q_sc}': q for q_sc, q in zip(C.QUESTIONS_SC, C.QUESTIONS)}


class MapTest(Page):
    form_model = 'player'
    form_fields = ['positionsTest']  # Store the final positions
   
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.positionsTest = player.positionsTest
        pos = json.loads(player.positionsTest)
        pos = {p["label"]: [p["x"], p["y"]] for p in pos}
        #calculate distances
        dF = distance(pos["self"], pos["F"])
        dC = distance(pos["self"], pos["C"])
        dS = distance(pos["self"], pos["S"])
        dFS = distance(pos["F"], pos["S"])
        dFC = distance(pos["F"], pos["C"])
        dCS = distance(pos["C"], pos["S"])
        # check conditions
        player.isTrainingCondFvC = bool(dF<dC)  # Rule 2/3
        player.isTrainingCondSelfvFC = bool(dFC>dC)  # Rule 4
        player.isTrainingCondSvF = bool(dS>dF) # Rule 5
        player.isTrainingCondSvFC = bool((dFS<dS) and (dCS<dS)) # Rule 6.
        isTrainingPassed = player.isTrainingCondFvC & player.isTrainingCondSelfvFC & player.isTrainingCondSvFC & player.isTrainingCondSvF
        player.isTrainingPassed = isTrainingPassed
    
    @staticmethod
    def is_displayed(player):
        return not player.isTrainingPassed 
    

class MapTestResult(Page):
    @staticmethod
    def vars_for_template(player: Player):
        passedMsg = "Well done! Your arrangement fulfills all the criteria. Below we show another possible example of an arrangement that accurately describes the scenario."
        errors = ""
        errors += r"The distance between self and C should be larger than the distance between self and F (bullet points 2/3). <br>" if player.isTrainingCondFvC==0 else ""
        errors += r"The distance between F and C should be larger than the distance between self and C (bullet point 4). <br>" if player.isTrainingCondSelfvFC==0 else ""
        errors += r"The distance between self and S should be larger than the distance between self and F (bullet point 5). <br>" if player.isTrainingCondSvF==0 else ""
        errors += r"The distances between F and S and between C and S should be smaller than the distance between self and S (bullet point 6). <br>" if player.isTrainingCondSvFC==0 else ""
        
        failedMsg=fr"Your arrangement does not meet all parts of the description: <br>  <br> {errors} <br>"+\
        "Please repeat the training and try to arrange the dots so that all criteria are fulfilled. You can see one possible arrangement that fulfills all the criteria below."
        if player.isTrainingPassed:
            player.trainingMessageConfirmed = True
        return {"isTrainingPassedMsg": passedMsg if player.isTrainingPassed else failedMsg} 
    @staticmethod
    def is_displayed(player: Player):
        return not player.trainingMessageConfirmed or not player.isTrainingPassed

class MapE(Page):
    form_model = 'player'
    form_fields = ['positions', 'edges']

    @staticmethod
    def vars_for_template(player: Player):
        labels = [
            player.label_1,
            player.label_2,
            player.label_3,
            player.label_4,
            player.label_5,
        ]
        # Filter and assign x/y positions
        belief_points = [
        {"label": label, "x": 750, "y": 100 + i * 80}  # 750 is just beyond 700px canvas
        for i, label in enumerate(labels) if label
        ]

        return dict(belief_points=belief_points)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.positions = player.positions
        player.edges = player.edges


class Map(Page):
    form_model = 'player'
    form_fields = ['positions']  # Store the final positions
    
    @staticmethod
    def vars_for_template(player: Player):
        return {f"friend{f}": getattr(player, f"friend{f}") for f in range(1, C.NFRIENDS+1)}
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.positions = player.positions

class MapP(Page):
    form_model = 'player'
    form_fields = ['positions']  # Store the final positions
    
    @staticmethod
    def vars_for_template(player: Player):
        d = {f"friend{f}": getattr(player, f"friend{f}") for f in range(1, C.NFRIENDS+1)}
        d["currentP"] = player.ps_placed+1
        d["img_source"] = f"P{d['currentP']}_ops.png"
        P = f"P{d['currentP']}"
        P_op = C.P_OPS[P]
        P_op_text= f"{P} "+f" {P} ".join([C.P_OP_RESPONSE[q][P_op[n]] for n, q in enumerate(C.QUESTIONS_SC)])
        d["P_op_text"] =P_op_text
        
        pos = json.loads(player.positions)
        pos = {p["label"]: [p["x"], p["y"]] for p in pos}
        for f in ["self"]+[f"friend{f}" for f in range(1, C.NFRIENDS+1)]+["GreenVoter", "AfDVoter"]+[f"P{p}" for p in range(1,5)]:
            p = pos[f] if not "friend" in f else pos[getattr(player, f"friend{f[-1]}")]
            d[f"pos_{f}_x"] = p[0]
            d[f"pos_{f}_y"] = p[1]

            if f==f"P{d['currentP']}":
                d[f"pos_{f}_x"] = 0 + 10*int(f[-1])
                d[f"pos_{f}_y"] = 0+ 10*int(f[-1])
        return d
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.positions = player.positions
        player.ps_placed += 1

    @staticmethod
    def is_displayed(player):
        return player.ps_placed <= C.NFRIENDS  

class CheckDistance(Page):
    form_model = 'player'
    form_fields = ['check_self_f1f2', "reason_f1f2", "check_self_P1P2", "reason_P1P2"]
    
    @staticmethod
    def vars_for_template(player: Player):
        pos = json.loads(getattr(player, f"positions"))
        pos = {p["label"]: [p["x"], p["y"]] for p in pos}
        isDistF1LargerDistF2 = distance(pos["self"], pos[player.friend1]) > distance(pos["self"], pos[player.friend2])
        isDistP1LargerDistP2 = distance(pos["self"], pos["P1"]) > distance(pos["self"], pos["P2"])
        distantFriend = player.friend1 if isDistF1LargerDistF2 else player.friend2
        similarFriend = player.friend2 if isDistF1LargerDistF2 else player.friend1
        distantP = "P1" if isDistP1LargerDistP2 else "P2"
        similarP = "P2" if isDistP1LargerDistP2 else "P1"
        return {
            'distantFriend': distantFriend,
            'similarFriend': similarFriend,
            'distantP': distantP,
            'similarP': similarP,
        }
    

class ResultsWaitPage(WaitPage):
    pass

class Results(Page):
    pass

### classes for question pages ###
class QuestionMain1(Page):
    form_model = 'player'
    form_fields = ['main_q1_response']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.MAIN_QUESTION_1)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        print("Main response:", player.main_q1_response)


class QuestionFollow1(Page):
    form_model = 'player'
    form_fields = ['q1_followup1']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.FOLLOWUP_QUESTIONS[0])


class QuestionFollow2(Page):
    form_model = 'player'
    form_fields = ['q1_followup2']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.FOLLOWUP_QUESTIONS[1])


class QuestionFollow3(Page):
    form_model = 'player'
    form_fields = ['q1_followup3']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.FOLLOWUP_QUESTIONS[2])


class QuestionFollow4(Page):
    form_model = 'player'
    form_fields = ['q1_followup4']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.FOLLOWUP_QUESTIONS[3])

class LabelingPage(Page):
    form_model = 'player'
    form_fields = ['label_1', 'label_2', 'label_3', 'label_4', 'label_5']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            main_question=C.MAIN_QUESTION_1,
            main_answer=player.main_q1_response,
            followups=list(zip(C.FOLLOWUP_QUESTIONS, [
                player.q1_followup1,
                player.q1_followup2,
                player.q1_followup3,
                player.q1_followup4
            ]))
        )
        
        
# ah wow that is pretty wild.
# MapTest + MapTestResult is the test phase (kind of actually makes sense.)
#  +[MapTest, MapTestResult] * 5
page_sequence = [
    Introduction, 
    QuestionMain1, 
    QuestionFollow1,
    QuestionFollow2,
    QuestionFollow3,
    QuestionFollow4,
    LabelingPage,
    MapE,
    Demographics,
    Results]
#page_sequence = [Introduction, Opinions, Friends]+[FriendOpinions]*C.NFRIENDS+[Green_Opinions, AfD_Opinions] +[MapE] +[Map]+[MapP]*C.NPS+[CheckDistance, Demographics, Results]

# pages we need: 
# 1. Introduction