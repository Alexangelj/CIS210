"""
  Too Many Pins.  Assignment 1, Part 1 CIS 210
  Authors:  Alexander Angel
  Credits: None
  
  Convert pins and integers into vowel-consonant pairs which are pronounceable nonsense words.
  """

import argparse

error_message = 'Argument not valid. Please use an integer.'

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
            print(error_message)
            return error_message
    if pin < 1:
        return mnemonic[::-1]

alphacode(3464140)
def testEQ(test,funcn,result):
    if funcn == result:
        print('True')
    else:
        print('False')

def run_tests():
    """
    This function runs a set of tests to help you debug your
    program as you develop it.
    """
    print("**** TESTING --- examples from course assignment page")
    testEQ("4327 => lohi", alphacode(4327), "lohi")
    testEQ("1298 => dizo", alphacode(1298), "dizo")
    print("***** Longer PIN codes ****")
    testEQ("1234567 => begomari?", alphacode(1234567), "begomari")
    testEQ("42424242 => lililili ?", alphacode(42424242), "lililili")
    testEQ("98765 => cuwira?", alphacode(98765), "cuwira")
    testEQ("987654 => zotenu?", alphacode(987654), "zotenu")
    testEQ("(same digit pairs, reverse order) 547698 => nutezo ?", alphacode(547698), "nutezo")
    print("**** Edge cases (robustness testing) ****")
    testEQ("0 => empty mnemonic ?", alphacode(0), "")
    testEQ("-42 and all negative numbers => empty mnemonic? ", alphacode(-42), "")
    testEQ("Invalid argument (float) => error? ", alphacode(0.2), error_message)
    testEQ("Larger Invalid argument (float) => error? ", alphacode(1005040.352), error_message)
    testEQ("Invalid argument (float) and negative => 0", alphacode(-3.14), "")
    print("*** End of provided test cases. ****")

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
    #run_tests()
    main()     