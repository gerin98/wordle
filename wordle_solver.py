import numpy as np
import enchant
from collections import defaultdict
from collections import Counter

'''
First set all known letters
'''
def tryKnownLetters(possibleWord, knownLetters):
    for i in knownLetters:
        possibleWord[i] = knownLetters[i]
    return possibleWord

'''
Each recursion takes care of one position and tries all possible letters at that position
'''
def tryPossibleLetters(possibleWord, letters, positions):
    position = positions.pop(0)
    possibleLetters = letters[position]
    remainingLetters = {p:letters[p] for p in set(letters).intersection(positions)}
    remainingPositions = list(remainingLetters.keys())

    possibleWords = []
    for pl in possibleLetters:
        possibleWord[position] = pl
        if (len(remainingPositions) > 0):
            moreWords = tryPossibleLetters(possibleWord.copy(), remainingLetters.copy(), remainingPositions.copy())
            possibleWords.append(moreWords)
        else:
            possibleWords.append("".join(possibleWord))

    return possibleWords

'''
Some of the guesses may not be valid in the case that the permutation didn't use a misplaced 
letter at all. Remove those guesses before proceding
guessesSoFar: list of strings (guesses)
misplacedLetters: dict { key = letter, value = indices of letter }
'''
def verifyValidGuesses(guessesSoFar, misplacedLetters):
    validGuessesSoFar = []
    for guess in guessesSoFar:
        validWord = True
        for l in misplacedLetters:
            containsLetter = False
            for pos in misplacedLetters[l]:
                if (guess[pos] == l):
                    containsLetter = True
                    break
            validWord = validWord & containsLetter
            if (not validWord):
                break
        if (validWord):
            validGuessesSoFar.append(guess)
    return validGuessesSoFar

'''
Convert 2-D array of characters back into words
'''
def convertToWords(wordTile):
    guesses = []
    for word in wordTile.transpose():
        guesses.append("".join(word))
    return guesses

'''
Fill in the blanks of the initialGuess with the given letters.
Return all possible combinations
'''
def generateGuesses(initialGuess, letters, blank):
    np_word = np.array(list(initialGuess)).reshape(-1,1)
    np_letters= np.array(list(letters))

    wordTile = np.tile(np_word, len(letters))
    wordTile[blank] = np_letters

    return convertToWords(wordTile)

'''
Generate all possible guesses
'''
def allGuessesForWord(guesses, letters):
    for g in guesses:
        try:
            blank = guesses[0].index('_')
        except ValueError:
            break
        
        gfw = generateGuesses(guesses[0], letters, blank)
        
        for w in gfw:
            guesses.append(w)

        if (len(gfw) > 0):
            guesses.pop(0)
        else:
            break
    return guesses

def reverseDict(dict):
    d = defaultdict(list)
    newdict = [(letter, pos) for pos,letters in dict.items() for letter in letters ]

    for t in newdict:
        d[t[0]].append(t[1])
    
    return d

def inputGetKnownLetters():
    knownLetters = {}
    knownLettersInput = input("Enter known letters and their position eg. \"2:u, 4:b\": \n")
    knownLettersInput = ''.join(knownLettersInput.split())
    if (len(knownLettersInput) == 0):
        return knownLetters

    tokens = knownLettersInput.split(",")
    for token in tokens:
        t = token.split(":")
        knownLetters[int(t[0])] = t[1]
    
    return knownLetters

def inputGetUnusedLetters():
    unusedLettersInput = input("Enter unused letters eg. \"u, b, s\": \n")
    unusedLettersInput = ''.join(unusedLettersInput.split())
    unusedLetters = unusedLettersInput.split(",")
    return unusedLetters

def inputGetMisplacedLetters():
    possibleLetters = {}
    misplacedLetters = {}
    misplacedLettersInput = input("Enter misplaced letters and their position eg. \"2:{u,b}, 4:{u,b}\": \n")
    misplacedLettersInput = ''.join(misplacedLettersInput.split())
    if (len(misplacedLettersInput) == 0):
        return possibleLetters, misplacedLetters

    tokens = misplacedLettersInput.split("},")
    
    # create dict keyed by position
    for token in tokens:
        t = token.split(":")
        pos = t[0]
        letters = t[1]
        letters = letters.replace('{', '')
        letters = letters.replace('}', '')
        letters = letters.split(',')
        possibleLetters[int(pos)] = letters

    # reverse the dict to key by letter
    misplacedLetters = reverseDict(possibleLetters)

    # add blanks to dict keyed by pos
    for pos in possibleLetters.values():
        pos.append('_')

    return possibleLetters, misplacedLetters

# Script starts here
def main(letters, knownLetters, possibleLetters, misplacedLetters):
    word = list("_____")
    possibleLetterPositions = list(possibleLetters.keys())

    # place any known letters in the correct spots (green letters)
    word = tryKnownLetters(word, knownLetters)
    
    # try all possible words using known letters initially the wrong spots (yellow letters)
    if (len(possibleLetterPositions) == 0):
        validGuessesSoFar = ["".join(word)]
    else:
        guessesSoFar = list(np.array(tryPossibleLetters(word.copy(), possibleLetters, possibleLetterPositions)).flat)
        validGuessesSoFar = verifyValidGuesses(guessesSoFar, misplacedLetters)

    # try all possible words by filling in the remaining blanks (grey letters)
    allResults = []
    for v in validGuessesSoFar:
        allResults = allResults + allGuessesForWord([v], letters)
    allResults = set(allResults)

    d = enchant.Dict("en_US")

    # filter the english words
    allValidResults = []
    for result in allResults:
        if (d.check(result)):
            allValidResults.append(result)

    print("\n=== Possible Words ===")
    print(allValidResults)

    stats = ''.join(allValidResults)
    c = Counter(stats)

    print("\n=== Stats ===")
    print(c)

if __name__ == "__main__":
    knownLetters = inputGetKnownLetters()
    possibleLetters, misplacedLetters = inputGetMisplacedLetters()
    letters = inputGetUnusedLetters()
    letters = list(set(letters + list(knownLetters.values())))
    main(letters, knownLetters, possibleLetters, misplacedLetters) 
    