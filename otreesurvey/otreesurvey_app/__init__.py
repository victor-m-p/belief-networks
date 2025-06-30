from otree.api import *
import json
from .llm_utils import *
import random

doc = """
Your app description
"""

US_STATES = [
    'Not Applicable', 'Alaska', 'Alabama', 'Arkansas', 'Arizona',
    'California', 'Colorado', 'Connecticut', 'District of Columbia',
    'Delaware', 'Florida', 'Georgia', 'Hawaii',
    'Iowa', 'Idaho', 'Illinois', 'Indiana',
    'Kansas', 'Kentucky', 'Louisiana', 'Massachusetts',
    'Maryland', 'Maine', 'Michigan', 'Minnesota',
    'Missouri', 'Mississippi', 'Montana', 'North Carolina',
    'North Dakota', 'Nebraska', 'New Hampshire', 'New Jersey',
    'New Mexico', 'Nevada', 'New York', 'Ohio',
    'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
    'South Carolina', 'South Dakota', 'Tennessee', 'Texas',
    'Utah', 'Virginia', 'Vermont', 'Washington',
    'Wisconsin', 'West Virginia', 'Wyoming']

def smart_linebreak(text, threshold=15):
    if len(text) <= threshold:
        return text
    mid = len(text) // 2
    right = text.find(' ', mid)
    left = text.rfind(' ', 0, mid)
    if right == -1 and left == -1:
        split_point = mid  
    elif right == -1:
        split_point = left
    elif left == -1:
        split_point = right
    else:
        split_point = left if (mid - left) <= (right - mid) else right
    return text[:split_point] + '\n' + text[split_point+1:]

