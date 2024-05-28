import pandas as pd

def change(x):
    print(x)
    x = x.split('-')
    y = x[0][1:] + ' - ' + x[1]
    return y


dict_mention = {'GSI - CTE': '71', 'GSI - SCOM': '73', 'GSI - DS': '72',
                'CVT - AET': '82', 'CVT - SIC': '81',
                'INFO - IA': '31', 'INFO - MSc AI': '35', 'INFO - ASI': '33', 'INFO - SL': '32', 'INFO - CYBER': '34',
                'ENE - E2': '53', 'ENE - PEG': '52', 'ENE - RE': '51', 'ENE - SES': '54',
                'VSE - ESP': '61', 'VSE - HSB': '62',
                'SCOC - SRI': '41', 'SCOC - MACS': '43', 'SCOC - OCENE': '42',
                'PNT - PSY': '22', 'PNT - QTE': '21',
                'MDS - MMF': '11', 'MDS - SDI-PS': '13', 'MDS - SDI-M': '12', 'MDS - MSc DSBA': '14'}

class FramaFormResult:

    def __init__(self, path_csv_file):
        self.path_csv_file = path_csv_file
        self.used_columns = ["nom", "prenom", "citation", "image", "dominante_mention"]
        self.order = ["dominante_mention", "nom", "prenom"]
        self.nb_student = 0

    def get_json(self):
        df_rdd = pd.read_csv(self.path_csv_file, header=0, sep=';')
        print(df_rdd.columns)

        df_rdd = df_rdd[self.used_columns]
        self.nb_student = df_rdd.shape[0]

        # map dominante_mention to order
        #df_rdd['dominante_mention'] = df_rdd['code passage'].apply(lambda x: change(x))
        df_rdd['dominante_mention'] = df_rdd['dominante_mention'].map(dict_mention)

        # sort values by dominante-mention, name, surname
        df_rdd.sort_values(by=self.order, inplace=True)
        df_rdd.reset_index(drop=True, inplace=True)
        return df_rdd.to_dict('index')

    def get_json_dominante(self, dominante):
        df_rdd = pd.read_csv(self.path_csv_file, header=0, sep=';')
        df_rdd = df_rdd[self.used_columns]
        self.nb_student = df_rdd.shape[0]

        # map dominante_mention to order
        #df_rdd['dominante_mention'] = df_rdd['code passage'].apply(lambda x: change(x))
        df_rdd['dominante_mention'] = df_rdd['dominante_mention'].map(dict_mention)

        # select dominante
        condition = df_rdd['dominante_mention'].str[0] == str(dominante)

        df_rdd = df_rdd[condition]
        df_rdd.reset_index(drop=True, inplace=True)
        return df_rdd.to_dict('index')


    def get_json_master(self):
        df_rdd = pd.read_csv(self.path_csv_file, header=0, sep=';')
        df_rdd = df_rdd[self.used_columns]
        self.nb_student = df_rdd.shape[0]

        # map dominante_mention to order
        #df_rdd['dominante_mention'] = df_rdd['code passage'].apply(lambda x: change(x))
        df_rdd['dominante_mention'] = df_rdd['dominante_mention'].map(dict_mention)

        # select dominante
        condition = df_rdd['dominante_mention'].isin(['45'])

        df_rdd = df_rdd[condition]
        df_rdd.reset_index(drop=True, inplace=True)
        return df_rdd.to_dict('index')

    def get_nb_student(self):
        return self.nb_student



