import nltk
import dash
import nltk
import difflib
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
from nltk.cluster.util import cosine_distance
from dash.dependencies import Input, Output, State
from sklearn.ensemble import RandomForestClassifier

external_stylesheets = ['']

colors = {
    'background': '#ffffff',
    'banner': '#ffff00',
    'text1': '#000000',
    'text2': '#000000'
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,show_undo_redo=False)

header = html.Div(style={'backgroundColor': colors['banner'], 'font-family': 'Century Gothic', 'height':'175px' }, children=[
    html.H1(
        children = 'Syntax PR Co.',
        style = {
            'font-size': '65px',
            'textAlign': 'center',
            'color' : colors['text1']
        }
    ),
    html.Div(
        children = 'Examine Your Speechwriting',
        style = {
            'font-size': '35px',
            'textAlign': 'center',
            'color': colors['text2']
        }
    ),
])

app.title = "Speech Checker"
app.layout = html.Div(style= {'backgroundColor': colors['background']},
    children = [
        header,
        dcc.Tabs(id="tabs-example", value='tab-1-example', style={'textAlign':'center'}, children=[
            dcc.Tab(label='Input Speech', id='inputTab', children = [
                dcc.Textarea(
                    id='inputText',
                    placeholder='Enter a speech...',
                    style={'width':'100%','height':'400px'}
                ),
                html.Button('Submit', id='sumbitButton', style={'height':'40px','width':'140px'})
            ]), #tab 1
            dcc.Tab(label='Speech Analysis', id='outputTab', style={'textAlign':'center'}, children = [
                html.Div(id='scoreDisplay',children='No Speech Entered',style={'font-family': 'Century Gothic','font-size': '35px','textAlign': 'center','border-width':'8px'}),
                html.Div(id='outputContent',children='',style={'textAlign': 'center'})
            ]) #tab 2
        ]) #tabs obj
    ]) # entire layout

### Training
X = [
    [0.2206770320260939, 0.16444150300872848, 0.26751448186390947, 0.58712533150487, 0.5050302214253439, 0.6801564703521834, 0.5890299449491577, 0.5561725977374865, 0.6233668124636911],
    [0.21909331149281452, 0.16822689873957603, 0.2826479644797504, 0.5679722102197743, 0.4622933870068829, 0.6686992907910609, 0.5533959611271846, 0.5206761695675282, 0.5981738554805685],
    [0.18639193230159604, 0.13879495860288443, 0.20927516051956438, 0.5782069232444341, 0.5024750410242014, 0.6583653027793185, 0.5858910942585438, 0.5664235386626175, 0.6131445223876603],
    [0.22479072982187454, 0.18636712941809297, 0.26951768909072904, 0.6577229024142464, 0.5874365398901084, 0.7356621954845705, 0.5518841529444279, 0.5249945243930422, 0.5796050147073137],
    [0.17064183606190358, 0.13184682346106283, 0.20599061296683502, 0.49838191720146113, 0.3965624149541385, 0.5987464416853956, 0.5680601664983725, 0.5259715344172728, 0.627135788291258],
    [0.1848718815401489, 0.13693315333732198, 0.2102304448015972, 0.5141976142890523, 0.4084460467781959, 0.6410679832199497, 0.6078637832180149, 0.5805887283151228, 0.6523637058160225]
]

y = [1,1,0,0,0,0]
clf = RandomForestClassifier(n_estimators=500, max_depth=None, random_state=720)
clf.fit(X, y)
###
### DATA PREP
speeches = []
for title in ['MLK','JFK','FDR1','FDR2','RR']:
    filename =  "Speeches/" + title + '.txt'
    file = open(filename).read()
    tokens = nltk.sent_tokenize(file)
    for s in range(len(tokens)):
        tokens[s] = nltk.word_tokenize(tokens[s])
    speeches.append(tokens)
lengths = []
for speech in speeches:
    for sent in speech:
        lengths.append(len(sent))
