from enum import Enum


class GameType(str, Enum):
    EIGHT_BALL = "EIGHT_BALL"
    NINE_BALL = "NINE_BALL"
    TEN_BALL = "TEN_BALL"
