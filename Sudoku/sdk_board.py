"""
Sudoku board to hold board and tile classes.
Author: Alexander Angel
Authored: is_consistent, naked_single, hidden_single, min_choice_tile, is_complete, solve methods.
Credits: Nathan Malamud for helping me understand how to iterate through a matrix properly.
Date: 5/20/2019
Time: 23:09:09
"""

from sdk_config import CHOICES, UNKNOWN, ROOT
from sdk_config import NROWS, NCOLS
from typing import Sequence, List, Set
import enum

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Event(object):
    """Abstract base class of all events, both for MVC
    and for other purposes.
    """
    pass

class Listener(object):
    """Abstract base class for listeners.
    Subclass this to make the notification do
    something useful.
    """

    def __init__(self):
        """Default constructor for simple listeners without state"""
        pass

    def notify(self, event: Event):
        """The 'notify' method of the base class must be
        overridden in concrete classes.
        """
        raise NotImplementedError("You must override Listener.notify")
    
class EventKind(enum.Enum):
    TileChanged = 1
    TileGuessed = 2

class TileEvent(Event):
    """Abstract base class for things that happen
    to tiles. We always indicate the tile.  Concrete
    subclasses indicate the nature of the event.
    """

    def __init__(self, tile: 'Tile', kind: EventKind):
        self.tile = tile
        self.kind = kind
        # Note 'Tile' type is a forward reference;
        # Tile class is defined below

    def __str__(self):
        """Printed representation includes name of concrete subclass"""
        return f"{repr(self.tile)}"

class TileListener(Listener):
    def notify(self, event: TileEvent):
        raise NotImplementedError(
            "TileListener subclass needs to override notify(TileEvent)")

class Listenable:
    """Objects to which listeners (like a view component) can be attached"""

    def __init__(self):
        self.listeners = [ ]

    def add_listener(self, listener: Listener):
        self.listeners.append(listener)

    def notify_all(self, event: Event):
        for listener in self.listeners:
            listener.notify(event)

class Tile(Listenable):
    """One tile on the Sudoku grid.
    Public attributes (read-only): value, which will be either
    UNKNOWN or an element of CHOICES; candidates, which will
    be a set drawn from CHOICES.  If value is an element of
    CHOICES,then candidates will be the singleton containing
    value.  If candidates is empty, then no tile value can
    be consistent with other tile values in the grid.
    value is a public read-only attribute; change it
    only through the access method set_value or indirectly 
    through method remove_candidates.   
    """
    def __init__(self, row: int, col: int, value=UNKNOWN):
        super().__init__()
        assert value == UNKNOWN or value in CHOICES
        self.row = row
        self.col = col
        self.set_value(value)

    def set_value(self, value: str):
        if value in CHOICES:
            self.value = value
            self.candidates = {value}
        else:
            self.value = UNKNOWN
            self.candidates = set(CHOICES)
        self.notify_all(TileEvent(self, EventKind.TileChanged))

    def __repr__(self) -> str:
        return "Tile({}, {}, '{}')".format(self.row,self.col, self.value)

    def __str__(self) -> str:
        return '{}'.format((self.value))

    def could_be(self, value: str) -> bool:
        """True iff value is a candidate value for this tile"""
        return value in self.candidates

    def remove_candidates(self, used_values: Set[str]):
        """
        The used values cannot be a value of this unknown tile.
        We remove those possibilities from the list of candidates.
        If there is exactly one candidate left, we set the
        value of the tile.
        Returns:  True means we eliminated at least one candidate,
        False means nothing changed (none of the 'used_values' was
        in our candidates set).
        """
        new_candidates = self.candidates.difference(used_values)
        if new_candidates == self.candidates:
            # Didn't remove any candidates
            return False
        self.candidates = new_candidates
        if len(self.candidates) == 1:
            self.set_value(new_candidates.pop())
        self.notify_all(TileEvent(self, EventKind.TileChanged))
        return True