lengths = np.array(lengths)
lower = np.percentile(lengths,35)
upper = np.percentile(lengths,70)
def syllable_count(word):
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count
speeches_pos = []
speeches_syl = []
for speech in speeches:
    speech_pos = []
    speech_syl = []
    for sent in speech:
        sent_pos = nltk.pos_tag(sent)
        sent_pos = [i[1] for i in sent_pos]
        speech_pos.append(sent_pos)
        sent_syl = []
        for word in sent:
            sent_syl.append(syllable_count(word))
        speech_syl.append(sent_syl)
    speeches_pos.append(speech_pos)
    speeches_syl.append(speech_syl)
def similarity(sent1, sent2):

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    for w in sent1:
        vector1[all_words.index(w)] += 1

    for w in sent2:
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)
###

## FIXME:
@app.callback([
    Output('scoreDisplay', 'children'),
    Output('outputContent', 'children')],
    [Input('sumbitButton', 'n_clicks')],
    [State('inputText', 'value')])
def update_output(n_clicks, value):
    if n_clicks is not None:
        inputSpeech = nltk.sent_tokenize(value)
        for s in range(len(inputSpeech)):
            inputSpeech[s] = nltk.word_tokenize(inputSpeech[s])

        pos_inputSpeech = []
        syl_inputSpeech = []

        for sent in inputSpeech:
            sent_pos = nltk.pos_tag(sent)
            sent_pos = [i[1] for i in sent_pos]
            pos_inputSpeech.append(sent_pos)
            sent_syl = []
            for word in sent:
                sent_syl.append(syllable_count(word))
            syl_inputSpeech.append(sent_syl)

        # loop through each sentence
        lexCompare = []
        posCompare = []
        sylCompare = []

        for sent in range(len(inputSpeech)):

            if len(inputSpeech[sent]) <= lower:
                percentile = 0
            elif len(inputSpeech[sent]) < upper:
                percentile = 1
            else:
                percentile = 2

            allLex = []
            allPos = []
            allSyl = []

            for speech in range(len(speeches)):
                for sent2 in range(len(speeches[speech])):
                    if percentile == 0:
                        if len(speeches_pos[speech][sent2]) <= lower:
                            allLex.append(similarity(inputSpeech[sent],speeches[speech][sent2]))
                            allPos.append(similarity(pos_inputSpeech[sent],speeches_pos[speech][sent2]))
                            allSyl.append(difflib.SequenceMatcher(None,syl_inputSpeech[sent],speeches_syl[speech][sent2]).ratio())
                    elif percentile == 1:
                        if len(speeches_pos[speech][sent2]) > lower and len(speeches_pos[speech][sent2]) < upper:
                            allLex.append(similarity(inputSpeech[sent],speeches[speech][sent2]))
                            allPos.append(similarity(pos_inputSpeech[sent],speeches_pos[speech][sent2]))
                            allSyl.append(difflib.SequenceMatcher(None,syl_inputSpeech[sent],speeches_syl[speech][sent2]).ratio())
                    else:
                        if len(speeches_pos[speech][sent2]) >= upper:
                            allLex.append(similarity(inputSpeech[sent],speeches[speech][sent2]))
                            allPos.append(similarity(pos_inputSpeech[sent],speeches_pos[speech][sent2]))
                            allSyl.append(difflib.SequenceMatcher(None,syl_inputSpeech[sent],speeches_syl[speech][sent2]).ratio())

            lexAvg = np.mean(allLex)
            lexCompare.append(lexAvg)

            posAvg = np.mean(allPos)
            posCompare.append(posAvg)

            sylAvg = np.mean(allSyl)
            sylCompare.append(sylAvg)

        dataForML = [np.mean(lexCompare),np.percentile(lexCompare,25),np.percentile(lexCompare,75),
                    np.mean(posCompare),np.percentile(posCompare,25),np.percentile(posCompare,75),
                    np.mean(sylCompare),np.percentile(sylCompare,25),np.percentile(sylCompare,75)]

        print(dataForML)
        score = clf.predict([dataForML])

        goodMessage = "This Speech is Ready!"
        badMessage = "This Speech is Not Ready Yet"

        if score[0] == 1:
            return goodMessage, value
        else:
            return badMessage, value

if  __name__ == '__main__':
    app.run_server(debug=True)
