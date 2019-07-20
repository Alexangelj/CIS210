"""
A bit field is a range of binary digits within an
unsigned integer. Bit 0 is the low-order bit,
with value 1 = 2^0. Bit 31 is the high-order bit,
with value 2^31. 

A bitfield object is an aid to encoding and decoding 
instructions by packing and unpacking parts of the 
instruction in different fields within individual 
instruction words. 

Note that we are treating Python integers as if they 
were 32-bit unsigned integers.  They aren't ... Python 
actually uses a variable length signed integer
representation, but we ignore that because we are trying
to simulate a machine-level representation. 
"""

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

WORD_SIZE = 32 


class BitField(object):
    """A BitField object handles insertion and 
    extraction of one field within an integer.
    """
    def __init__(self, from_bit, to_bit):
        self.from_bit = from_bit
        self.to_bit = to_bit
        self.width = 2**(self.to_bit + 1)
        self.mask = self.width -(2**from_bit)

    def insert(self, field: int, word:int):
        """
        Input a field value and a word.
        Returns the word, with the field value replacing the old contents of that
        of the word. 
        Uses AND over the word width.
        13 in binary is 1101. Insert at Bitfield(0,3) should return 1101. Field is 1101, word is 0.
        
        Test 1
        Passing in Bitfield(0,3), 1101, 0, expected to return 1101. 
        Which is 0 & 1101.
        
        Test 2
        # A value that doesn't fit; some high bits lost
        self.assertEqual(low_4.insert(21, 0), 5)
        Passing in Bitfield(0,3), 10101, 0, expected to return 0101. 
        The first bit gets masked out because it is outside the width of the bitfield object.
        if 21 > 16, return field & mask?
        Input 1 0101 = 21
        Oprtn   
        Outpt 0 0101 = 5

        Test 3
        mid_4 = BitField(4, 7)
        # A value that fits snugly in4 bits
        self.assertEqual(mid_4.insert(13, 0), 13 << 4)
        Passing in Bitfield(4,7), 1101, 1101 0000, output should be 1101 0000 = 208
        4 is also 0100 which is the from_bit.
        return 1101 << from_bit

        Test 4
        # A value that doesn't fit; some high bits lost
        self.assertEqual(mid_4.insert(21, 0), 5 << 4)
        Passing in Bitfield(4,7), 10101, 0000, should return 1010 0000, inserting 1 0101 into 0000 0000
        1 0101 0000 within 4,7 is 

        Test 5
        # Doesn't clobber other bits
        higher = 15 << 4
        self.assertEqual(low_4.insert(13, higher), 13 + higher)
        Passing in Bitfield(0,3), 1101, 1111 0000, returns 1111 1101
        Basically, inserts 1101 in to 1111 0000. So 0000 1101 | 1111 0000 = field | word
        """
        return field << self.from_bit & self.mask | word
    def extract(self, word: int):
        """
        Takes a word and returns value of field (i.e. bits in bitfield)
        
        Test 1
        # Extract unsigned
        self.assertEqual(low_4.extract(15), 15)
        Passing through Bitfield(0,3), 1111, return 1111.

        Test 2
        # Extract unsigned
        self.assertEqual(mid_4.extract(15 << 4), 15)
        Passing through Bitfield(4,7), 1111 0000, should return 1111
        """
        return word >> self.from_bit & self.mask
    
    def extract_signed(self, word: int):
        """
        Exact same as extract, but if sign bit of the field is 1, it forms the negative.

        Test 1
        self.assertEqual(low_4.extract_signed(15), -1)
        # Doesn't clobber other bits
        Passing in Bitfield(0,3), 1111, return -1
        """
        return sign_extend(word, self.to_bit) >> self.from_bit
    # FIXME:
    #    The constructor should take two integers, from_bit and to_bit,
    #    indicating the bounds of the field.  Unlike a Python range, these
    #    are inclusive, e.g., if from_bit=0 and to_bit = 4, then it is a
    #    5 bit field with bits numbered 0, 1, 2, 3, 4.
    #
    #    You might want to precompute some additional values in the constructor
    #    rather than recomputing them each time you insert or extract a value.
    #    I precomputed the field width (used in several places), a mask (for
    #    extracting the bits of interest), the inverse of the mask (for clearing
    #    a field before I insert a new value into it), and a couple of other values
    #    that could be useful to have in sign extension (see the sign_extend
    #    function below).
    #
    #    method insert takes a field value (an int) and a word (an int)
    #    and returns the word with the field value replacing the old contents
    #    of that field of the word.
    #    For example,
    #      if word is   xaa00aa00 and
    #      field_val is x0000000f
    #      and the field is bits 4..7
    #      then insert gives xaa00aaf0
    #
    #   method extract takes a word and returns the value of the field
    #   (which was set in the constructor)
    #
    #   method extract_signed does the same as extract, but then if the
    #   sign bit of the field is 1, it sign-extends the value to form the
    #   appropriate negative integer.  extract_signed could call the function
    #   extract_signed below, but you may prefer to incorporate that logic into
    #   the extract_signed method.


# Sign extension is a little bit wacky in Python, because Python
# doesn't really use 32-bit integers ... rather it uses a special
# variable-length bit-string format, which makes *most* logical
# operations work in the extpected way  *most* of the time, but
# with some differences that show up especially for negative
# numbers.  I've written this sign extension function for you so
# that you don't have to spend time plotting a way to make it work.
# You'll probably want to convert it to a method in the BitField
# class.
#
# Examples:
#    Suppose we have a 3 bit field, and the field
#    value is 0b111 (7 decimal).  Since the high
#    bit is 1, we should interpret it as
#    -2^2 + 2^1  + 2^0, or -4 + 3 = -1
#
#    Suppose we hve the same value, decimal 7 or
#    0b0111, but now it's in a 4 bit field.  In thata
#    case we should interpret it as 2^2 + 2^1 + 2^0,
#    or 4 + 2 + 1 = 7, a positive number.
#
#    Sign extension distinguishes these cases by checking
#    the "sign bit", the highest bit in the field.

def sign_extend(field: int, width: int) -> int:
    """Interpret field as a signed integer with width bits.
    If the sign bit is zero, it is positive.  If the sign bit
    is negative, the result is sign-extended to be a negative
    integer in Python.
    width must be 2 or greater. field must fit in width bits.
    """
    log.debug("Sign extending {} ({}) in field of {} bits".format(field, bin(field), width))
    assert width > 1
    assert field >= 0 and field < 1 << (width + 1)
    sign_bit = 1 << (width - 1) # will have form 1000... for width of field
    mask = sign_bit - 1         # will have form 0111... for width of field
    if (field & sign_bit):
        # It's negative; sign extend it
        log.debug("Complementing by subtracting 2^{}={}".format(width-1,sign_bit))
        extended = (field & mask) - sign_bit
        log.debug("Should return {} ({})".format(extended, bin(extended)))
        return extended
    else:
        return field