class Board(object):
    """A board has a matrix of tiles"""

    def __init__(self):
        """The empty board"""
        self.groups: List[List[[Tile]]] = [ ]
        # Row/Column structure: Each row contains columns
        self.tiles: List[List[Tile]] = [ ]
        for row in range(NROWS):
            cols = [ ]
            for col in range(NCOLS):
                cols.append(Tile(row, col))
            self.tiles.append(cols)  
        for block_row in range(ROOT):
            for block_col in range(ROOT):
                group = [ ] 
                for row in range(ROOT):
                    for col in range(ROOT):
                        row_addr = (ROOT * block_row) + row
                        col_addr = (ROOT * block_col) + col
                        group.append(self.tiles[row_addr][col_addr])
                self.groups.append(group)
        for row in self.tiles: 
            self.groups.append(row)
        for row in range(len(self.tiles)):
            columns = [ ]
            for col in range(NCOLS):
                columns.append(self.tiles[col][row])
            self.groups.append(columns)

    def set_tiles(self, tile_values: Sequence[Sequence[str]] ):
        """Set the tile values a list of lists or a list of strings"""
        for row_num in range(NROWS):
            for col_num in range(NCOLS):
                tile = self.tiles[row_num][col_num]
                tile.set_value(tile_values[row_num][col_num])

    def __str__(self) -> str:
        """In Sadman Sudoku format"""
        return "\n".join(self.as_list())


    def as_list(self) -> List[str]:
        """Tile values in a format compatible with 
        set_tiles.
        """
        row_syms = [ ]
        for row in self.tiles:
            values = [tile.value for tile in row]
            row_syms.append("".join(values))
        return row_syms
    
    def is_consistent(self) -> bool:
        """
        Checks group by group (i.e. rows, columns, blocks) and checks for duplicate values.
        Return value True if no duplicates are found on board.
        Return value False if duplicate is found on board.
        """
        for group in self.groups:
            used_symbols = set()
            for tile in group:
                if tile.value in CHOICES:
                    if tile.value in used_symbols: # If tile.value is more than once to used_symbols
                        return False
                    else:
                        used_symbols.add(tile.value)
        return True

    def naked_single(self) -> bool:
        """Eliminate candidates and check for sole remaining possibilities.
        Return value True means we crossed off at least one candidate.
        Return value False means we made no progress.
        """
        candidate_set_before = 0 # No changes to candidate set, progress is False
        for group in self.groups:
            used_values = set()
            for tile in group: # Adds the currently used values within the group to a set
                if tile.value in CHOICES:
                    used_values.add(tile.value)
            for tile in group: # Loops through tiles and remove a candidate if that candidate is already a value placed on the board
                if tile.value in UNKNOWN and len(used_values) > 0:
                    if Tile.remove_candidates(tile, used_values): # Removes values from candidates so there are no duplicates in the group
                        candidate_set_before += 1 # Change to candidate set, progress is True
        candidate_set_after = candidate_set_before
        if candidate_set_after > 0: # If at least one change was made to a tile's value, return value is True
            return True
        else:
            return False # If no changes were made to any tiles, return value is False
        
    def hidden_single(self) -> bool:
        """
        Suppose we have eliminated all but two candidates from all our unknown tiles. If one of the 
        unknown tiles has a value of 3 and no other unknown tiles have that value of 3, then
        the tile with a candidate of 3 must have the value of 3 because there is no other place
        to put it (i.e. no other tile has a candidate of 3 because 3 was elimated from their candidates).

        Return value True if a value was placed on a tile (marking we *made* progress).
        Return value False if no value was placed on a tile (marking we *did not make* progress).
        """
        tile_to_change = None # Stores the tile with a sole candidate within the group
        for group in self.groups:
            set_tile = 0 # No changes were made to any tile values
            leftovers = set(CHOICES)
            for tile in group: # Loops through tile values already placed in group and removes them from possibilities
                if tile.value in CHOICES:
                    if tile.value in leftovers:
                        leftovers.remove(tile.value)
            for value in leftovers: # Loops through values that can be placed and counts how many times that value is in a candidate set
                count = 0
                for tile in group:
                    if value in tile.candidates:
                        count += 1
                        tile_to_change = tile
                if count < 2 and count > 0:
                    tile_to_change.set_value(value)
                    tile_to_change.notify_all(TileEvent(tile_to_change, EventKind.TileChanged))
                    set_tile += 1 # A change was made to a tile value
        if set_tile > 0: # If a change was made to at least one tile value, return value True
            return True
        else:
            return False
        
    def min_choice_tile(self) -> Tile: 
        """Returns a tile with value UNKNOWN and 
        minimum number of candidates. 
        Precondition: There is at least one tile 
        with value UNKNOWN. 
        """
        unknowns_in_board = False # Pre-condition: must contain unknown ('.') values
        min_candidates_tile = 8 # Start at max amount of candidates -> 0 to 8 possible candidates
        min_tile = Tile # Stores the tile with the minimum amount of candidates 
        for group in self.groups:
            for tile in group: # Confirms pre-condition is met
                if tile.value in UNKNOWN:
                    unknowns_in_board = True
                    if len(tile.candidates) < min_candidates_tile:
                        # Iterate through tiles in each group
                        # and change min_tile if corresponding tile 
                        # has less candidates than the currently stored tile
                        min_tile = tile
                        min_candidates_tile = len(tile.candidates)
        if unknowns_in_board: # Must finish looping through all tiles, return value is Tile with unknown value '.'
            return min_tile

    def is_complete(self) -> bool:
        """None of the tiles are UNKNOWN.  
        Note: Does not check consistency; do that 
        separately with is_consistent.
        """
        for group in self.groups:
            for tile in group:
                if tile.value in UNKNOWN:
                    return False
        return True
            
    def solve(self):
        """General solver; guess-and-check 
        combined with constraint propagation.
        """
        self.propagate()
        if self.is_complete():
            return True
        elif not self.is_consistent():
            return False
        else:
            saved_board = self.as_list()
            guess_tile = self.min_choice_tile()
            candidates = guess_tile.candidates
            for value in candidates:
                guess_tile.set_value(value)
                if self.solve():
                    return True
                else:
                    self.set_tiles(saved_board)
            return False
        
    def propagate(self):
        """Repeat solution tactics until we
        don't make any progress, whether or not
        the board is solved.
        """
        progress = True
        while progress:
            progress = self.naked_single()
            self.hidden_single()
        return

