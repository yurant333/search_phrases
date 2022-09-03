
# Подключаемся из Google colub к Google drive, предварительно скопировав файл с таблицей к себе на диск
from google.colab import drive
drive.mount('/content/gdrive')

# Подключаем Pandas
import pandas as pd
# Считываем таблицу в переменную
df = pd.read_table('gdrive/MyDrive/test_files/test_data.csv', sep = ',')

# Устанавливаем последнюю версию Spacy
!pip install spacy
# Скачиваем большую версию русского словаря из Spacy
!python -m spacy download ru_core_news_lg

# Создадим список приветствий
greetings_pattern_1 = [{'TEXT': 'привет'}] 
greetings_pattern_2 = [{'TEXT':{'REGEX': 'добр[а-я]{2}'}}, 
                       {'TEXT':{'REGEX': 'ут[а-я]{2}'}}] 
greetings_pattern_3 = [{'TEXT': {'REGEX': 'добр[а-я]{2}'}},
                       {'TEXT': {'REGEX': 'д[а-я]{2}'}}] 
greetings_pattern_4 = [{'TEXT': {'REGEX': 'добр[а-я]{2}'}},
                       {'TEXT': {'REGEX': 'веч[а-я]{2}'}}] 
greetings_pattern_5 = [{'TEXT': 'здравствуйте'}] 
greetings_pattern_6 = [{'TEXT': {'REGEX': 'зд[a,о]рова'}}] 
greetings_pattern_7 = [{'TEXT': 'приветствую'}]
greetings_pattern_8 = [{'TEXT': {'REGEX': 'здра[с|сь]те'}}]
greetings_pattern_9 = [{'TEXT':'добрый'}]
greetings_list = [greetings_pattern_1, 
                  greetings_pattern_2, 
                  greetings_pattern_3, 
                  greetings_pattern_4, 
                  greetings_pattern_5, 
                  greetings_pattern_6, 
                  greetings_pattern_7, 
                  greetings_pattern_8, 
                  greetings_pattern_9]
# Создадим список прощаний
partings_pattern_1 = [{'TEXT': 'до'},
                      {'TEXT': {'REGEX': 'свидан[ь|и]я'}}]
partings_pattern_2 = [{'TEXT': 'хорошего'},
                      {'TEXT': {'REGEX': '[вечера|дня]'}}]
partings_pattern_3 = [{'TEXT': 'всего'},
                      {'TEXT': {'REGEX': '[доброго|хорошего|наилучшего]'}}]
partings_pattern_4 = [{'TEXT': {'REGEX': 'проща[й|те]'}}]
partings_pattern_5 = [{'TEXT': {'REGEX': 'пок[а|асики]'}}]
partings_pattern_6 = [{'TEXT': 'чао'}] 
partings_pattern_7 = [{'TEXT': {'REGEX': '[гудб|б]ай'}}] 
partings_pattern_8 = [{'TEXT': 'ауфидерзейн'}] 
partings_pattern_9 = [{'TEXT': 'бывай'}] 
partings_pattern_10 = [{'TEXT': 'покедова'}] 
partings_pattern_11 = [{'TEXT': 'досвидос'}]
partings_list = [partings_pattern_1, 
                 partings_pattern_2, 
                 partings_pattern_3, 
                 partings_pattern_4, 
                 partings_pattern_5, 
                 partings_pattern_6, 
                 partings_pattern_7, 
                 partings_pattern_8, 
                 partings_pattern_9, 
                 partings_pattern_10, 
                 partings_pattern_11]
# Создадим список представления имени 
introduced_pattern_1 = [{'TEXT': 'меня'}, 
                        {'TEXT': 'зовут'}] 
introduced_pattern_2 = [{'TEXT': 'моё'},
                        {'TEXT': 'имя'}]
introduced_pattern_3 = [{'TEXT': {'REGEX': 'это'}}, 
                        {'POS': 'PROPN'}]
introduced_list = [introduced_pattern_1, 
                   introduced_pattern_2, 
                   introduced_pattern_3]
# Создадим список поиска компании
search_name_company_pattern_1 = [{'TEXT': 'это компания'},
                                 {'POS': 'PROPN'}] 
search_name_company_pattern_2 = [{'TEXT': 'компания'},
                                 {'POS': 'PROPN'}]
search_name_company_pattern_3 = [{'TEXT': 'это из компании'},
                                 {'POS': 'PROPN'}]
search_name_company_pattern_4 = [{'TEXT': 'компания'},
                                 {'POS': 'NOUN'}]
search_name_company_pattern_5 = [{'TEXT': 'компания'},
                                 {'POS': 'VERB'},
                                 {'POS': 'NOUN'}]
search_name_company_list = [search_name_company_pattern_1, 
                            search_name_company_pattern_2, 
                            search_name_company_pattern_3, 
                            search_name_company_pattern_4,
                            search_name_company_pattern_5]
# Скачаем заранее список имен, так как в Spacy на готовом словаре нельзя отделить имя сотрудника от имени собстенного.
import requests
url_male_names = 'https://raw.githubusercontent.com/Raven-SL/ru-pnames-list/master/lists/male_names_rus.txt'
url_female_names = 'https://raw.githubusercontent.com/Raven-SL/ru-pnames-list/master/lists/female_names_rus.txt'
names_list=[]
for  name in requests.get(url_male_names).text.split():
  names_list.append(name.lower())
