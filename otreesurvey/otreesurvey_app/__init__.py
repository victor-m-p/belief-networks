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
    MAX_NODES=20
    MAX_CHAR=60
    MAX_USER_NODES=3
    
    QUESTIONS = [
        "How would you describe yourself politically? Would you call yourself a conservative or a liberal or something else? What does this mean to you?",
        #"Which party did you vote for at the last national election, and why did you vote for that party? If you did not vote in the last national election, why?", 
        "What are some things that concern you in the political domain? Feel free to mention things that are important to you personally, or more long-term concerns or challenges for your country",
        "Are there things about your country that make you feel proud or ashamed? Feel free to write about any features or events that come to mind",
        "Are there any political questions where you feel dissonance or conflict? Maybe something that is salient for you personally, or is discussed among your social contacts or in the media",
        "Are there any more things that are important to you politically that we have not yet discussed? Feel free to write about anything that comes to mind",
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
    gender = models.StringField(
        label='What is your gender?',
        choices=[
            "Female", 
            "Male", 
            "Non-binary", 
            "Prefer not to disclose", 
            "Other"],
        widget=widgets.RadioSelect
        )
    education = models.StringField(
        label='What is the highest level of school you have completed or the highest degree you have received?',
        choices=[
            "Less than high school degree", 
            "High school degree or equivalent (e.g., GED)",
            "Some college but no degree", 
            "Associate degree", 
            "Bachelor degree",
            "Graduate degree (e.g., Masters, PhD, M.D)"
            ],
        widget=widgets.RadioSelect
    )
    politics = models.StringField(
        label='How would you describe your political viewpoints?',
        choices=[
            "Very liberal",
            "Slightly liberal",
            "Moderate",
            "Slightly conservative",
            "Very conservative",
            "Prefer not to disclose"
            ],
        widget=widgets.RadioSelect
    )

    # map positions
    # this might now be outdated 
    positions = models.LongStringField()  # Stores JSON data of positions
    edges = models.LongStringField()  # Added for edges
    
    # for questions (can we make this smoother?)
    answer1 = models.LongStringField(label="", blank=False)  
    answer2 = models.LongStringField(label="", blank=False)
    answer3 = models.LongStringField(label="", blank=False)
    answer4 = models.LongStringField(label="", blank=False)
    answer5 = models.LongStringField(label="", blank=False)
    
    # LLM stuff
    prompt_used = models.LongStringField(blank=True)
    llm_result = models.LongStringField(blank=True)
    generated_nodes = models.LongStringField(blank=True)
    revised_beliefs = models.LongStringField(blank=True)
    final_nodes = models.LongStringField(blank=True)
    user_nodes = models.LongStringField(blank=True)

    # For new way of doing belief codings (humans)
    # Currently we are not doing these human labels.
    label_input_0 = models.StringField(blank=True)
    label_input_1 = models.StringField(blank=True)
    label_input_2 = models.StringField(blank=True)
    label_input_3 = models.StringField(blank=True)

    all_labels_json = models.LongStringField(initial='[]')  # final flat list
    label_snapshots = models.LongStringField(initial='[]')  # list of lists

    # Position/NETWORK 
    ## Stage 1.
    positions_1 = models.LongStringField(blank=True)
    ## Stage 2.
    edges_2 = models.LongStringField(blank=True)
    positions_2 = models.LongStringField(blank=True)
    ## stage 3 (what about size here??)
    edges_3 = models.LongStringField(blank=True)
    positions_3 = models.LongStringField(blank=True)
    
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
    
    ## QUESTIONNAIRE ## 
    # taken from: https://www.pewresearch.org/politics/quiz/political-typology/
    policy_1 = models.IntegerField(
        label="How much more, if anything, needs to be done to ensure equal rights for all Americans regardless of their racial or ethnic backgrounds?",
        choices=[[1, "A lot"], [2, "A little"], [3, "Nothing at all"]],
        widget=widgets.RadioSelect
    )

    policy_2 = models.IntegerField(
        label="If you had to choose, would you rather have…",
        choices=[[1, "A smaller government providing fewer services"], [2, "A bigger government providing more services"]],
        widget=widgets.RadioSelect
    )

    # this is just taken out of my ass 
    policy_3 = models.IntegerField(
        label="Climate change is a major threat to our way of life.",
        choices=[[1, "Strongly disagree"], [2, "Disagree"], [3, "Neutral"], [4, "Agree"], [5, "Strongly agree"]],
        widget=widgets.RadioSelect
    )
    
    ## judge network ## 
    network_reflection_rating = models.IntegerField(
        label="How well do you feel that this representation captures your political beliefs?",
        choices=[[1, "Not at all"], [2, "Slightly"], [3, "Moderately"], [4, "Very well"], [5, "Extremely well"]],
        widget=widgets.RadioSelectHorizontal
    )

    network_reflection_text = models.LongStringField(
        label="Please share your thoughts about the network representation of your beliefs above. Does it make sense for you to think about your beliefs in this way or does it feel weird? Are there any connections or beliefs that feel especially meaningful or maybe surprising?",
        blank=True
    )

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

class Demographics(Page): # what do we actually need here? 
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'politics']

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

    @staticmethod
    def get_form_fields(player):
        revised_raw = player.field_maybe_none('revised_beliefs') or '[]'
        revised = json.loads(revised_raw)
        fields = []
        for i in range(len(revised)):
            fields.append(f"node_choice_{i}")
            fields.append(f"node_reject_reason_{i}")
            fields.append(f"node_modify_text_{i}")
        return fields

    @staticmethod
    def vars_for_template(player):
        beliefs = json.loads(player.generated_nodes)
        try:
            revised = json.loads(player.revised_beliefs)
        except (TypeError, json.JSONDecodeError):
            revised = [
                {"belief": b, "user_action": "", "text_field": ""}
                for b in beliefs
            ]
            player.revised_beliefs = json.dumps(revised)

        return dict(belief_items=revised, C=C)

    @staticmethod
    def error_message(player, values):
        revised = json.loads(player.revised_beliefs)
        for i, item in enumerate(revised):
            choice = values.get(f"node_choice_{i}", "")
            reason = values.get(f"node_reject_reason_{i}", "")
            mod = values.get(f"node_modify_text_{i}", "")

            item['user_action'] = choice
            if choice == 'REJECT':
                item['text_field'] = reason
            elif choice == 'MODIFY':
                item['text_field'] = mod
            else:
                item['text_field'] = ""

        player.revised_beliefs = json.dumps(revised)

        for item in revised:
            if not item['user_action']:
                return "Please evaluate all beliefs before continuing."
            if item['user_action'] == 'MODIFY' and not item['text_field'].strip():
                return "Please provide modified text for all items marked as MODIFY."

    @staticmethod
    def before_next_page(player, timeout_happened):
        pass