class C(BaseConstants): 
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    MIN_LEN_ANS = 100
    QUESTIONS = [
        "Please describe your dietary pattern, specifically your meat eating habits. Think about what you would consume in a typical week",
        "Are there any personal motivations that you have to eat or not to eat meat? Feel free to write about anything that comes to mind",
        "Think about the people you interact with on a regular basis and whose opinions and meat eating habits are important to you. What are their meat eating habits?",
        "Think about the people you interact with on a regular basis and whose opinions and meat eating habits are important to you. What are their motivations to eat or to avoid eating meat?"
    ]
    MEAT_DEFINITION = "Even if you did not think much about these issues please write whatever comes to mind at this moment. Please try to write at least a few sentences."
    MEAT_FREQ_CATEGORIES = [
        "never",
        "less than once a week",
        "one or two days a week",
        "three or four days a week",
        "five or six days a week",
        "every day"
    ]
    NUM_NODES_THRESHOLD=3
    NUM_NODES_MAX=10


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    
    # --- QUESTIONS ---
    answer1 = models.LongStringField(label="", blank=False)  
    answer2 = models.LongStringField(label="", blank=False)
    answer3 = models.LongStringField(label="", blank=False)
    answer4 = models.LongStringField(label="", blank=False)
    
    # --- MEAT SCALE ---
    meat_consumption_present = models.StringField(
        choices=C.MEAT_FREQ_CATEGORIES,
        label="How often do you eat any meat in an average week?",
        widget=widgets.RadioSelect
    )
    meat_consumption_past = models.StringField(
        choices=C.MEAT_FREQ_CATEGORIES,
        label="Try to recall your meat eating habits 5 years ago. How often did you eat any meat in an average week?",
        widget=widgets.RadioSelect
    )
    meat_consumption_future = models.StringField(
        choices=C.MEAT_FREQ_CATEGORIES,
        label="Try to imagine how your meat eating habits might look 5 years from now. How often do you think you will eat any meat in an average week?",
        widget=widgets.RadioSelect
    )
    
    # --- SOCIAL CIRCLE ---
    social_circle_distribution = models.LongStringField(blank=True)
    
    # --- LLM --- 
    prompt_used = models.LongStringField(blank=True)
    llm_result = models.LongStringField(blank=True)
    generated_nodes = models.LongStringField(blank=True)
    final_nodes = models.LongStringField(blank=True)
    generated_nodes_ratings = models.LongStringField(blank=True) 

    # --- MAPPING: PLACEMENT + EDGES ---
    positions_1 = models.LongStringField(blank=True)
    positions_2 = models.LongStringField(blank=True)
    positions_3 = models.LongStringField(blank=True)
    positions_4 = models.LongStringField(blank=True)
    positions_5 = models.LongStringField(blank=True)

    edges_2 = models.LongStringField(blank=True)
    edges_3 = models.LongStringField(blank=True)
    edges_4 = models.LongStringField(blank=True)
    edges_5 = models.LongStringField(blank=True)
    
    # --- NETWORK REFLECTION ---
    network_reflection_rating = models.IntegerField(
        label="How well does this representation capture the most important influences on your meat eating behavior?",
        choices=[[1, "Not at all"], [2, "Slightly"], [3, "Moderately"], [4, "Very well"], [5, "Extremely well"]],
        widget=widgets.RadioSelectHorizontal
    )
    network_reflection_text = models.LongStringField(
        label="Was there anything that was difficult or unclear?",
        blank=True
    )
    network_surprise_text = models.LongStringField(
        label="Do you feel that something is missing from the network?",
        blank=True
    )
    network_learn_text = models.LongStringField(
        label="Did you learn anything about your motivations or habits?",
        blank=True
    )
    
    ### --- PLAUSIBILITY ---
    importance_ratings = models.LongStringField(blank=True)
    #plausibility_edge_evaluations = models.LongStringField()
    plausibility_edge_pairs_data = models.LongStringField()
    plausibility_edge_1_type = models.IntegerField(
        choices=[(0, 'No Influence'), (1, 'Positive Influence'), (2, 'Negative Influence')],
        label="Influence type for pair 1"
    )
    plausibility_edge_1_strength = models.IntegerField(blank=True)
    plausibility_edge_2_type = models.IntegerField(
        choices=[(0, 'No Influence'), (1, 'Positive Influence'), (2, 'Negative Influence')],
        label="Influence type for pair 2"
    )
    plausibility_edge_2_strength = models.IntegerField(blank=True)
    plausibility_edge_3_type = models.IntegerField(
        choices=[(0, 'No Influence'), (1, 'Positive Influence'), (2, 'Negative Influence')],
        label="Influence type for pair 3"
    )
    plausibility_edge_3_strength = models.IntegerField(blank=True)
    social_pressure_personal_beliefs = models.LongStringField(blank=True)
    
    ### VEMI ### 
    vemi_1 = models.IntegerField(label="I want to be healthy", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_2 = models.IntegerField(label="Plant-based diets are better for the environment", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_3 = models.IntegerField(label="Animals do not have to suffer", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_4 = models.IntegerField(label="Animals’ rights are respected", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_5 = models.IntegerField(label="I want to live a long time", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_6 = models.IntegerField(label="Plant-based diets are more sustainable", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_7 = models.IntegerField(label="I care about my body", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_8 = models.IntegerField(label="Eating meat is bad for the planet", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_9 = models.IntegerField(label="Animal rights are important to me", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_10 = models.IntegerField(label="Plant-based diets are environmentally-friendly", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_11 = models.IntegerField(label="It does not seem right to exploit animals", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_12 = models.IntegerField(label="Plants have less of an impact on the environment than animal products", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_13 = models.IntegerField(label="I am concerned about animal rights", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_14 = models.IntegerField(label="My health is important to me", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)
    vemi_15 = models.IntegerField(label="I don’t want animals to suffer", choices=[1,2,3,4,5,6,7], widget=widgets.RadioSelectHorizontal)

    # attention
    attention_personal = models.IntegerField(
        label="How much attention do you pay to your own meat eating motivations and behaviors?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal
    )
    attention_social = models.IntegerField(
        label="How much attention do you pay to the meat eating motivations and behaviors of your social contacts??",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal
    )

    # --- Demographics ---
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
    state = models.StringField(
        label="In which state do you currently live?",
        choices=US_STATES
    )
    zipcode = models.StringField(
        label="Please enter your 5-digit ZIP code:",
        min_length=5,
        max_length=5,
    )

    # FOR EXCLUSION 
    num_nodes = models.IntegerField(initial=0)

    consent_given = models.BooleanField(
        choices=[[True, 'I consent'], [False, 'I do not consent']],
        widget=widgets.RadioSelect,
        label=''
    )
    
    # For now just set default as True 
    force_answer = models.BooleanField(initial=True)

# some of this we can delete
for i in range(40): # just some high enough number
    setattr(Player, f"belief_rating_{i}", models.StringField(blank=True)) # used. 

# PAGES 
class Consent(Page):
    form_model = 'player'
    form_fields = ['consent_given']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.force_answer = True

    def error_message(self, values):
        if values['consent_given'] is None:
            return "Please indicate whether you consent to participate."

## QUESTIONS
class Question1(Page):
    form_model = 'player'
    form_fields = ['answer1']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            meat=C.MEAT_DEFINITION,
            prompt=C.QUESTIONS[0])

    @staticmethod
    def error_message(player, values):
        if len(values['answer1']) < C.MIN_LEN_ANS:
            return f'Please write at least {C.MIN_LEN_ANS} characters.'

    @staticmethod
    def is_displayed(player: Player): 
        return player.consent_given 

# implement check.
class Question2(Page):
    form_model = 'player'
    form_fields = ['answer2']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            meat=C.MEAT_DEFINITION,
            prompt=C.QUESTIONS[1])

    @staticmethod
    def error_message(player, values):
        if len(values['answer2']) < C.MIN_LEN_ANS:
            return f'Please write at least {C.MIN_LEN_ANS} characters.'

    @staticmethod
    def is_displayed(player: Player): 
        return player.consent_given 

class Question3(Page):
    form_model = 'player'
    form_fields = ['answer3']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            meat=C.MEAT_DEFINITION,
            prompt=C.QUESTIONS[2])
    
    @staticmethod
    def error_message(player, values):
        if len(values['answer3']) < C.MIN_LEN_ANS:
            return f'Please write at least {C.MIN_LEN_ANS} characters.'

    @staticmethod
    def is_displayed(player: Player): 
        return player.consent_given 

class Question4(Page):
    form_model = 'player'
    form_fields = ['answer4']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            meat=C.MEAT_DEFINITION,
            prompt=C.QUESTIONS[3])
        
    @staticmethod
    def error_message(player, values):
        if len(values['answer4']) < C.MIN_LEN_ANS:
            return f'Please write at least {C.MIN_LEN_ANS} characters.'

    @staticmethod
    def is_displayed(player: Player): 
        return player.consent_given 

class MeatScale(Page):
    form_model = 'player'
    form_fields = ['meat_consumption_present', 'meat_consumption_past', 'meat_consumption_future']

    @staticmethod
    def is_displayed(player: Player): 
        return player.consent_given 

class SocialCircleDistribution(Page):

    form_model = 'player'
    form_fields = ['social_circle_distribution']

    @staticmethod
    def vars_for_template(player: Player):
        categories = C.MEAT_FREQ_CATEGORIES
        initial_distribution = json.dumps({category: 0 for category in categories})
        return dict(
            categories=categories,
            initial_distribution=initial_distribution
        )

    @staticmethod
    def error_message(player, values):
        try:
            data = json.loads(values['social_circle_distribution'])
            if sum(data.values()) != 100:
                return "The total must sum to exactly 100"
        except Exception:
            return "Something went wrong. Please adjust the sliders again."

    @staticmethod
    def is_displayed(player: Player): 
        return player.consent_given 

class LLMGenerate(Page):
    timeout_seconds = 120
    auto_submit = True

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not player.field_maybe_none('generated_nodes'):
            questions_answers = {
                C.QUESTIONS[i]: getattr(player, f"answer{i+1}")
                for i in range(len(C.QUESTIONS))
            }

            player.prompt_used = make_node_prompt(questions_answers)

            try:
                llm_nodes = call_openai(NodeModelList, player.prompt_used)
                llm_nodes = json.loads(llm_nodes.model_dump_json(indent=2))['results']
            except Exception as e:
                print("❌ LLM call failed:", e)
                llm_nodes = []

            player.llm_result = json.dumps(llm_nodes)
            filtered_nodes = [
                node for node in llm_nodes 
                if not (node['type'] == 'PERSONAL' and node['category'] == 'BEHAVIOR')
            ]
            random.shuffle(filtered_nodes)
            player.generated_nodes = json.dumps(filtered_nodes)
            
            # for exclusion 
            player.num_nodes = len(filtered_nodes)
    
    @staticmethod
    def is_displayed(player: Player): 
        return player.consent_given 

class BeliefAccuracyRating(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        return [f"belief_rating_{i}" for i in range(len(json.loads(player.generated_nodes or '[]')))]

    @staticmethod
    def vars_for_template(player: Player):
        nodes = json.loads(player.generated_nodes) if player.generated_nodes else []
        qa_pairs = [{'question': q, 'answer': getattr(player, f'answer{i+1}')}
                    for i, q in enumerate(C.QUESTIONS)]
        belief_items = [
            {"index": i, "belief": node.get("stance", ""), "rating": ""}
            for i, node in enumerate(nodes)
        ]
        return dict(belief_items=belief_items, transcript=qa_pairs, C=C, rating_options=list(range(1, 8)))

    @staticmethod
    def error_message(player: Player, values):
        nodes = json.loads(player.generated_nodes or '[]')
        ratings_to_store = []
        for i, node in enumerate(nodes):
            stance = node.get("stance", "")
            rating = values.get(f"belief_rating_{i}", "")
            if not rating:
                return "Please rate all items before continuing."
            ratings_to_store.append({"text": smart_linebreak(stance), "belief": stance, "rating": rating})
        player.generated_nodes_ratings = json.dumps(ratings_to_store)

        # First filter: only include beliefs rated > 4
        filtered_nodes = [r for r in ratings_to_store if int(r["rating"]) > 4]

        # Second filter: randomly sample if too many
        if len(filtered_nodes) > C.NUM_NODES_MAX:
            filtered_nodes = random.sample(filtered_nodes, C.NUM_NODES_MAX)

        player.final_nodes = json.dumps(filtered_nodes)
        player.num_nodes = len(filtered_nodes)
        
    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )
        
class Exit(Page):
    @staticmethod
    def is_displayed(player: Player):
        return (
            not player.consent_given
            or player.num_nodes < C.NUM_NODES_THRESHOLD
        )
        
class MapNodePlacement(Page):
    form_model = 'player'
    form_fields = ['positions_1']

    @staticmethod
    def vars_for_template(player):
        labels = [item['text'] for item in json.loads(player.final_nodes or '[]') if item.get('text')]
        return dict(belief_labels_json=json.dumps(labels))
    
    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class MapEdgeCreation1(Page):
    form_model = 'player'
    form_fields = ['positions_2', 'edges_2']

    @staticmethod
    def vars_for_template(player):
        labels = [item['text'] for item in json.loads(player.final_nodes or '[]')]
        positions = json.loads(player.positions_1 or '[]')
        belief_points = [
            {"label": label, "x": positions[i+1]['x'], "y": positions[i+1]['y'], "radius": 20}
            for i, label in enumerate(labels)
        ]
        return dict(
            belief_points=belief_points, 
            belief_labels_json=json.dumps(labels),
            force_answer=player.force_answer)
    
    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class MapEdgeCreation2(Page):
    form_model = 'player'
    form_fields = ['positions_3', 'edges_3']

    @staticmethod
    def vars_for_template(player):
        labels = [item['text'] for item in json.loads(player.final_nodes or '[]')]
        positions = json.loads(player.positions_2 or '[]')
        prior_edges = json.loads(player.edges_2 or '[]')
        belief_points = [
            {"label": label, "x": positions[i+1]['x'], "y": positions[i+1]['y'], "radius": 20}
            for i, label in enumerate(labels)
        ]
        return dict(
            belief_points=belief_points, 
            belief_labels_json=json.dumps(labels), 
            belief_edges=prior_edges,
            force_answer=player.force_answer)

    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class MapEdgeCreation3(Page):
    form_model = 'player'
    form_fields = ['positions_4', 'edges_4']

    @staticmethod
    def vars_for_template(player):
        labels = [item['text'] for item in json.loads(player.final_nodes or '[]')]
        positions = json.loads(player.positions_3 or '[]')
        prior_edges = json.loads(player.edges_3 or '[]')
        belief_points = [
            {"label": label, "x": positions[i+1]['x'], "y": positions[i+1]['y'], "radius": 20}
            for i, label in enumerate(labels)
        ]
        return dict(
            belief_points=belief_points, 
            belief_labels_json=json.dumps(labels), 
            belief_edges=prior_edges,
            force_answer=player.force_answer)

    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class MapImportance(Page):
    form_model = 'player'
    form_fields = ['positions_5', 'edges_5']

    @staticmethod
    def vars_for_template(player):
        labels = [item['text'] for item in json.loads(player.final_nodes or '[]')]
        positions = json.loads(player.positions_4 or '[]')
        prior_edges = json.loads(player.edges_4 or '[]')
        belief_points = [
            {"label": label, "x": positions[i+1]['x'], "y": positions[i+1]['y'], "radius": 20}
            for i, label in enumerate(labels)
        ]
        return dict(belief_points=belief_points, belief_labels_json=json.dumps(labels), belief_edges=prior_edges)

    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class NetworkReflection(Page):
    form_model = 'player'
    form_fields = [
        'network_reflection_rating', 
        'network_reflection_text',
        'network_surprise_text',
        'network_learn_text'
    ]

    @staticmethod
    def vars_for_template(player):
        labels = [item['text'] for item in json.loads(player.final_nodes or '[]')]
        positions = json.loads(player.positions_5 or '[]')
        edges = json.loads(player.edges_5 or '[]')
        belief_points = [
            {"label": label, "x": positions[i+1]['x'], "y": positions[i+1]['y'], "radius": positions[i+1].get('radius', 20)}
            for i, label in enumerate(labels)
        ]
        return dict(belief_points=belief_points, belief_edges=edges, focal_radius=positions[0].get('radius', 20))

    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class PlausibilityImportance(Page):
    form_model = 'player'
    form_fields = ['importance_ratings']  # this will be a JSON field to hold the answers

    @staticmethod
    def vars_for_template(player):
        positions = json.loads(player.positions_5)
        labels = [node['label'] for node in positions]
        labels = [label for label in labels if label != 'Meat Eating']  # optionally skip the focal node

        return dict(labels=labels)

    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class PlausibilityEdges(Page):
    form_model = 'player'
    form_fields = [
        'plausibility_edge_1_type', 'plausibility_edge_1_strength',
        'plausibility_edge_2_type', 'plausibility_edge_2_strength',
        'plausibility_edge_3_type', 'plausibility_edge_3_strength'
    ]

    @staticmethod
    def vars_for_template(player):
        nodes = json.loads(player.positions_5 or '[]')
        edges = json.loads(player.edges_5 or '[]')
        labels = [n['label'] for n in nodes]

        edge_lookup = {tuple(sorted([e['from'], e['to']])): e['polarity'] for e in edges}
        all_pairs = [(a, b) for i, a in enumerate(labels) for b in labels[i+1:]]

        pos_pairs = [p for p in all_pairs if edge_lookup.get(tuple(sorted(p))) == 'positive']
        neg_pairs = [p for p in all_pairs if edge_lookup.get(tuple(sorted(p))) == 'negative']
        none_pairs = [p for p in all_pairs if tuple(sorted(p)) not in edge_lookup]

        def pick(pairs):
            return random.choice(pairs) if pairs else random.choice(all_pairs)

        pos = pick(pos_pairs)
        neg = pick(neg_pairs)
        none = pick(none_pairs)

        player.plausibility_edge_pairs_data = json.dumps({"positive": pos, "negative": neg, "none": none})
        return dict(all_pairs=[(1, pos), (2, neg), (3, none)])

    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class SocialPressureMotivations(Page):
    form_model = 'player'
    form_fields = ['social_pressure_personal_beliefs']

    @staticmethod
    def vars_for_template(player):
        def normalize(t): return t.replace('\n', ' ').strip()

        positions = json.loads(player.positions_5 or '[]')
        llm_nodes = json.loads(player.llm_result or '[]')
        node_lookup = {normalize(n['stance']): n for n in llm_nodes}

        return dict(
            belief_items=[p for p in positions if node_lookup.get(normalize(p['label']), {}).get('type') == 'PERSONAL' and node_lookup.get(normalize(p['label']), {}).get('category') == 'MOTIVATION'],
            categories=['Good reason', 'Bad reason', 'Neither']
        )

    @staticmethod
    def error_message(player, values):
        try:
            data = json.loads(values['social_pressure_personal_beliefs'])
        except Exception:
            return "Something went wrong. Please adjust the sliders again."

        for belief_data in data.values():
            if sum(belief_data['values'].values()) != 100:
                return "Each box must sum to exactly 100%."

    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class VEMI(Page):
    form_model = 'player'
    form_fields = [
        'vemi_1', 'vemi_2', 'vemi_3', 'vemi_4', 'vemi_5',
        'vemi_6', 'vemi_7', 'vemi_8', 'vemi_9', 'vemi_10',
        'vemi_11', 'vemi_12', 'vemi_13', 'vemi_14', 'vemi_15'
    ]
    
    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class AttentionPage(Page):
    form_model = 'player'
    form_fields = [
        'attention_personal',
        'attention_social',
    ]

    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class Demographics(Page): 
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'politics', 'state', 'zipcode']

    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

class ResultsWaitPage(WaitPage):
    pass

class Results(Page):
    @staticmethod
    def is_displayed(player: Player): 
        return (
            player.num_nodes >= C.NUM_NODES_THRESHOLD
            and player.consent_given
        )

page_sequence = [
    # INFORMED CONSENT # 
    Consent,
    Question1,
    Question2,
    Question3,
    Question4,
    MeatScale,
    SocialCircleDistribution,
    LLMGenerate, # HERE-->REVIEW
    BeliefAccuracyRating, # HERE-->REVIEW
    Exit,
    MapNodePlacement,
    MapEdgeCreation1,
    MapEdgeCreation2,
    MapEdgeCreation3,
    MapImportance,
    NetworkReflection,
    PlausibilityImportance,
    PlausibilityEdges,
    SocialPressureMotivations,
    VEMI,
    AttentionPage,
    Demographics,
    Results
]