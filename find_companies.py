import re
from nltk.corpus import stopwords

# identify which sentences may have a company in it
def identify_potential_sentence(sentence):
    matches = re.findall(r"(?:(?:[A-Z]+[a-z]*) ?)+", sentence)
    if matches:
        return matches
    else:
        return False

# removes the stop words from a found match
def remove_stop_words(word):
    stop_words = set(stopwords.words('english'))
    cleaned_word = ' '.join([x for x in word.split(' ') if x.lower() not in stop_words]).rstrip()
    return cleaned_word

def find_potential_companies(list_of_sentences):
    potential_matches = []
    for sentence_index, sentence in enumerate(list_of_sentences):
        matches = identify_potential_sentence(sentence) 
        if matches:
            # filter out the matches with annoying APBloomberg or AP stuff in it
            cleaned_matches = [remove_stop_words(x) for x in matches]
            remove_empty_words = [x for x in cleaned_matches if x != '']
            for match in remove_empty_words:
                potential_matches.append(match)
    return potential_matches