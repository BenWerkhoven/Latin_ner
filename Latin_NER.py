import streamlit as st
import spacy
import json
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from spacy import displacy

# Hier wordt het model gecached. Dit houdt in dat het model een keer geladen wordt als de gebruiker de app opstart, maar daarna hoeft het model niet weer opnieuw geladen te worden als de gebruiker het script laat lopen (na input te leveren bijvoorbeeld)
@st.cache(allow_output_mutation = True)
def load_model(model_name):
    nlp = spacy.load(model_name)
    return nlp

def load_data(file, json_file=True):
    # Laad data in, kies of het uit een json komt of uit een gewoon txt bestand
    if json_file:
        with open (file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        with open (file, "r", encoding="utf-8") as f:
            data = f.read()
    return (data)

def clean_text(text):
    # Corpus is nog wat rommelig, deze functie schoont die op zodat die goed getokenised kan worden
    cleaned = re.sub(r"[\(\[].*?[\)\]]", "", text)
    cleaned = cleaned.replace('\n\n','').replace('\n','').replace(' .','.').replace('.','. ')
    cleaned = cleaned.replace('   ',' ').replace('  ',' ').replace('"','')
    #cleaned = replace_jv(cleaned).strip()
    cleaned = cleaned.replace('v','u').replace('j','i').replace('V','U').replace('J','I').strip()
    
    return cleaned

def corpus_preproces(text):
    # Als de text opgeschoond is 
    words = word_tokenize(text)
    que_words = load_data("data\que_woorden.json")
    words_split = []
    for word in words:
        if (word.endswith('que')) & (word not in que_words):
            word = word.split('que')[0]
            words_split.append('que')
            words_split.append(word)
        elif word in ['BOOK','ONE','TWO','THREE','FOUR','FIVE','SIX','SEVEN','EIGHT','NINE','TEN','ELEVEN','TWELVE','THIRTEEN']:
            pass
        else:
            words_split.append(word.strip())
    # Voeg nu de woorden weer samen
    corpus_preprocessed = ' '.join(words_split)
    # Verwijder spaties voor leestekens
    #corpus_preprocessed = corpus_preprocessed.replace(' ,', ',').replace(' .', '.').replace(' ;', ';').replace(' :', ':').replace(' ?', '?').replace(' !', '!')
        
    # We willen het model trainen op zin niveau. Hiervoer moet de text op zinnen gesplitst worden, maar dat gaat soms mis als er afkortingen worden gebruikt.
    # Dit stukje code kan omgaan met afkortingen die in de lijst staan
    punkt_param = PunktParameters()
    abbreviation = ['a', 'd', 'u','kal', 'apr', 'id', 'april', 'cn', 'c','tib','f','m','p','sex']
    punkt_param.abbrev_types = set(abbreviation)
    tokenizer = PunktSentenceTokenizer(punkt_param)
    corpus_sents = tokenizer.tokenize(corpus_preprocessed)
    #
    corpus_sents = ' \n\n'.join(corpus_sents)
    
    return corpus_sents

nlp = load_model("models/model-best")

st.title('Latin NER')

# Normaal gesproken runt streamlit de hele code bij elke klik van de gebruiker.
# Een form maakt een kleine omgeving waar de gebruiker aanpassingen kan doen (input kan leveren) zonder dat de hele script loopt, tot dat op de knop gedrukt wordt. Dit is essentieel als de script lang duurt
form1 = st.sidebar.form(key = 'Opties')
form1.header('Latijnse tekst:')

#ent_types = form1.multiselect('Kies de entities die je wil zien',["PERSON","ORG","GPE"])

text = form1.text_area('Voorbeeld tekst', 'Gallia omins divisa est in partes tres')

form1.form_submit_button('Analyseer!')
#sentence, sent_preproc, hits = analyse_sent(text, nlp, ent_types)
#st.write(sent_preproc)
#st.write(hits)

#spacy_streamlit.visualize(nlp, text)
sentence_clean = clean_text(text)
corpus_proc = corpus_preproces(sentence_clean)
ent_html = displacy.render(nlp(corpus_proc), style="ent", jupyter=False)
st.markdown(ent_html, unsafe_allow_html=True)