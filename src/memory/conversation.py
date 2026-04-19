"""Short-term conversation memory: keeps the last N Q/A turns."""

from dataclasses import dataclass
from typing import List

from collections import deque

@dataclass
class Turn:
    """A single user/assistant exchange.

    Attributes:
        question: User question.
        answer: Assistant answer.
    """
    question: str
    answer: str
    
class ConversationMemory:
    """Bounded FIFO store of recent conversation turns.

    Args:
        max_turns: Maximum number of turns kept in memory. Older turns
                   are evicted automatically.
    """
    def __init__(self, max_turns: int=5):
        self.max_turns = max_turns
        self.turns: deque[Turn] = deque(maxlen=max_turns)
        
    def add_turn(self, question: str, answer: str) -> None :
        """Append a new turn, evicting the oldest if full.

        Args:
            question: User question.
            answer: Assistant answer.
        """
        self.turns.append(Turn(question=question, answer=answer))
        
    def get_history(self) -> List[Turn]:
        """Return all stored turns, oldest first.

        Returns:
            List copy of the internal deque.
        """
        return list(self.turns)
    
    def format_for_prompt(self) -> str:
        """Render the history as a plain-text block suitable for a prompt.

        Returns:
            Formatted history, or ``"No previous conversation."`` if empty.
        """
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