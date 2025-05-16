from otree.api import *
import json
from .llm_utils import *
import json

doc = """
Your app description
"""

max_length=30
MAX_NODES=20

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
    QUESTIONS = [
        "Some countries are implementing a tax on CO₂ to combat climate change. Do you have any thoughts on such a proposal?",
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
    # demography page 
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
    #own_climate_concern= make_field(C.QUESTIONS[0])
    #own_gay_adoption= make_field(C.QUESTIONS[1])
    #own_govt_reduce_inequ=  make_field(C.QUESTIONS[2])
    #own_migration_enriches_culture=  make_field(C.QUESTIONS[3])

    # map positions
    # positionsTest = models.LongStringField()  # Stores JSON data of positions
    positions = models.LongStringField()  # Stores JSON data of positions
    edges = models.LongStringField()  # Added for edges

    #################################
    #####  CHecks   #####
    #################################
    #for toCheck in ["f1f2", "P1P2"]:
    #    exec(f"check_self_{toCheck} = models.StringField(        choices=['not at all','somewhat','very much'],label=C.CHECKTEXT('your friends'),widget=widgets.RadioSelectHorizontal,blank=True)")
    #    exec(f"reason_{toCheck} =  models.LongStringField(label=C.REASONTEXT)")
    #del toCheck

    isTrainingPassed = models.BooleanField(initial=False)#
    isTrainingCondFvC = models.BooleanField(initial=False)#
    isTrainingCondSelfvFC = models.BooleanField(initial=False)#
    isTrainingCondSvFC = models.BooleanField(initial=False)#
    trainingMessageConfirmed = models.BooleanField(initial=False)#
    isTrainingCondSvF = models.BooleanField(initial=False)#
    current_friend = models.IntegerField(initial=1)  
    ps_placed = models.IntegerField(initial=0)  
    
    # for questions
    answer1 = models.LongStringField(label="", blank=False)  # Will use dynamic label
    answer2 = models.LongStringField(label="", blank=False)
    answer3 = models.LongStringField(label="", blank=False)
    answer4 = models.LongStringField(label="", blank=False)
    answer5 = models.LongStringField(label="", blank=False)

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
    
    # LLM stuff
    prompt_used = models.LongStringField(blank=True)
    llm_result = models.LongStringField(blank=True)
    generated_nodes = models.LongStringField(blank=True)
    accepted_nodes = models.LongStringField(blank=True)

# Maximum number of generated nodes
for i in range(MAX_NODES):  
    setattr(Player, f"node_{i}", models.BooleanField(label="", blank=True))

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
        
class ResultsWaitPage(WaitPage):
    pass

class Results(Page):
    pass

### classes for question pages ###
class Question1(Page):
    form_model = 'player'
    form_fields = ['answer1']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.QUESTIONS[0])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        print("Main response:", player.answer1)


class Question2(Page):
    form_model = 'player'
    form_fields = ['answer2']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.QUESTIONS[1])


class Question3(Page):
    form_model = 'player'
    form_fields = ['answer3']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.QUESTIONS[2])


class Question4(Page):
    form_model = 'player'
    form_fields = ['answer4']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.QUESTIONS[3])


class Question5(Page):
    form_model = 'player'
    form_fields = ['answer5']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.QUESTIONS[4])

class LabelingPage(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        return [f"label_{i+1}" for i in range(len(C.QUESTIONS))]

    @staticmethod
    def vars_for_template(player: Player):
        qa_pairs = list(zip(C.QUESTIONS, [getattr(player, f"answer{i+1}") for i in range(len(C.QUESTIONS))]))
        formfields = [f"label_{i+1}" for i in range(len(C.QUESTIONS))]
        return dict(qa_pairs=qa_pairs, formfields=formfields)


class LLMGenerate(Page):
    timeout_seconds = 300
    auto_submit = True

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not player.field_maybe_none('generated_nodes'):
            questions_answers = {
                C.QUESTIONS[i]: getattr(player, f"answer{i+1}")
                for i in range(len(C.QUESTIONS))
            }

            prompt = make_node_prompt(questions_answers)
            player.prompt_used = prompt

            print("📜 Prompt:\n", prompt)
            print("🔑 API KEY:", os.getenv("OPENAI_API_KEY"))

            try:
                llm_nodes = call_openai(
                    NodeModelList,
                    prompt)
            except Exception as e:
                print("❌ LLM call failed:", e)
                llm_nodes = []

            llm_nodes = json.loads(llm_nodes.model_dump_json(indent=2))
            llm_nodes = llm_nodes['results']
            
            # save this here 
            player.llm_result = json.dumps(llm_nodes)

            # here only the nodes
            generated_nodes = [x['stance'] for x in llm_nodes]
            generated_nodes = [s.replace("I agree with the following: ", "", 1).strip() for s in generated_nodes]
            player.generated_nodes = json.dumps(generated_nodes)


class LLMReview(Page):
    form_model = 'player'
    form_fields = [f'node_{i}' for i in range(MAX_NODES)]

    @staticmethod
    def vars_for_template(player: Player):
        beliefs = json.loads(player.generated_nodes)
        zipped_beliefs = list(zip(beliefs, [f'node_{i}' for i in range(len(beliefs))]))
        return dict(zipped_beliefs=zipped_beliefs)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        beliefs = json.loads(player.generated_nodes)
        accepted = []
        for i, belief in enumerate(beliefs):
            if i >= MAX_NODES:
                break
            if getattr(player, f'node_{i}'):  # if True (Accepted)
                accepted.append(belief)
        player.accepted_nodes = json.dumps(accepted)
        

class MapLLM(Page):
    form_model = 'player'
    form_fields = ['positions', 'edges']

    @staticmethod
    def vars_for_template(player: Player):
        accepted_nodes = json.loads(player.accepted_nodes)
        # Filter and assign x/y positions
        belief_points = [
        {"label": label, "x": 750, "y": 100 + i * 80}  # 750 is just beyond 700px canvas
        for i, label in enumerate(accepted_nodes) if label
        ]

        return dict(belief_points=belief_points)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.positions = player.positions
        player.edges = player.edges
        
# ah wow that is pretty wild.
page_sequence = [
    Introduction, 
    Question1, 
    Question2,
    Question3,
    Question4,
    Question5,
    LLMGenerate, # LabelingPage
    LLMReview, # LabelingPage
    MapLLM, #MapE,
    Demographics,
    Results]

# page_sequence = [Introduction, Question1, Question2, Question3, Question4, Question5, LabelingPage, MapE, ...]