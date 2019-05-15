"""
Solve a jumble (anagram) by checking against each word in a dictionary
Authors: Alexander Angel
Credits: None    

Usage: python jumbler.py jumbleword wordlist.txt
"""

import argparse

def jumbler(jumble, wordlist):
    """
    Print elements of wordlist that can be rearranged into the jumble.
    Args:
       jumble:  The anagram as a string
       wordlist:  A sequence of words as a file or list
    Returns:  nothing
    Effects:  prints each matching word on an individual line,
              then a count of matching words (or "No matches" if zero)
    """
    matches = 0
    lines = 0
    sorted_jumble = sorted(jumble)
    for word in wordlist:
        word = word.strip()  # Remove spaces or carriage return at ends
        sorted_word = sorted(word)
        if sorted_word == sorted_jumble:
            print(word)
            matches += 1
        lines += 1

    print("{} matches in {} lines".format(matches,lines))


def run_tests():
    """
    Simple test cases for jumbler.  
    Args: none
    Returns: nothing
    Effects:  Prints test results
    """
    shortlist = [ "alpha", "beta", "sister", "gamma", "resist", "theta" ]
    print("Expecting match on alpha:")
    jumbler("phaal", shortlist)
    print("Expecting matches on sister and resist:")
    jumbler("tiress", shortlist)
    print("Expecting no matches:")
    jumbler("alxha", shortlist)
    
def main():
    """
    Interaction if run from the command line.
    Magic for now; we'll look at what's going on here
    in the next week or two. 
    """
    parser = argparse.ArgumentParser(description="Solve a jumble (anagram)")
    parser.add_argument("jumble", type=str, help="Jumbled word (anagram)")
    parser.add_argument('wordlist', type=argparse.FileType('r'),
                        help="A text file containing dictionary words, one word per line.")
    args = parser.parse_args()  # gets arguments from command line
    jumble = args.jumble
    wordlist = args.wordlist
    jumbler(jumble, wordlist)

if __name__ == "__main__":
    #run_tests()   
    main()     

    

    