for  name in requests.get(url_female_names).text.split():
  names_list.append(name.lower())

# Далее напишем ряд вспомогательных функций для поиска реплик
# Импортируем модуль Spacy
import spacy
# Инициализируем контейнер конвейра с русским словарем
nlp = spacy.load('ru_core_news_lg')
# Из Spacy загрузим метод Matcher для поиска фраз в диалоге
from spacy.matcher import Matcher    
# Создадим функцию поиска представлений сотрудника
def is_greeting(df):
  matcher = Matcher(nlp.vocab)
  for index, row in df.iterrows():
    if (row['role']=='manager'):
      text = nlp(row['text'].lower())
      matcher.add('Greeting', greetings_list)
      matches = matcher(text)
      if matches !=[]:
        # Установим флаг приветствия
        if df['insight'].iloc[index]=='':
          df['insight'].iloc[index]='greeting=True'
        else:
          df['insight'].iloc[index]=df['insight'].iloc[index] + ', ' + 'greeting=True'
        # Вычленим фразу из реплики с приветствием
        for match_id, start, end in matches: 
          span = text[start:end]                   
          if df['phrases'].iloc[index]=='':
            df['phrases'].iloc[index]='is_greeting_phrases="' + span.text + '"'
          else:
            df['phrases'].iloc[index]=df['phrases'].iloc[index] + ', ' + 'is_greeting_phrases="' + span.text + '"'
# Создадим функцию поиска прощаний сотрудника, алгоритм функции аналоничен функции поиска представлений сотрудника
def is_parting(df):
  matcher = Matcher(nlp.vocab)
  for index, row in df.iterrows():
    if (row['role']=='manager'):
      text = nlp(row['text'].lower())
      matcher.add('Partings', partings_list)
      matches = matcher(text)
      if matches !=[]:
        if df['insight'].iloc[index]=='':
          df['insight'].iloc[index]='parting=True'
        else:
          df['insight'].iloc[index]=df['insight'].iloc[index] + ', ' + 'parting=True' 
        for match_id, start, end in matches: 
          span = text[start:end]                   
          if df['phrases'].iloc[index]=='':
            df['phrases'].iloc[index]='is_parting_phrases="' + span.text + '"'
          else:
            df['phrases'].iloc[index]=df['phrases'].iloc[index] + ', ' + 'is_parting_phrases="' + span.text + '"'
# Создадим функцию поиска представления сотрудника
def is_introduced(df):
  matcher = Matcher(nlp.vocab)
  for index, row in df.iterrows():
    if (row['role']=='manager'):
      text = nlp(row['text'].lower())
      matcher.add('Introduced', introduced_list)
      matches = matcher(text)
      if matches !=[]:
        for match_id, start, end in matches: 
          span = text[start:end]
          if df['phrases'].iloc[index]=='':
            df['phrases'].iloc[index]='is_introduced_phrases="' + span.text + '"'
          else:
            df['phrases'].iloc[index]=df['phrases'].iloc[index] + ', ' + 'is_introduced_phrases="' + span.text + '"'
# Создадим функцию поиска названия компании
def search_name_company(df):
  matcher = Matcher(nlp.vocab)
  for index, row in df.iterrows():
    if (row['role']=='manager'):
      text = nlp(row['text'].lower())
      matcher.add('Search_name_company', search_name_company_list)
      matches = matcher(text)
      if matches !=[]:
        for match_id, start, end in matches: 
          span = text[start+1:end]
          if df['phrases'].iloc[index]=='':
            df['phrases'].iloc[index]='search_name_company_phrases="' + span.text + '"'
          else:
            df['phrases'].iloc[index]=df['phrases'].iloc[index] + ', ' + 'search_name_company_phrases="' + span.text + '"'
# Создадим функцию поиска имени сотрудника
def search_name_manager(df):
  matcher = Matcher(nlp.vocab)
  for index, row in df.iterrows():
    if (row['role']=='manager'):
      text = nlp(row['text'].lower())
      matcher.add('Introduced', introduced_list)
      matches = matcher(text)
      if matches !=[]:
      # Для поиска имени применим атрибут ents и сравним значения со списком имен
        for names in text.ents:
          if df['phrases'].iloc[index]=='' and str(names) in names_list:
            df['phrases'].iloc[index]='search_name_manager_phrases="' + str(names) + '"'
          elif df['phrases'].iloc[index]!='' and str(names) in names_list:
            df['phrases'].iloc[index]=df['phrases'].iloc[index] + ', ' + 'search_name_manager_phrases="' + str(names) + '"'
          else:
            continue
# Создадим функцию проверки приветствия-прощания сотрудника          
def is_greeting_and_parting(df):
  for dlg_id in df['dlg_id'].unique():
    if len(df[(df['dlg_id'] == dlg_id) & (df['insight'] != '')]['insight'].unique()) == 2:
      print('В диалоге ', str(dlg_id), ' приветствие-прощание выполнено')
    else:
      print('В диалоге ', str(dlg_id), ' приветствие-прощание не выполнено')

# Создадим столбцы с репликами и флагами приветствия
df['phrases']=''
df['insight']=''
# Вызовем вспомогательные функции
is_greeting(df)
is_parting(df)
is_introduced(df)
search_name_manager(df)
search_name_company(df)

# Вызовем главную функцию проверки условия приветствия-прощания сотрудника
is_greeting_and_parting(df)