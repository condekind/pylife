import fileinput
import logging
import sys
from copy import deepcopy
from enum import IntEnum
from functools import lru_cache
from logging import debug, info
from pathlib import Path
from time import sleep
from typing import Any, Final, TypeAlias


class Cell(IntEnum):
    Dead: Final[int] = 0
    Live: Final[int] = 1

    def __str__(
        self,
    ):
        match self:
            case Cell.Dead:
                return "░"
            case Cell.Live:
                return "█"

    def __repr__(
        self,
    ):
        return self.__str__()


Cell.Values = {member.value for member in Cell}
Board: TypeAlias = list[list[Cell]]
Neighbourhood: TypeAlias = tuple[tuple[Cell, 3], 3]


@lru_cache(maxsize=1024)
def tmap(cells: Neighbourhood) -> Cell:
    """
    Transition map of a 3x3 Cell grid to Cell
    """
    _r0, _r1, _r2, *_ = cells
    nbrs = sum(_r0) + sum(_r1) + sum(_r2)
    match cells:
        case [r0, r1, r2] if r1[1] == Cell.Live and (nbrs == 3 or nbrs == 4):
            return Cell.Live
        case [r0, r1, r2] if r1[1] == Cell.Dead and (nbrs == 3):
            return Cell.Live
        case [[_, _, _], r1, [_, _, _]]:
            return Cell.Dead
        case err:
            raise ValueError(f"Invalid state: {err}")


class Game:
    @staticmethod
    def parse_board(fpath: str | Path) -> Board:
        ret: Board = []
        ret += [
            [Cell(int(c)) for c in ln.strip() if int(c) in Cell.Values]
            for line in fileinput.input(fpath)
            if len(ln := line.strip()) > 0
        ]

        return ret

    def __init__(
        self,
        **kwargs: dict[str, Any],
    ):
        match kwargs:
            case {"board": b, **rest} if b is not None:
                self.board = Game.parse_board(b)
                self.rows = len(b)
                self.cols = len(b[0]) if b[0] else 0
            case {"rows": r, "cols": c, **rest}:
                self.rows = rows
                self.cols = cols
                self.board = [[Cell.Dead for c in range(cols)] for r in range(rows)]
            case rest:
                raise ValueError(f"Invalid Game __init__() args: {kwargs.items()}")
        self.buffer = deepcopy(self.board)

    def __str__(
        self,
    ):
        ret = ""
        for r in self.board:
            for c in r:
                ret += str(c)
            ret += "\n"
        return str(ret)

    def step(self, n: int = 1):
        for _ in range(n):
            for rdx, r in list(enumerate(self.board))[1:-1]:
                for cdx, c in list(enumerate(r))[1:-1]:
                    self.buffer[rdx][cdx] = tmap(
                        (
                            (
                                self.board[rdx - 1][cdx - 1],
                                self.board[rdx - 1][cdx],
                                self.board[rdx - 1][cdx + 1],
                            ),
                            (
                                self.board[rdx][cdx - 1],
                                self.board[rdx][cdx],
                                self.board[rdx][cdx + 1],
                            ),
                            (
                                self.board[rdx + 1][cdx - 1],
                                self.board[rdx + 1][cdx],
                                self.board[rdx + 1][cdx + 1],
                            ),
                        )
                    )
            # Swap board <-> buffer
            self.board, self.buffer = self.buffer, self.board


def start(n: int = sys.maxsize, delay: float | int = 0.02):
    game: Game

    debug(sys.argv)

    match len(sys.argv):
        case 3:
            game = Game(sys.argv[1], sys.argv[2])
        case 2:
            game = Game(board=sys.argv[1])
        case _:
            game = Game()

    try:
        for _ in range(n):
            print("\033[H\033[2J", end="")
            print(game, flush=True)
            sleep(delay)
            game.step()
    except KeyboardInterrupt:
        print(tmap.cache_info())

    info(tmap.cache_info())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start()
