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
    def __init__(self, low: int, high:int):
        """
        Takes two integers to indicate
        low and high bounds of bitfield.
        """
        self.low = low
        self.high = high
        self.width = 2**(self.high + 1)
        self.mask = self.width - (2**self.low)
        #self.mask = 1 << self.low

    def insert(self, field: int, word: int):
        """
        Args: Field value (int), word (int).
        Returns: Word with the field value replacing 
        old contents of that field of the word.

        Example:
        low_4 = BitField(0, 3)
        self.assertEqual(low_4.insert(13, 0), 13)
        insert word into field
        """
        # 13 in binary is 001101
        # 21 in binary is 010101
        # 5 in binary is  000101
        # if word is   xaa00aa00 and
    #      field_val is x0000000f
    #      and the field is bits 4..7
    #      then insert gives xaa00aaf0
        # if word is 0000
        # and field_val is 1101
        # then insert gives 1101
        # if word is 000000
        # and field_val is 010101
        # and the field is bits 0..3
        # then insert gives 0101
        if field > self.width:
            return field & self.mask
        if word > self.width:
            return word^self.mask
        new_word = word | field
        return new_word & self.mask
        """
        new_word = field
        if new_word < self.width:
            new_word = field << self.low
            new_word = new_word & self.mask
        if word > self.width:
            new_word = new_word | word
            return new_word
        if word < self.width:
            return new_word & self.mask
        if new_word > self.width:
            new_word = (new_word^self.width)
            new_word = new_word & self.mask
        return new_word
        """
    def extract(self, word: int) -> int:
        """
        Args: word(int).
        Returns: value of the field.
        """
        new_word = word
        print(str(word) + ' is word')
        if new_word > self.width:
            #print(self.width)
            new_word = new_word
            print(str(new_word) + ' is new word,' + str(self.width) + ' is width')
            print(hex(new_word))
            print(hex(new_word & self.mask))
            new_word = new_word & self.mask
            # & (self.width - 1)
            return new_word
        if new_word < self.width:
            new_word = new_word >> self.low
            return new_word
        return new_word & self.mask

    def sign_extend(self, field: int, width: int) -> int:
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
    
    def extract_signed(self, word: int) -> int:
        new_word = self.sign_extend(word, self.high)
        if new_word > self.width:
            return new_word
        if new_word < self.width:
            new_word = new_word >> self.low
        return new_word
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
#

lowpart = BitField(0, 3)
midpart = BitField(4, 6)
highpart = BitField(7, 9)
packed = 0
packed = lowpart.insert(1, packed)
packed = midpart.insert(1, packed)
packed = highpart.insert(1, packed)

print(str(lowpart.extract(packed)) + ' is extract low part')
print(str(midpart.extract(packed)) + ' is extract mid part')
print(str(highpart.extract(packed)) + ' is extract high part')
