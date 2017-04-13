from bs4 import BeautifulSoup
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer

def clean_text(doc, remove_stop_words=True, remove_digits=False, remove_punc=True, stem=False):
    
    # 1. Remove any HTML markup
    text = BeautifulSoup(doc, 'lxml').get_text()  
    
    # 2. Extract special negator like n't
    text = re.sub('n\'t', ' not', text)
    
    # 3. remove punctuation(except .-)
    if remove_punc:
        text = re.sub('[^a-zA-Z.\-\d]', ' ', text)
        
    if remove_digits:
        text = re.sub('[.\d]', ' ', text)
        
    # 4. Convert to lower case 
    text = text.lower()
        
    # 5. Remove stop words
    if remove_stop_words:
        stops = set(stopwords.words("english"))
        text = [w for w in text.split(' ') if not w in stops]
        text = ' '.join(text)
                
    # 6. apply Porter Stemming
    # probably don't need this
    if stem:
        stemmer = PorterStemmer()
        stemmer = LancasterStemmer()
        text = [stemmer.stem(w) for w in text.split(' ')]
        text = ' '.join(text)
        
    # 7. Remove extra white space
    text = re.sub(' +',' ', text)
        
    return text