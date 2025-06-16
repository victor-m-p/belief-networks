from otree.api import *
import json
from .llm_utils import *
import json
import random

doc = """
Your app description
"""

US_STATES = [
    'Alaska', 'Alabama', 'Arkansas', 'Arizona',
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

    # Find middle point
    mid = len(text) // 2

    # Search for nearest space to the middle (first to the right, then to the left)
    right = text.find(' ', mid)
    left = text.rfind(' ', 0, mid)

    # Pick the best split point
    if right == -1 and left == -1:
        split_point = mid  # no spaces found, just split at middle
    elif right == -1:
        split_point = left
    elif left == -1:
        split_point = right
    else:
        # pick the closer one to mid
        split_point = left if (mid - left) <= (right - mid) else right

    # Insert line break
    return text[:split_point] + '\n' + text[split_point+1:]


class C(BaseConstants): 
    
    # not sure we need this 
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    MAX_NODES=20
    MAX_CHAR=60
    MAX_USER_NODES=3
    
    QUESTIONS = [
        "Please describe your dietary pattern, specifically your meat eating habits. Think about what you would consume in a typical week",
        "Are there any personal motivations that you have to eat or not to eat meat? Feel free to write about anything that comes to mind",
        "Think about the people you interact with on a regular basis and whose opinions and meat eating habits are important to you. What are their meat eating habits?",
        "Think about the people you interact with on a regular basis and whose opinions and meat eating habits are important to you. What are their motivations to eat or to avoid eating meat?"
    ]

    MEAT_DEFINITION = "Even if you did not think much about these issues please write whatever comes to mind at this moment. Please try to write at least a few sentences."

    N_QUESTIONS = len(QUESTIONS)

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

# helper function
def get_filtered_nodes(player, type_filter, category_filter):
    try:
        llm_data = json.loads(player.llm_result)
    except (TypeError, json.JSONDecodeError):
        llm_data = []
    return [
        node for node in llm_data
        if node.get('type') == type_filter and node.get('category') == category_filter
    ]

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
    state = models.StringField(
        label="In which state do you currently live?",
        choices=US_STATES
    )

    zipcode = models.StringField(
        label="Please enter your 5-digit ZIP code:",
        min_length=5,
        max_length=5,
    )

    # add the scale  
    meat_consumption_present = models.StringField(
        choices=[
            'never',
            'less than once a week',
            'one or two days a week',
            'three or four days a week',
            'five or six days a week',
            'every day',
        ],
        label="How often do you eat any meat in an average week?",
        widget=widgets.RadioSelect
    )
    meat_consumption_past = models.StringField(
        choices=[
            'never',
            'less than once a week',
            'one or two days a week',
            'three or four days a week',
            'five or six days a week',
            'every day',
        ],
        label="Try to recall your meat eating habits 5 years ago. How often did you eat any meat in an average week?",
        widget=widgets.RadioSelect
    )
    meat_consumption_future = models.StringField(
        choices=[
            'never',
            'less than once a week',
            'one or two days a week',
            'three or four days a week',
            'five or six days a week',
            'every day',
        ],
        label="Try to imagine how your meat eating habits might look 5 years from now. How often do you think you will eat any meat in an average week?",
        widget=widgets.RadioSelect
    )

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
    user_nodes = models.LongStringField(blank=True)
    final_nodes = models.LongStringField(blank=True)
    generated_nodes_ratings = models.LongStringField(blank=True)

    # For new way of doing belief codings (humans)
    # Currently we are not doing these human labels.
    label_input_0 = models.StringField(blank=True)
    label_input_1 = models.StringField(blank=True)
    label_input_2 = models.StringField(blank=True)
    label_input_3 = models.StringField(blank=True)

    all_labels_json = models.LongStringField(initial='[]')  # final flat list
    label_snapshots = models.LongStringField(initial='[]')  # list of lists

    # Position/NETWORK 
    ## MapNodePlacement
    positions_1 = models.LongStringField(blank=True)
    ## MapEdgeCreation1
    edges_2 = models.LongStringField(blank=True)
    positions_2 = models.LongStringField(blank=True)
    ## MapEdgeCreation2
    edges_3 = models.LongStringField(blank=True)
    positions_3 = models.LongStringField(blank=True)
    ## MapEdgeCreation3
    edges_4 = models.LongStringField(blank=True)
    positions_4 = models.LongStringField(blank=True)
    ## MapImportance
    edges_5 = models.LongStringField(blank=True)
    positions_5 = models.LongStringField(blank=True)
    
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
    
    ## judge network ## 
    network_reflection_rating = models.IntegerField(
        label="How well do you feel that this representation captures your political beliefs?",
        choices=[[1, "Not at all"], [2, "Slightly"], [3, "Moderately"], [4, "Very well"], [5, "Extremely well"]],
        widget=widgets.RadioSelectHorizontal
    )

    network_reflection_text = models.LongStringField(
        label="Please share your thoughts about the network representation above. Does it make sense for you to think about your motivations and habits in this way or does it feel weird? Are there any connections, motivations, or habits that feel especially meaningful or maybe surprising?",
        blank=True
    )
    
    # attention
    attention_personal_behaviors = models.IntegerField(
        label="How much attention do you pay to your own meat eating habits?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal
    )
    attention_personal_motivations = models.IntegerField(
        label="How much attention do you pay to your own meat eating motivations?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal
    )
    attention_social_motivations = models.IntegerField(
        label="How much attention do you pay to the meat eating motivations of your social contacts?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal
    )
    attention_social_behaviors = models.IntegerField(
        label="How much attention do you pay to the meat eating habits of your social contacts?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal
    )
    attention_meat_eating = models.IntegerField(
        label="How much attention do you overall pay to meat eating?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal
    )
    
    social_circle_distribution = models.LongStringField(blank=True)
    
    ### plausibility edges ### 
    # Pair data storage (assuming you generate pairs like before)
    plausibility_edge_pairs_data = models.LongStringField()

    # For Pair 1:
    edge_influence_type_1 = models.IntegerField(
        choices=[
            (0, 'No influence'),
            (1, 'Positive influence'),
            (2, 'Negative influence')
        ],
        label="",
        widget=widgets.RadioSelect
    )
    edge_influence_strength_1 = models.IntegerField(
        min=0, max=100,
        label="Influence strength (0-100)",
        blank=True
    )

    # For Pair 2:
    edge_influence_type_2 = models.IntegerField(
        choices=[
            (0, 'No influence'),
            (1, 'Positive influence'),
            (2, 'Negative influence')
        ],
        label="",
        widget=widgets.RadioSelect
    )
    edge_influence_strength_2 = models.IntegerField(
        min=0, max=100,
        label="Influence strength (0-100)",
        blank=True
    )
    
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

for i in range(C.MAX_NODES):
    setattr(Player, f"belief_rating_{i}", models.StringField(blank=True))
    setattr(Player, f"node_choice_{i}", models.StringField(blank=True))
    setattr(Player, f"node_modify_text_{i}", models.StringField(blank=True))
    setattr(Player, f"node_reject_reason_{i}", models.StringField(blank=True))
    setattr(Player, f"LLM_codings_{i}", models.StringField(blank=True))
    setattr(Player, f"LLM_accepted_{i}", models.StringField(blank=True))
    setattr(Player, f"Human_nodes_{i}", models.StringField(blank=True))
    setattr(Player, f"Final_nodes_{i}", models.StringField(blank=True))

# PAGES 
## INTRODUCTION 
class Introduction(Page):
    pass

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
        if len(values['answer1']) < 100:
            return 'Please write at least 100 characters.'

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
        if len(values['answer2']) < 100:
            return 'Please write at least 100 characters.'

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
        if len(values['answer3']) < 100:
            return 'Please write at least 100 characters.'

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
        if len(values['answer4']) < 100:
            return 'Please write at least 100 characters.'

class MeatScale(Page):
    form_model = 'player'
    form_fields = ['meat_consumption_present', 'meat_consumption_past', 'meat_consumption_future']

class SocialCircleDistribution(Page):

    form_model = 'player'
    form_fields = ['social_circle_distribution']

    @staticmethod
    def vars_for_template(player):
        categories = [
            'never',
            'less than once a week',
            'one or two days a week',
            'three or four days a week',
            'five or six days a week',
            'every day',
        ]

        initial_distribution = json.dumps({category: 0 for category in categories})

        return dict(
            categories=categories,
            initial_distribution=initial_distribution
        )

    @staticmethod
    def error_message(player, values):
        import json

        try:
            data = json.loads(values['social_circle_distribution'])
        except Exception:
            return "Something went wrong. Please adjust the sliders again."

        total = sum(data.values())
        if total != 100:
            return "The total must sum to exactly 100."

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
            player.llm_result = json.dumps(llm_nodes)
            
            filtered_nodes = [
                node for node in llm_nodes 
                if not (node['type'] == 'PERSONAL' and node['category'] == 'BEHAVIOR')
            ]
            
            random.shuffle(filtered_nodes)
            player.generated_nodes = json.dumps(filtered_nodes)
            

class BeliefAccuracyRating(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        generated_nodes = json.loads(player.generated_nodes or '[]')
        return [f"belief_rating_{i}" for i in range(len(generated_nodes))]

    @staticmethod
    def vars_for_template(player):
        generated_nodes = json.loads(player.generated_nodes or '[]')

        qa_pairs = []
        for i, question in enumerate(C.QUESTIONS):
            fieldname = f'answer{i+1}'
            answer = getattr(player, fieldname, '')
            qa_pairs.append({'question': question, 'answer': answer})

        stored_ratings = json.loads(player.field_maybe_none('generated_nodes_ratings') or '[]')

        rating_items = []
        for i, node in enumerate(generated_nodes):
            stance = node.get("stance", "")
            rating = ''
            if i < len(stored_ratings):
                rating = stored_ratings[i].get("rating", "")
            rating_items.append({
                "index": i,
                "belief": stance,
                "rating": str(rating),
            })

        return dict(
            belief_items=rating_items,
            transcript=qa_pairs,
            C=C,
            rating_options=list(range(1, 8))
        )

    @staticmethod
    def error_message(player, values):
        generated_nodes = json.loads(player.generated_nodes or '[]')
        ratings_to_store = []

        for i, node in enumerate(generated_nodes):
            stance = node.get("stance", "")
            rating = values.get(f"belief_rating_{i}", "")
            text = smart_linebreak(stance)
            if not rating:
                return "Please rate all items before continuing."
            ratings_to_store.append({
                "text": text,
                "belief": stance,
                "rating": rating # not used right now
            })

        player.generated_nodes_ratings = json.dumps(ratings_to_store)

        # for revised beliefs - maybe we can do this in a more smooth way 
        final_nodes = [
            entry for entry in ratings_to_store 
            if int(entry["rating"]) >= 4
        ]
        
        player.final_nodes = json.dumps(final_nodes)

    @staticmethod
    def before_next_page(player, timeout_happened):
        pass

class MapNodePlacement(Page):
    form_model = 'player'
    form_fields = ['positions_1']

    @staticmethod
    def vars_for_template(player):
        final_nodes = json.loads(player.final_nodes or '[]')
        belief_texts = [item['text'] for item in final_nodes if item.get('text')]

        # Just send the labels, layout happens in template
        belief_points = [{"label": label} for label in belief_texts]

        return dict(
            belief_labels_json=json.dumps([point['label'] for point in belief_points]),
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        pass

class MapEdgeCreation1(Page):
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
        labels = [item['text'] for item in final_nodes]
        for i, item in enumerate(final_nodes):
            pos_idx = i + 1
            x = positions[pos_idx]['x']
            y = positions[pos_idx]['y']
            radius = 20
            belief_points.append({"label": item['text'], "x": x, "y": y, "radius": radius})

        return dict(
            belief_points=belief_points,
            belief_labels_json=json.dumps(labels)  # only pass labels_json for JS
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass

class MapEdgeCreation2(Page):
    form_model = 'player'
    form_fields = ['positions_3', 'edges_3']

    @staticmethod
    def vars_for_template(player: Player):
        final_nodes = json.loads(player.final_nodes or '[]')
        try:
            positions = json.loads(player.positions_2 or '[]')
            prior_edges = json.loads(player.edges_2 or '[]')
        except (TypeError, json.JSONDecodeError):
            positions = []
            prior_edges = []

        belief_points = []
        labels = [item['text'] for item in final_nodes]
        for i, item in enumerate(final_nodes):
            pos_idx = i + 1
            x = positions[pos_idx]['x']
            y = positions[pos_idx]['y']
            radius = 20
            belief_points.append({"label": item['text'], "x": x, "y": y, "radius": radius})

        return dict(
            belief_points=belief_points,
            belief_labels_json=json.dumps(labels),
            belief_edges=prior_edges  # <-- pass existing edges
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass

class MapEdgeCreation3(Page):
    form_model = 'player'
    form_fields = ['positions_4', 'edges_4']

    @staticmethod
    def vars_for_template(player: Player):
        final_nodes = json.loads(player.final_nodes or '[]')
        try:
            positions = json.loads(player.positions_3 or '[]')
            prior_edges = json.loads(player.edges_3 or '[]')
        except (TypeError, json.JSONDecodeError):
            positions = []
            prior_edges = []

        belief_points = []
        labels = [item['text'] for item in final_nodes]
        for i, item in enumerate(final_nodes):
            pos_idx = i + 1
            x = positions[pos_idx]['x']
            y = positions[pos_idx]['y']
            radius = 20
            belief_points.append({"label": item['text'], "x": x, "y": y, "radius": radius})

        return dict(
            belief_points=belief_points,
            belief_labels_json=json.dumps(labels),
            belief_edges=prior_edges  # <-- pass existing edges
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass

class MapImportance(Page):
    form_model = 'player'
    form_fields = ['positions_5', 'edges_5']

    @staticmethod
    def vars_for_template(player: Player):
        final_nodes = json.loads(player.final_nodes or '[]')
        try:
            positions = json.loads(player.positions_4 or '[]')
            prior_edges = json.loads(player.edges_4 or '[]')
        except (TypeError, json.JSONDecodeError):
            positions = []
            prior_edges = []

        belief_points = []
        labels = [item['text'] for item in final_nodes]
        for i, item in enumerate(final_nodes):
            pos_idx = i + 1
            x = positions[pos_idx]['x']
            y = positions[pos_idx]['y']
            radius = 20
            belief_points.append({"label": item['text'], "x": x, "y": y, "radius": radius})

        return dict(
            belief_points=belief_points,
            belief_labels_json=json.dumps(labels),
            belief_edges=prior_edges  # <-- pass existing edges
        )
        
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass

class NetworkReflection(Page):
    form_model = 'player'
    form_fields = ['network_reflection_rating', 'network_reflection_text']

    @staticmethod
    def vars_for_template(player: Player):
        final_nodes = json.loads(player.final_nodes or '[]')
        try:
            positions = json.loads(player.positions_5 or '[]')
            prior_edges = json.loads(player.edges_5 or '[]')
        except (TypeError, json.JSONDecodeError):
            positions = []
            prior_edges = []

        belief_points = []
        labels = [item['text'] for item in final_nodes]
        for i, item in enumerate(final_nodes):
            pos_idx = i + 1
            x = positions[pos_idx]['x']
            y = positions[pos_idx]['y']
            radius = positions[pos_idx]['radius']
            belief_points.append({"label": item['text'], "x": x, "y": y, "radius": radius})

        return dict(
            belief_points=belief_points,
            belief_edges=prior_edges
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

class PlausibilityEdges(Page):
    form_model = 'player'
    form_fields = [
        'edge_influence_type_1', 'edge_influence_strength_1',
        'edge_influence_type_2', 'edge_influence_strength_2'
    ]

    @staticmethod
    def vars_for_template(player):
        # You can adapt this depending on how you store nodes
        all_nodes = json.loads(player.positions_3)
        labels = [node['label'] for node in all_nodes]
        random.shuffle(labels)
        chosen = labels[:4]

        pair_1 = (chosen[0], chosen[1])
        pair_2 = (chosen[2], chosen[3])

        # Save for record keeping
        player.plausibility_edge_pairs_data = json.dumps({
            "pair_1": pair_1,
            "pair_2": pair_2
        })

        return dict(pair_1=pair_1, pair_2=pair_2)

class VEMI(Page):
    form_model = 'player'
    form_fields = [
        'vemi_1', 'vemi_2', 'vemi_3', 'vemi_4', 'vemi_5',
        'vemi_6', 'vemi_7', 'vemi_8', 'vemi_9', 'vemi_10',
        'vemi_11', 'vemi_12', 'vemi_13', 'vemi_14', 'vemi_15'
    ]

class AttentionPage(Page):
    form_model = 'player'
    form_fields = [
        'attention_personal_behaviors',
        'attention_personal_motivations',
        'attention_social_motivations',
        'attention_social_behaviors',
        'attention_meat_eating'
    ]

class Demographics(Page): 
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'politics', 'state', 'zipcode']

class ResultsWaitPage(WaitPage):
    pass

class Results(Page):
    pass

# page sequence 
page_sequence = [
    Introduction,
    # QUESTIONS 
    Question1, 
    Question2, 
    Question3, 
    Question4,
    # WEIRD THAT THESE ARE BEFORE LLM THINGS?
    MeatScale,
    SocialCircleDistribution,
    # GENERATE + SELECT BELIEFS 
    LLMGenerate,
    BeliefAccuracyRating,
    # PLACEMENT + EDGES + IMPORTANCE
    MapNodePlacement,
    MapEdgeCreation1,
    MapEdgeCreation2,
    MapEdgeCreation3,
    MapImportance,
    NetworkReflection,
    # PLAUSIBILITY
    PlausibilityImportance,
    PlausibilityEdges,
    # OTHER 
    VEMI,
    AttentionPage,
    Demographics, 
    # The page with social influence on personal beliefs # 
    Results
]