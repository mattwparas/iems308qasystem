import re
from nltk.corpus import stopwords

# identify which sentences may have a company in it
def identify_potential_sentence(sentence):
  matches = re.findall(r"(?=([A-Z][a-z]+ [A-Z][a-z]+))", sentence)
  if matches:
      return matches
  else:
      return False

# removes the stop words from a found match
def remove_stop_words(word):
  stop_words = set(stopwords.words('english'))
  cleaned_word = ' '.join([x for x in word.split(' ') if x.lower() not in stop_words]).rstrip()
  return cleaned_word


def find_ceo_matches(list_of_sentences):
  # filter keywords
  bad_keywords = set(['Inc', 'inc', 'Corp', 'corp', 'corporation', 'Co', 'company', 'Company', 'Group', 'Ltd', 'ltd', 'Capital', 'capital',
                     'management', 'Management', 'Financial', 'financial', 'consulting', 'Consulting', 'Depot', 'China', 'USA', 'Asia', 'North America',
                     'Administration', 'Department', 'Business', 'Industry', 'Institute', 'United', 'States', 'Asia', 'Europe', 'New', 'York', 'Chicago',
                     'Houston', 'Los', 'Angeles', 'National', 'President', 'Representative', 'House', 'Representatives', 'Senator', 'CFO', 
                     'Mojave', 'Desert', 'Olympics', 'Obama', 'Secretary', 'General', 'Inspector', 'Advisor', 'Economic', 'Atlantic', 'Gulf', 'Pacific', 'Ocean', 
                     'Finance', 'Wall Street', 'Wall', 'Street', 'Federal', 'Affordable', 'Republicans', 'Democrats', 'Congressional', 'Aviation', 'Internet', 'Hong', 
                     'Kong', 'Beijing', 'Africa', 'Russia', 'Government', 'Research', 'Council', 'Public', 'Service', 'Mobility', 'Bitcoin', 'Economy', 'Commodity',
                     'Prices', 'Presentation', 'Citi', 'Navy', 'Jewish', 'Muslim', 'Journal', 'British', 'Zillow', 'Egypt', 'Congo', 'Kitchen', 'Thrift', 'Savings', 
                     'Director', 'Iraq', 'Iran', 'War', 'Saudi', 'Arabia', 'Oil', 'Turkey', 'Greece', 'Investment', 'Production', 'User', 'Experience', 'Western',
                     'Eastern', 'Bank', 'Access', 'Debt', 'Growth', 'Resources', 'Brazil', 'Mexico', 'Canada', 'Canadian', 'American', 'English', 'Chinese', 
                     'Dangerous'])

  potential_matches = []

  for sentence_index, sentence in enumerate(list_of_sentences):
      matches = identify_potential_sentence(sentence) 
      if matches:
          filtered_matches = []
          # filter out the matches with annoying APBloomberg or AP stuff in it
          for match in matches:
              if " " + match + " " in sentence:
                  filtered_matches.append(match)
              elif sentence[:len(match)+1 == match + " "]:
                  filtered_matches.append(match)                 
              elif sentence[-len(match)+1:] == " " + match:
                  filtered_matches.append(match)
          
          filtered_2 = []
          for match in filtered_matches:
              split_word = match.split(' ')
              if split_word[0] not in bad_keywords and split_word[1] not in bad_keywords:
                  filtered_2.append(match)
                  
          cleaned_matches = [remove_stop_words(x) for x in filtered_2]
          remove_empty_words = [x for x in cleaned_matches if x != '']
          for match in remove_empty_words:
              potential_matches.append(match)

  return potential_matches