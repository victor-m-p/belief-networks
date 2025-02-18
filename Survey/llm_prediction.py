import pandas as pd 

def is_numeric_string(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

# data
d = pd.read_csv('data/data_project_1044868_2025_02_11.csv', sep=';')

# just start with one person 
d = d[d['lfdn'] == 22].reset_index()
focal_topic = 'animal products'

### predefined stuff ### 

# predefined questions (omg; also in this crazy format.)
predefined_questions_mapping = {
    0: "Strongly disagree",
    1: "Somewhat disagree",
    2: "Neutral / Not Sure", # "Neither agree nor disagree",
    3: "Somewhat agree",
    4: "Strongly agree",
}
n_answer_options = len(predefined_questions_mapping)

predefined_questions = [
    "I try to reduce my consumption of animal products",
    "I try to reduce my overall carbon footprint",
    "I try to reduce flying", # maybe waste: a bit covered by above
    "I believe in anthropogenic climate change",
    "Animals have feelings", # are sentient? 
    "Animal products are a necessary part of a healthy diet",
    "Animal products taste good", # this is tricky: like could be "some"
    "Most production animals have a good life",
    "Behavioral changes are effective at addressing climate change", # why not animal welfare?
    "Policy changes are effective at addressing climate change",
    "I support a tax on meat specifically",
    "I support a tax on animal products generally"   
]

predefined_idx = [
    # one question per row here: 
    "v_1198", "v_1199", "v_1222", "v_1234", "v_1246",
    "v_1200", "v_1201", "v_1223", "v_1235", "v_1247", 
    "v_1202", "v_1203", "v_1224", "v_1236", "v_1248",
    "v_1204", "v_1205", "v_1225", "v_1237", "v_1249",
    "v_1206", "v_1207", "v_1226", "v_1238", "v_1250",
    "v_1208", "v_1209", "v_1227", "v_1239", "v_1251",
    "v_1212", "v_1213", "v_1229", "v_1241", "v_1253",
    "v_1216", "v_1217", "v_1231", "v_1243", "v_1255",
    "v_1218", "v_1219", "v_1232", "v_1244", "v_1256",
    "v_1220", "v_1221", "v_1233", "v_1245", "v_1257",
    "v_1259", "v_1260", "v_1261", "v_1262", "v_1263",
    "v_1264", "v_1265", "v_1266", "v_1267", "v_1268",
]

predefined_dict = {}
i=-1
for question in predefined_questions: 
    for key, val in predefined_questions_mapping.items(): 
        i+=1
        idx = predefined_idx[i] 
        if d[idx][0]: 
            predefined_dict[question] = {
                "answer_code": key,
                "answer_text": val 
            } 

### political views + demographics ### 
# we need to add some mapping here for clarity eventually 
demographic_cols = [
    'own_pol', # politics
    'down_ind', # beliefs + behaviors point in same direction
    'down_con', # experience no conflict (beliefs + behaviors)
    'temp_dis', # temperature (distraction)
    'temp_dbt', # temperature (attention)
    'gender', # gender
    'age', # age
    'educ' # education
]
df_demographics = d[demographic_cols].melt(var_name="variable", value_name="value")