class LLMAddBeliefs(Page):
    form_model = 'player'
    form_fields = ['user_nodes']

    @staticmethod
    def vars_for_template(player):
        revised = json.loads(player.revised_beliefs or '[]')
        accepted = []

        for item in revised:
            if item['user_action'] == 'ACCEPT':
                accepted.append({"text": item['belief'], "source": "ACCEPTED"})
            elif item['user_action'] == 'MODIFY':
                accepted.append({"text": item['text_field'], "source": "MODIFIED"})

        return dict(accepted_beliefs=accepted, C=C)

    @staticmethod
    def before_next_page(player, timeout_happened):
        revised = json.loads(player.revised_beliefs or '[]')
        accepted = []

        for item in revised:
            if item['user_action'] == 'ACCEPT':
                accepted.append({"text": item['belief'], "source": "ACCEPTED"})
            elif item['user_action'] == 'MODIFY':
                accepted.append({"text": item['text_field'], "source": "MODIFIED"})

        try:
            user_contributions = json.loads(player.user_nodes or '[]')
        except json.JSONDecodeError:
            user_contributions = []

        for node in user_contributions:
            if node.strip():
                accepted.append({"text": node.strip(), "source": "USER"})

        player.final_nodes = json.dumps(accepted)

# splitting network part up # 
class MapNodePlacement(Page):
    form_model = 'player'
    form_fields = ['positions_1']

    @staticmethod
    def vars_for_template(player):
        final_nodes = json.loads(player.final_nodes or '[]')
        belief_texts = [item['text'] for item in final_nodes if item.get('text')]

        belief_points = [
            {"label": label, "x": 750, "y": 40 + i * 60, "radius": 20}
            for i, label in enumerate(belief_texts)
        ]

        mode = 'all'
        label_display = 'always'

        return dict(
            belief_points=belief_points,
            belief_texts=belief_texts,
            mode=mode,
            label_display=label_display
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        pass

class MapEdgeCreation(Page):
    form_model = 'player'
    form_fields = ['positions_2', 'edges_2']

    @staticmethod
    def vars_for_template(player: Player):
        final_nodes = json.loads(player.final_nodes or '[]')
        try:
            positions = json.loads(player.positions_1 or '[]')
        except (TypeError, json.JSONDecodeError):
            positions = []

        belief_points = []
        for i, item in enumerate(final_nodes):
            x = positions[i]['x'] if i < len(positions) else 750
            y = positions[i]['y'] if i < len(positions) else 100 + i * 80
            radius = positions[i].get('radius', 20) if i < len(positions) else 20
            belief_points.append({"label": item['text'], "x": x, "y": y, "radius": radius})

        return dict(
            belief_points=belief_points,
            mode='all',
            label_display='always',
            all_labels_json=json.dumps([b['text'] for b in final_nodes])
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass


class MapImportance(Page):
    form_model = 'player'
    form_fields = ['positions_3', 'edges_3']

    @staticmethod
    def vars_for_template(player):
        prev_positions = json.loads(player.positions_2 or '[]')
        prior_edges = json.loads(player.edges_2 or '[]')

        return dict(
            belief_points=prev_positions,
            belief_edges=prior_edges,
            label_display='always'
        )

class NetworkReflection(Page):
    form_model = 'player'
    form_fields = ['network_reflection_rating', 'network_reflection_text']

    @staticmethod
    def vars_for_template(player):
        positions = json.loads(player.positions_3 or '[]')
        raw_edges = json.loads(player.edges_3 or '[]')

        # rename (could make this clearner.)
        edges = []
        for edge in raw_edges:
            edges.append({
                "from": edge["fromLabel"],
                "to": edge["toLabel"],
                "polarity": edge["polarity"]
            })

        return dict(
            belief_points=positions,
            belief_edges=edges,
            label_display='always'
        )

class PlausibilityImportance(Page):
    form_model = 'player'
    form_fields = ['importance_pair_1', 'importance_pair_2']

    @staticmethod
    def vars_for_template(player):
        all_nodes = json.loads(player.positions_3)
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

class PolicyQuestionnaire(Page):
    form_model = 'player'
    form_fields = ['policy_1', 'policy_2', 'policy_3']


# page sequence 
page_sequence = [
    Introduction, 
    # QUESTIONS 
    Question1, 
    Question2, 
    Question3, 
    Question4, 
    Question5, 
    # GENERATE + SELECT BELIEFS 
    LLMGenerate,
    LLMReviewRevise,
    LLMAddBeliefs,
    # PLACEMENT 
    MapNodePlacement,
    MapEdgeCreation,
    MapImportance,
    # PLAUSIBILITY 
    # PlausibilityImportance,
    # PlausibilityPosition, 
    # PlausibilityEdges
    # Face Validity 
    # FaceValidity, 
    # DEMOGRAPHICS 
    NetworkReflection,
    PolicyQuestionnaire,
    Demographics, 
    Results
]