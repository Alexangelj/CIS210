"""
  Too Many Pins.  Assignment 1, Part 1 CIS 210
  Author: Alexander Angel
  Credits: None
  
  Convert pins and integers into vowel-consonant pairs which are pronounceable nonsense words.
  """

import argparse

error_message = 'Argument not valid. Please use a positive integer.'

def alphacode(pin):
    """
    Convert numeric pin code to an
    easily pronounced mnemonic.
    args:
        pin:  code as positive integer
    returns:
        mnemonic as string
    """
    mnemonic = ''
    vowels = list(''.join('aeiou'))
    consonants = list(''.join('bcdfghjklmnpqrstvwyz'))  
    while pin > 0:
        try:
            i = pin % 100
            pin = pin // 100
            remainder = i % 5
            quotient = i // 5
            mnemonic += str(vowels[remainder] + consonants[quotient])
        except TypeError:
            return error_message
    if pin < 1:
        return mnemonic[::-1]

def main():
    """
    Interaction if run from the command line.
    Magic for now; we'll look at what's going on here
    in the next week or two. 
    """
    parser = argparse.ArgumentParser(description="Create mnemonic for PIN code")
    parser.add_argument("PIN", type=int, 
                        help="personal identifier number (an integer)")
    args = parser.parse_args()  # gets arguments from command line
    pin = args.PIN
    mnemonic = alphacode(pin)
    print('Encoding of {} is {}'.format(pin,mnemonic))

if __name__ == "__main__":
    main()     