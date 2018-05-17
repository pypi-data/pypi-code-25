'''
Created on 05 mag 2018

@author: Simone
'''
from supwsd.wsd import SupWSD

'''
Created on 03 mag 2018

@author: Simone Papandrea
'''


def version():
    return SupWSD().version();
       
def model():
    return SupWSD().model();
    
def disambiguate_text():
    disambiguate("The human brain is quite proficient at word-sense disambiguation. The fact that natural language is formed in a way that requires so much of it is a reflection of that neurologic reality.") 
    
def disambiguate_tags():
    disambiguate("The human " + SupWSD.SENSE_TAG + "brain" + SupWSD.SENSE_TAG + " is quite proficient at word-sense disambiguation. The fact that natural language is formed "+ SupWSD.SENSE_TAG+"in a way"+ SupWSD.SENSE_TAG+" that requires so much of it is a " + SupWSD.SENSE_TAG + "reflection" + SupWSD.SENSE_TAG + " of that neurologic reality.")
    
def disambiguate(text):

    for sense in SupWSD().senses(text):
        print("Word: {}\tLemma: {}\tPOS: {}\tSense: {}\tSource: {}\tCount: {}\tValid: {}\tMiss: {}".format(sense.word, sense.lemma, sense.pos,sense.key(),sense.source,sense.count(),sense.valid(),sense.miss()))

        for result in sense.results:
            print("Sense {}\tProbability: {}".format(result.key, result.prob))
            
              
if __name__ == '__main__':
        
    print("===============TESTING SUPWSD INFO===============")
    print("SupWSD Version: {}\tTraining data: {}".format(version(), model()))

    print("\n===============TESTING SUPWSD TAG===============")    
    disambiguate_tags();        
    
    print("\n===============TESTING SUPWSD TEXT===============");
    disambiguate_text()                  
        
    print("=====================DONE=====================")   