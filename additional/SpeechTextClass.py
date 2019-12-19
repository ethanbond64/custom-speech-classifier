fullList = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z','1','2','3','4','5','6','7','8','9','0','-',"'",'%','$','&','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
endList = ['.','!','?',',']
import numpy as np
from english import english
from english10 import english10
from stopwords import stopwords
def tokenize(inText,speech):
    outText = []
    sent = []
    spaceLocations = []

    for letter in range(len(inText)):
        if inText[letter] == ' ':
            spaceLocations.append(letter)

    # Add the first word
    sent.append(inText[0:spaceLocations[0]].lower())
    # Add all the words in the middle
    for loc in range(len(spaceLocations)-1):
        nextWord = inText[spaceLocations[loc]+1:spaceLocations[loc+1]].lower()
        if len(nextWord) > 0:

            if nextWord[-1] in endList:
                sent.append(nextWord[0:len(nextWord)-1])
                outText.append(sent)
                sent = []
            else:
                sent.append(nextWord)

    # Keep this for when a single sentence is entered
    if len(sent) > 0:
        outText.append(sent)

    # Add the last word, either break into word and '.' or leave it alone
    lastWord = inText[spaceLocations[-1]+1:]
    if lastWord[-1] in endList:
        outText[-1].append(lastWord[:-1])
    else:
        outText[-1].append(lastWord)

    return outText

# def tokenizeSpeech(inText):
#     inText.split('\n')
#     print()

def commonScore(lis1,lis2):
    score = 0
    for i in lis1:
        if i in lis2:
            score += 1
    return score

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

def syllablize(tokens):
    maxx = 0
    for sentence in tokens:
        if len(sentence) > maxx:
            maxx = len(sentence)
    
    outMatrix = []
    for sent in tokens:
        nextSent = np.zeros(maxx)
        for word in range(len(sent)):
            nextSent[word] = syllable_count(sent[word])
        outMatrix.append(nextSent)
    return np.matrix(outMatrix)

class speechText:

    def __init__(self,filename,speech=True,toke=True,syl=True,common=False):
        with open(filename,'r') as corpus:
            Corpus = ''
            for let in corpus:
                Corpus += let
        corpus.close()
        self.string = Corpus
        if toke == True and speech == True:
            self.tokens = tokenize(self.string,True)
        else:
            self.tokens = tokenize(self.string,False)
        if syl == True:
            self.syllables = syllablize(self.tokens)
        if common == True:
            self.commons = commonWords(self.tokens)
        return


    def findSimilar(inText):
        wordList = textToList(inText)
        similarSets = []
        lilSet = []

        # First word
        lilSet.append(wordList[0])

        for ii in range(3,len(wordList)):
            if (wordList[ii-2] in endList) and (wordList[ii] == wordList[1]) and (wordList[ii-1] not in lilSet):
                lilSet.append(wordList[ii-1])

        if len(lilSet) > 1:
            similarSets.append(lilSet)

        # Rest of the words
        for bb in range(1,len(wordList)-1):

            if wordList[bb] not in endList:
                context = [wordList[bb-1],wordList[bb+1]]
                lilSet = [wordList[bb]]
                existing = False
                listLocation = 0
                #find if the word is already documented
                if len(similarSets) != 0:
                    for kk in range(len(similarSets)):
                        if wordList[bb] in similarSets[kk]:
                            existing = True
                            listLocation = kk

                for pp in range(bb+1,len(wordList)-1):
                    if (wordList[pp-1] == context[0]) and (wordList[pp+1] == context[1]) and (wordList[pp] not in lilSet):
                        if existing == False:
                            lilSet.append(wordList[pp])
                        else:
                            if wordList[pp] not in similarSets[listLocation]:
                                similarSets[listLocation].append(wordList[pp])

                if len(lilSet) > 1:
                    similarSets.append(lilSet)

        return similarSets
