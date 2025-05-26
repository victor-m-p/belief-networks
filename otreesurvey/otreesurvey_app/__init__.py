from otree.api import *
import json
from .llm_utils import *
import json
import random

doc = """
Your app description
"""

class C(BaseConstants): 
    
    # not sure we need this 
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    
    NEW_LABELS_PER_PAGE = 1 # minimum number of new labels per page.

    # meta-variables
    MAX_NODES=20
    MAX_CHAR=60
    
    QUESTIONS = [
        "How do you place yourself politically? Would you call yourself a conservative or a liberal or something else? What does this mean to you?",
        "Which party did you vote for at the last national election, and why did you vote for that party? If you did not vote in the last national election, why?", 
        "What are some things that concern you in the political domain? Feel free to mention things that are important to you personally, or more long-term concerns or challenges for your country",
        "Are there things about your country that make you feel proud or ashamed? Feel free to write about any features or events that come to mind",
        "Are there any more things that are important to you politically that we have not yet discussed? Feel free to write about anything that comes to mind",
        #"Are there any political questions where you feel dissonance or conflict? Either because you are not quite sure yourself, or because you disagree with some of your social contacts?"
    ]
    
    N_QUESTIONS = len(QUESTIONS)

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

    # map positions
    # positionsTest = models.LongStringField()  # Stores JSON data of positions
    positions = models.LongStringField()  # Stores JSON data of positions
    edges = models.LongStringField()  # Added for edges
    
    # for questions 
    answer1 = models.LongStringField(label="", blank=False)  # Will use dynamic label
    answer2 = models.LongStringField(label="", blank=False)
    answer3 = models.LongStringField(label="", blank=False)
    answer4 = models.LongStringField(label="", blank=False)
    answer5 = models.LongStringField(label="", blank=False)
    
    # LLM stuff
    prompt_used = models.LongStringField(blank=True)
    llm_result = models.LongStringField(blank=True)
    generated_nodes = models.LongStringField(blank=True)
    accepted_nodes = models.LongStringField(blank=True)

    # For new way of doing belief codings (humans)
    # Currently we are not doing these human labels.
    label_input_0 = models.StringField(blank=True)
    label_input_1 = models.StringField(blank=True)
    label_input_2 = models.StringField(blank=True)
    label_input_3 = models.StringField(blank=True)

    all_labels_json = models.LongStringField(initial='[]')  # final flat list
    label_snapshots = models.LongStringField(initial='[]')  # list of lists

    # Plausibility check (not implemented yet)
    importance_pair_1 = models.IntegerField(
    label="",
    choices=[1, 2, 3, 4, 5, 6, 7],
    widget=widgets.RadioSelectHorizontal
    )
    importance_pair_2 = models.IntegerField(
        label="",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal
    )
    importance_pairs_data = models.LongStringField()

for i in range(C.MAX_NODES):
    setattr(Player, f"node_choice_{i}", models.StringField(blank=True))
    setattr(Player, f"node_modify_text_{i}", models.StringField(blank=True))
    setattr(Player, f"node_reject_reason_{i}", models.StringField(blank=True))
    #setattr(Player, f"LLM_proposed_{i}", models.StringField(blank=True))
    setattr(Player, f"LLM_codings_{i}", models.StringField(blank=True))
    setattr(Player, f"LLM_accepted_{i}", models.StringField(blank=True))
    setattr(Player, f"Human_nodes_{i}", models.StringField(blank=True))
    setattr(Player, f"Final_nodes_{i}", models.StringField(blank=True))

# PAGES
class Introduction(Page):
    pass

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'feel_closest', 'feel_closest_party', "how_polarised"]

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

# new version of above.
class LLMReviewRevise(Page):
    form_model = 'player'

    def get_form_fields(self):
        beliefs = json.loads(self.generated_nodes)
        fields = []
        for i in range(len(beliefs)):
            fields.append(f'node_choice_{i}')
            fields.append(f'node_modify_text_{i}')
            fields.append(f'node_reject_reason_{i}')
        return fields

    def error_message(self, values):
        beliefs = json.loads(self.generated_nodes)

        for i in range(len(beliefs)):
            choice = values.get(f'node_choice_{i}')
            if not choice:
                return "Please evaluate all beliefs before continuing."

            if choice == 'MODIFY':
                mod_text = values.get(f'node_modify_text_{i}', '').strip()
                if not mod_text:
                    return "Please provide modified text for all items marked as MODIFY."
            
    def vars_for_template(self):
        beliefs = json.loads(self.generated_nodes)
        zipped_beliefs = list(zip(beliefs, range(len(beliefs))))
        return dict(zipped_beliefs=zipped_beliefs)

    def before_next_page(self, timeout_happened):
        beliefs = json.loads(self.generated_nodes)

        for i, belief in enumerate(beliefs):
            choice = getattr(self, f'node_choice_{i}', '')
            modify_text = getattr(self, f'node_modify_text_{i}', '').strip()
            reject_reason = getattr(self, f'node_reject_reason_{i}', '').strip()

            if choice == "ACCEPT":
                setattr(self, f"LLM_codings_{i}", "ACCEPT")
                setattr(self, f"LLM_accepted_{i}", belief)

            elif choice == "REJECT":
                reason = f"REJECT: {reject_reason}" if reject_reason else "REJECT"
                setattr(self, f"LLM_codings_{i}", reason)

            elif choice == "MODIFY" and modify_text:
                setattr(self, f"LLM_codings_{i}", f"MODIFY: {modify_text}")
                setattr(self, f"LLM_accepted_{i}", modify_text)
        
class MapLLM(Page):
    form_model = 'player'
    form_fields = ['positions', 'edges']

    @staticmethod
    def vars_for_template(player: Player):
        accepted_nodes = json.loads(player.accepted_nodes)
        mode = 'all'  # 'sequential', 'all'
        label_display = 'always' # 'hover', 'always' --- hover + list of numbers. 

        if mode == 'all':
            belief_points = [
                {"label": label, "x": 750, "y": 100 + i * 80}
                for i, label in enumerate(accepted_nodes) if label
            ]
        else:
            belief_points = []  # empty, will render first node via JS
        return dict(
            belief_points=belief_points,
            mode=mode,
            label_display=label_display,
            all_labels_json=json.dumps(accepted_nodes)  # still safe
        )

class PlausibilityCheck(Page):
    form_model = 'player'
    form_fields = ['importance_pair_1', 'importance_pair_2']

    @staticmethod
    def vars_for_template(player):
        all_nodes = json.loads(player.positions)
        labels = [node['label'] for node in all_nodes]
        random.shuffle(labels)
        chosen = labels[:4]

        pair_1 = (chosen[0], chosen[1])
        pair_2 = (chosen[2], chosen[3])

        # Save pairs for display in HTML and record-keeping
        player.importance_pairs_data = json.dumps({
            "pair_1": pair_1,
            "pair_2": pair_2
        })

        return dict(pair_1=pair_1, pair_2=pair_2)

# page sequence 
page_sequence = [
    Introduction, 
    Question1, 
    Question2, 
    Question3, 
    Question4, 
    Question5, 
    LLMGenerate,
    LLMReviewRevise,
    MapLLM, 
    Demographics, 
    Results
]