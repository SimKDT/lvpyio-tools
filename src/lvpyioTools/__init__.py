import enum


class SetSuffix(enum.StrEnum):
    SET = ".set"
    EXP = ".exp"

SET_SUFFIXES: set[SetSuffix] = set(SetSuffix)