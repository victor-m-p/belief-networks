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
        "Think about the people you interact with on a regular basis and whose opinions are important to you. What are their meat eating habits?",
        "Think about the people you interact with on a regular basis and whose opinions are important to you. What are their motivations to eat or to avoid eating meat?"
        #"What are some things that come to mind when you think about meat eating? What are your thoughts, feelings, or concerns about meat consumption?",
        #"Are there any personal motivations that you have to eat or not eat meat? Feel free to write about anything that comes to mind",
        #"Think about the people you interact with on a regular basis and whose opinions are important to you. What are their motivations to eat or avoid meat?",
        #"Think about the people you interact with on a regular basis and whoso opinions are important to you. What are their meat eating habits?"
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
        label="Approximately, how often, if at all, do you eat any meat in an average week?",
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
        label="Try to recall your meat eating habits 5 years ago. Approximately, how often, if at all, did you eat any meat in an average week?",
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
        label="Try to imagine how your meat eating habits might look 5 years from now. Approximately, how often, if at all, do you think you will eat any meat in an average week?",
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
    
    '''
    ## rate personal behavior, personal motivations, social behavior, social motivations? ## 
    personal_behavior_accurate = models.IntegerField(
        label="How accurately do the following statements summarize the personal behaviors you described in the interview?",
        choices=[[1, "Not at all"], [2, "Slightly"], [3, "Moderately"], [4, "Very well"], [5, "Extremely well"]],
        widget=widgets.RadioSelectHorizontal
    )

    personal_behavior_describe = models.IntegerField(
        label="How well overall do you feel that the following statements describe your meat eating habits?",
        choices=[[1, "Not at all"], [2, "Slightly"], [3, "Moderately"], [4, "Very well"], [5, "Extremely well"]],
        widget=widgets.RadioSelectHorizontal
    )

    personal_behavior_comments = models.LongStringField(
        blank=True,
        label="If there is anything you feel is not accurately captured in these statements, please describe it here (optional):"
    )
    
    node_accuracy_ratings = models.LongStringField(blank=True)
    '''
    
    social_circle_distribution = models.LongStringField(blank=True)
    #belief_accuracy_ratings = models.LongStringField(blank=True)

for i in range(C.MAX_NODES):
    setattr(Player, f"belief_rating_{i}", models.StringField(blank=True))
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
    form_fields = ['age', 'gender', 'education', 'politics', 'state', 'zipcode']

class ResultsWaitPage(WaitPage):
    pass

class Results(Page):
    pass

class AttentionPage(Page):
    form_model = 'player'
    form_fields = [
        'attention_personal_behaviors',
        'attention_personal_motivations',
        'attention_social_motivations',
        'attention_social_behaviors',
        'attention_meat_eating'
    ]

### classes for question pages ###
class Question1(Page):
    form_model = 'player'
    form_fields = ['answer1']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(prompt=C.QUESTIONS[0])
    
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
        if total != 10:
            return "The total must sum to exactly 10."


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
            #generated_nodes = [s.replace("I agree with the following: ", "", 1).strip() for s in generated_nodes]
            player.generated_nodes = json.dumps(generated_nodes)

