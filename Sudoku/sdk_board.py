"""
Sudoku board to hold board and tile classes
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
        row_syms = [ ]
        for row in self.tiles:
            values = [tile.value for tile in row]
            row_syms.append("".join(values))
        return "\n".join(row_syms)
    
    def is_consistent(self) -> bool:
        for group in self.groups:
            used_symbols = set()
            #print(group)
            #print('printed group')
            for tile in group:
                #print(tile)
                if str(tile) in CHOICES:
                    #print('if tile is "." we should not be here')
                    if str(tile) in used_symbols:
                        #print("Got to False")
                        #print(used_symbols)
                        return False
                    else:
                        #print('Got to add tiles' + ' ' + str(tile))
                        used_symbols.add(str(tile))
            #print(used_symbols)
        return True

    def naked_single(self) -> bool:
        """Eliminate candidates and check for sole remaining possibilities.
        Return value True means we crossed off at least one candidate.
        Return value False means we made no progress.
        """
        candidate_set_before = 0
        #print(candidate_set_before)
        for group in self.groups:
            used_values = set()
            for tile in group:
                if str(tile) in CHOICES:
                    used_values.add(tile.value)
            for tile in group:
                if str(tile) in UNKNOWN and len(used_values) > 0:
                    #print(used_values)
                    if Tile.remove_candidates(tile, used_values):
                        candidate_set_before += 1
        candidate_set_after = candidate_set_before
        #print(candidate_set_after)
        if candidate_set_after > 0:
            return True
        else:
            return False
        """
        for group in self.groups:
            used_tiles = set()
            for tile in group:
                if str(tile) in CHOICES:
                    #print(str(used_tiles) + ' ' + str(tile.candidates))
                    used_tiles.add(tile.value)
                    #print(used_tiles)
            for tile in group:
                if str(tile) in UNKNOWN and len(used_tiles) > 0:
                    #print('if {} is in {} should print progress then True'.format(used_tiles, tile.candidates))
                    #print('{} in {}'.format(used_tiles, tile.candidates))
                    #print(len(used_tiles.intersection(tile.candidates)))
                    if len(used_tiles.intersection(tile.candidates)) > 0:
                        #print("progress")
                        #print(used_tiles)
                        #print(tile.candidates)
                        return Tile.remove_candidates(tile, used_tiles)
                    else:
                        return False
        return False
        """
        """
        #used_values = set()
        for group in self.groups:
            used_values = set()
            for tile in group:
                if str(tile) in CHOICES:
                    used_values.add(tile.value)
            #print(group)
            #print(used_values)
            for tile in group:
                if len(used_values) > 0:
                    if str(tile) in UNKNOWN:
                        #print(used_values.difference(tile.candidates))
                        difference_check = tile.candidates.difference(used_values)
                        print(difference_check)
                        #print('{} difference check'.format(difference_check.difference(used_values)))
                        d2 = difference_check.difference(used_values)
                        print(d2)
                        for value in tile.candidates:
                            if value not in used_values:
                                if len(d2) > 0:
                                    #print(len(tile.candidates.difference(used_values)))
                                    if len(tile.candidates.difference(used_values)) > 0:
                                        print('{} = tile candidates'.format(tile.candidates))
                                        print('{} = used values'.format(used_values))
                                    return Tile.remove_candidates(tile, used_values)
        """
        """
        used_values = set()
        for group in self.groups:
            if len(used_values) < 6:
                for tile in group:
                    if str(tile) in CHOICES:
                        used_values.add(tile.value)
                        if str(tile) is '6':
                            print(group)
                            print("hit 6")
            else:
                for tile in group:
                    if str(tile) in UNKNOWN:
                        if len(tile.candidates) > 1:    
                            #print(tile)
                            #print(used_values)
                            print(tile.candidates)
                            print(used_values)
                            return Tile.remove_candidates(tile, used_values)
        """
        """
        used_values = set()
        for group in self.groups:
            for tile in group:
                if str(tile) in CHOICES:
                    used_values.add(tile.value)
                    if str(tile) is '6':
                        print(group)
                        print("hit 6")
        for group in self.groups:
            for tile in group:
                if str(tile) in UNKNOWN:
                    if len(tile.candidates) > 1:    
                        #print(tile)
                        #print(used_values)
                        print(tile.candidates)
                        print(used_values)
                        return Tile.remove_candidates(tile, used_values)
                    else:
                        print(tile.candidates)
                        print(used_values)
                        return False
        """
        """
        used_values = set()
        progress = True
        while progress:
            for group in self.groups:
                #Tile.used_values = set()
                for value in group:
                    if str(value) in CHOICES:
                        #print(value.candidates)
                        if value.value in value.candidates:
                            #print("value.value in value.candidates")
                            used_values.add(value.value)
                        #print(used_values)

                        #print("progress 1")
                        #print("progress 2")
                        #print(value)
                        #print(used_values)
                for symbol in used_values:
                    print("progress 3")
                    progress = Tile.remove_candidates(value, symbol)
                    print(progress)
                    return progress
            progress = False
                #print(tile.value)
        """

        """
        for group in self.groups:
            candidates_single = set()
            #print(group)
            for tile in group:
                #print(tile)
                if str(tile) in CHOICES:
                    #print(str(tile))
                    if str(tile) in candidates_single:
                        #print(str(tile))
                        x = Tile.remove_candidates(str(tile), candidates_single)
                        print(x)
                        return True
                    else: 
                        candidates_single.add(tile)
                        #print(candidates_single)
            for tile in candidates_single:
                if tile in candidates_single:
                    print(tile)
                    return Tile.remove_candidates(tile, candidates_single)
                else:
                    return False
            """
        """
        candidates_single = set()
        for group in self.groups:
            #print(group)
            for tile in group:
                if str(tile) in CHOICES:
                    candidates_single.add(tile)
            for tile in group:
                if tile in candidates_single:    
                    #print('removed candidates ' + str(tile))
                    #print(tile)
                    print(tile)
                    print(candidates_single)
                    print(Tile.remove_candidates(tile, candidates_single))
        return False
        """
        """
        candidates_1 = set()
        for row in range(len(self.groups)):
            for col in range(len(self.groups[row])):
                candidates_1.add(self.groups[row][col])
                if str(self.groups[row][col]) in CHOICES:
                    print(self.groups[row][col])
                    print("got to tile.remove")
                    print(Tile.remove_candidates(self.groups[row][col], candidates_1))
        """
        """
        used_candidates = set()
        candidates_active = set(CHOICES)
        for group in self.groups:
            
            #print(candidates_active)
            for tile in group:
                if str(tile) in CHOICES:
                    used_candidates.add(tile)
        #print(candidates_active)
        #print(used_candidates)
        for group in self.groups:
            #print(used_candidates)
            for value in group:
                if str(value) in CHOICES:
                    print(value)
                    #print(used_candidates)
                    print('removed ' + str(value))
                    Tile.remove_candidates(value, candidates_active)
                    if value not in candidates_active:
                        used_candidates.remove(value)
                        print(used_candidates)
                    return True
                    #print(value.value)
                    #print(candidates_active)
            if value.value in candidates_active:
                candidates_active.remove(value.value)
                #print(candidates_active)
            #print(candidates_active)
            if len(candidates_active) == 1:
                return Tile.remove_candidates(value, candidates_active)
        return True
        """
        
    def solve(self):
        progress = True
        while progress:
            progress = self.naked_single()
        return

board = Board()
board.set_tiles([".........", "......1..", "......7..",
                         "......29.", "........4", ".83......",
                         "......5..", ".........", "........."])
print(board.naked_single())
print(board.naked_single())
print(board.naked_single())
board.solve()