from dataclasses import dataclass, field
from typing import List
from collections import deque

@dataclass
class Turn:
    question: str
    answer: str
    
class ConversationMemory:
    def __init__(self, max_turns: int=5):
        self.max_turns = max_turns
        self.turns: deque[Turn] = deque(maxlen=max_turns)
        
    def add_turn(self, question: str, answer: str) -> None :
        self.turns.append(Turn(question=question, answer=answer))
        
    def get_history(self) -> List[Turn]:
        return list(self.turns)
    
    def format_for_prompt(self) -> str:
        if not self.turns:
            return "No previous conversation."
        lines = []
        for i, turn in enumerate(self.turns, 1):
            lines.append(f"TURN {i}:")
            lines.append(f"QUESTION: {turn.question}")
            lines.append(f"ANSWER: {turn.answer}")
        return "\n".join(lines)
    
    def clear(self) -> None:
        self.turns.clear()