'''
class RatePersonalBehavior(Page):
    form_model = 'player'
    form_fields = [
        'personal_behavior_accurate',
        'personal_behavior_describe',
        'personal_behavior_comments'
    ]

    @staticmethod
    def vars_for_template(player):
        try:
            llm_data = json.loads(player.llm_result)
        except (TypeError, json.JSONDecodeError):
            llm_data = []

        # Filter nodes for PERSONAL + BEHAVIOR
        filtered_beliefs = [
            node['stance'] for node in llm_data
            if node.get('type') == 'PERSONAL' and node.get('category') == 'BEHAVIOR'
        ]

        # Build interview transcript (as before)
        qa_pairs = []
        for i, question in enumerate(C.QUESTIONS):
            fieldname = f'answer{i+1}'
            answer = getattr(player, fieldname, '')
            qa_pairs.append({'question': question, 'answer': answer})

        return dict(
            beliefs=filtered_beliefs,
            transcript=qa_pairs
        )

class AccuracyRatingPage(Page):
    type_filter = None
    category_filter = None

    @classmethod
    def vars_for_template(cls, player):
        nodes = get_filtered_nodes(player, cls.type_filter, cls.category_filter)
        transcript = [
            {"question": C.QUESTIONS[i], "answer": getattr(player, f"answer{i+1}", '')}
            for i in range(len(C.QUESTIONS))
        ]
        return dict(beliefs=nodes, transcript=transcript)

    def before_next_page(self, timeout_happened):
        nodes = get_filtered_nodes(self.player, self.type_filter, self.category_filter)
        request_data = self.request.POST

        new_ratings = []
        for i, node in enumerate(nodes):
            initialized = request_data.get(f'initialized_{i}')
            if initialized != 'true':
                self._record_error()
                return

            rating = request_data.get(f'belief_accuracy_{i}')
            try:
                rating_int = int(rating)
            except (ValueError, TypeError):
                self._record_error()
                return

            new_ratings.append({
                "stance": node['stance'],
                "type": node['type'],
                "category": node['category'],
                "accuracy": rating_int
            })

        # Load existing ratings if any
        try:
            all_ratings = json.loads(self.player.node_accuracy_ratings)
        except (TypeError, json.JSONDecodeError):
            all_ratings = []

        all_ratings.extend(new_ratings)
        self.player.node_accuracy_ratings = json.dumps(all_ratings)
        self._record_success()

    def error_message(self, values):
        if self.participant.vars.get('rating_error'):
            return "Please provide accuracy ratings for all beliefs."

    def _record_error(self):
        self.participant.vars['rating_error'] = True

    def _record_success(self):
        self.participant.vars['rating_error'] = False


class AccuracyPersonalBehavior(AccuracyRatingPage):
    type_filter = "PERSONAL"
    category_filter = "BEHAVIOR"

class AccuracyPersonalMotivation(AccuracyRatingPage):
    type_filter = "PERSONAL"
    category_filter = "MOTIVATION"

class AccuracySocialBehavior(AccuracyRatingPage):
    type_filter = "SOCIAL"
    category_filter = "BEHAVIOR"

class AccuracySocialMotivation(AccuracyRatingPage):
    type_filter = "SOCIAL"
    category_filter = "MOTIVATION"
'''

