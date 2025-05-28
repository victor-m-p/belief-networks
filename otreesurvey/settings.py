from os import environ

SESSION_CONFIGS = [
        dict(
         name='SURVEY',
         app_sequence=['otreesurvey_app'],
         num_demo_participants=1,
     ),
]

ROOMS = [
    dict(
        name='belief_network_pretest_20250528',
        display_name='belief_network_pretest_20250528'
    )
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'

# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '5224270508850'
