import fileinput
import logging
import sys
import time
import argparse
from copy import deepcopy
from enum import IntEnum
from functools import lru_cache
from logging import debug, info
from pathlib import Path
from time import sleep
from typing import Final


CHAR_ALIVE: str
CHAR_DEAD: str


class Cell(IntEnum):
    Dead: Final[int] = 0
    Live: Final[int] = 1

    def __str__(
        self,
    ):
        match self:
            case Cell.Dead:
                return CHAR_DEAD
            case Cell.Live:
                return CHAR_ALIVE

    def __repr__(
        self,
    ):
        return self.__str__()


# Type Aliases
Board = list[list[Cell]]
Neighbourhood = tuple[
    tuple[Cell, Cell, Cell],
    tuple[Cell, Cell, Cell],
    tuple[Cell, Cell, Cell],
]


@lru_cache(maxsize=1024)
def tmap(cells: Neighbourhood) -> Cell:
    """
    Transition map of a 3x3 Cell grid to Cell
    """
    _r0, _r1, _r2, *_ = cells
    nbrs = sum(_r0) + sum(_r1) + sum(_r2)
    match cells:
        case [_, r1, _] if r1[1] == Cell.Live and (nbrs == 3 or nbrs == 4):
            return Cell.Live
        case [_, r1, _] if r1[1] == Cell.Dead and (nbrs == 3):
            return Cell.Live
        case [[_, _, _], _, [_, _, _]]:
            return Cell.Dead
        case err:
            raise ValueError(f"Invalid state: {err}")


class Game:
    @staticmethod
    def parse_board(fpath: str | Path) -> Board:
        ret: Board = []
        ret += [
            [Cell(int(c)) for c in ln.strip() if int(c) in set(Cell)]
            for line in fileinput.input(fpath)
            if len(ln := line.strip()) > 0
        ]

        return ret

    def __init__(
        self,
    ):
        self._args = argparse.Namespace()
        cli = argparse.ArgumentParser(prog="python python-game-of-life", description="Options")
        cli.add_argument("-i", "--input", type=str, required=True)
        cli.add_argument("-d", "--delay", type=float, default=0.2, help="Delay in seconds between iterations")
        cli.add_argument("-n", "--num-steps", type=int, default=sys.maxsize, help="Number of iterations to run")
        cli.add_argument("--alive", type=str, default="🐩", help="Character to use for living cells")
        cli.add_argument("--dead", type=str, default="🐈", help="Character to use for dead cells")

        cli.parse_args(namespace=self._args)

        # [-d]
        self.delay: float = self._args.delay

        # [-n]
        self.steps: int = self._args.num_steps

        # [-i]
        self.board = Game.parse_board(self._args.input)
        self.buffer = deepcopy(self.board)

        global CHAR_ALIVE, CHAR_DEAD
        CHAR_ALIVE = self._args.alive
        CHAR_DEAD = self._args.dead

    def __str__(
        self,
    ) -> str:
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


def start(n: int = sys.maxsize, delay: float | int = 0.05):
    game: Game
    start_time = time.time()

    debug(sys.argv)

    game = Game()

    try:
        for _ in range(game.steps):
            print("\033[H\033[2J", end="")
            print(game, flush=True)
            sleep(game.delay)
            game.step()
    except KeyboardInterrupt:
        info(
            f"\nRunning time: {time.time() - start_time} seconds\n"
            f"{tmap.cache_info()}"
        )
        return

    # ...
    debug(
        f"\nRunning time: {time.time() - start_time} seconds\n" f"{tmap.cache_info()}"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start()