class BeliefAccuracyRating(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        # Always load from generated_nodes
        generated_raw = player.generated_nodes or '[]'
        generated = json.loads(generated_raw)
        fields = []
        for i in range(len(generated)):
            fields.append(f"belief_rating_{i}")
        return fields

    @staticmethod
    def vars_for_template(player):
        generated_raw = player.generated_nodes or '[]'
        generated = json.loads(generated_raw)

        # Build interview transcript (unchanged)
        qa_pairs = []
        for i, question in enumerate(C.QUESTIONS):
            fieldname = f'answer{i+1}'
            answer = getattr(player, fieldname, '')
            qa_pairs.append({'question': question, 'answer': answer})

        # Build rating items
        rating_items = []
        for i, belief in enumerate(generated):
            # Try to load previous ratings if available
            stored_ratings_raw = player.field_maybe_none('generated_nodes_ratings') or '[]'
            try:
                stored_ratings = json.loads(stored_ratings_raw)
            except (TypeError, json.JSONDecodeError):
                stored_ratings = []

            rating = ''
            if i < len(stored_ratings):
                rating = stored_ratings[i].get("rating", "")

            rating_items.append({
                "index": i,
                "belief": belief,
                "rating": str(rating)
            })

        return dict(
            belief_items=rating_items,
            transcript=qa_pairs,
            C=C,
            rating_options=[str(n) for n in range(1, 8)]
        )

    @staticmethod
    def error_message(player, values):
        generated_raw = player.generated_nodes or '[]'
        generated = json.loads(generated_raw)

        ratings_to_store = []

        for i, belief in enumerate(generated):
            rating = values.get(f"belief_rating_{i}", "")
            if not rating:
                return "Please rate all beliefs before continuing."
            ratings_to_store.append({
                "belief": belief,
                "rating": rating
            })

        # Store ratings as JSON
        player.generated_nodes_ratings = json.dumps(ratings_to_store)

    @staticmethod
    def before_next_page(player, timeout_happened):
        pass

class LLMReviewRevise(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        beliefs = json.loads(player.generated_nodes)
        revised = json.loads(player.field_maybe_none('revised_beliefs') or '[]')

        if not revised:
            revised = [
                {"belief": b, "user_action": "", "text_field": ""}
                for b in beliefs
            ]
            player.revised_beliefs = json.dumps(revised)

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

        # Build interview transcript
        qa_pairs = []
        for i, question in enumerate(C.QUESTIONS):
            fieldname = f'answer{i+1}'
            answer = getattr(player, fieldname, '')
            qa_pairs.append({'question': question, 'answer': answer})

        return dict(
            belief_items=revised,
            transcript=qa_pairs,
            C=C
        )

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
        # Create final_nodes automatically after revision complete
        revised = json.loads(player.revised_beliefs)
        filtered = []
        for item in revised:
            if item['user_action'] == 'ACCEPT':
                filtered.append({'text': item['belief']})
            elif item['user_action'] == 'MODIFY' and item['text_field'].strip():
                filtered.append({'text': item['text_field'].strip()})
        player.final_nodes = json.dumps(filtered)


'''
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
'''

# splitting network part up # 
class MapNodePlacement(Page):
    form_model = 'player'
    form_fields = ['positions_1']

    @staticmethod
    def vars_for_template(player):
        final_nodes = json.loads(player.final_nodes or '[]')
        belief_texts = [item['text'] for item in final_nodes if item.get('text')]

        # Just send the labels, layout happens in template
        belief_points = [{"label": label} for label in belief_texts]

        mode = 'all'
        label_display = 'always'

        return dict(
            belief_points=belief_points,
            mode=mode,
            label_display=label_display
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        pass

'''
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
'''

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

class MeatScale(Page):
    form_model = 'player'
    form_fields = ['meat_consumption_present', 'meat_consumption_past', 'meat_consumption_future']

# Asking about attention to meat eating behaviors # 
# Asking about attention in the interview # 
# Asking about past + prediction # 

class MotivationBehaviorMapping(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player):
        llm_data = json.loads(player.llm_result)

        motivations = [
            node['stance'] for node in llm_data
            if node.get('type') == 'PERSONAL' and node.get('category') == 'MOTIVATION'
        ]

        meat_statement = f"I eat meat: {player.meat_consumption}"

        return dict(
            motivations=motivations,
            behavior_statement=meat_statement
        )

    @staticmethod
    def error_message(player, values):
        llm_data = json.loads(player.llm_result)
        motivations = [
            node['stance'] for node in llm_data
            if node.get('type') == 'PERSONAL' and node.get('category') == 'MOTIVATION'
        ]

        mappings = []
        for i, motivation in enumerate(motivations):
            response = values.get(f'link_{i}')
            if not response:
                return "Please complete all mappings before continuing."
            mappings.append({
                "motivation": motivation,
                "behavior": f"I eat meat: {player.meat_consumption}",
                "direction": response
            })

        player.motivation_behavior_links = json.dumps(mappings)

# page sequence 
page_sequence = [
    # SocialCircleDistribution,--> put in again
    # AttentionPage, --> put in again
    # Introduction, --> put in again
    # MeatScale, --> put in again
    # Demographics, --> put in again
    # QUESTIONS 
    Question1, 
    Question2, 
    Question3, 
    Question4,
    # GENERATE + SELECT BELIEFS 
    LLMGenerate,
    #RatePersonalBehavior,
    #AccuracyPersonalBehavior, # I mean of course looks terrible right now
    #MotivationBehaviorMapping,
    BeliefAccuracyRating,
    LLMReviewRevise,
    #LLMReviewRevise,
    #LLMAddBeliefs, # Need to figure out whether this would be on each page 
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
    # PolicyQuestionnaire,
    Demographics, 
    Results
]