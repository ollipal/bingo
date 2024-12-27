from typing import List
from pydantic import BaseModel

class Translation(BaseModel):
    language: str
    text: str

class Question(BaseModel):
    translations: List[Translation]
    difficulty: str
    type: str

class Quest(BaseModel):
    name: str
    language: str
    types: List[str]

# List of 25 strings representing a bingo card
BingoCard = List[str]

class BingoData(BaseModel):
    quests: List[Quest]
    questions: List[Question]
    difficulties: List[str]