#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
AGENT MEMORY - CONVERSATION & CONTEXT MANAGEMENT
Hash-chained conversation history with Newton Ledger integration.
═══════════════════════════════════════════════════════════════════════════════
"""

import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class TurnRole(Enum):
    """Conversation turn roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class GroundingInfo:
    """Grounding information for a claim."""
    claim: str
    score: float
    status: str
    sources: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "claim": self.claim,
            "score": self.score,
            "status": self.status,
            "sources": self.sources[:3],
        }


@dataclass
class ConstraintCheck:
    """Result of a constraint check."""
    constraint: str
    passed: bool
    details: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "constraint": self.constraint,
            "passed": self.passed,
            "details": self.details,
        }


@dataclass
class ConversationTurn:
    """A single turn in the conversation with full provenance."""
    id: str
    role: TurnRole
    content: str
    timestamp: int
    prev_hash: str
    hash: str
    
    # Verification metadata
    constraints_checked: List[ConstraintCheck] = field(default_factory=list)
    grounding_results: List[GroundingInfo] = field(default_factory=list)
    verified: bool = True
    
    # Action metadata
    action_taken: Optional[str] = None
    action_result: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "verified": self.verified,
            "constraints": [c.to_dict() for c in self.constraints_checked],
            "grounding": [g.to_dict() for g in self.grounding_results],
            "action": self.action_taken,
        }


class AgentMemory:
    """
    Hash-chained conversation memory.
    
    Every turn is:
    - Timestamped
    - Hash-chained to previous turn
    - Includes verification metadata
    - Exportable for audit
    """
    
    def __init__(self, max_turns: int = 100):
        self.turns: List[ConversationTurn] = []
        self.max_turns = max_turns
        self.conversation_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
    def _compute_hash(self, content: str, prev_hash: str, timestamp: int) -> str:
        """Compute hash for a turn."""
        payload = f"{content}:{prev_hash}:{timestamp}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]
    
    def add_turn(
        self,
        role: TurnRole,
        content: str,
        constraints: List[ConstraintCheck] = None,
        grounding: List[GroundingInfo] = None,
        action: str = None,
        action_result: Dict = None,
        verified: bool = True,
    ) -> ConversationTurn:
        """Add a turn to the conversation."""
        timestamp = int(time.time())
        prev_hash = self.turns[-1].hash if self.turns else "GENESIS"
        
        turn = ConversationTurn(
            id=f"{self.conversation_id}-{len(self.turns)}",
            role=role,
            content=content,
            timestamp=timestamp,
            prev_hash=prev_hash,
            hash=self._compute_hash(content, prev_hash, timestamp),
            constraints_checked=constraints or [],
            grounding_results=grounding or [],
            verified=verified,
            action_taken=action,
            action_result=action_result,
        )
        
        self.turns.append(turn)
        
        # Enforce max turns (FIFO, but keep system messages)
        if len(self.turns) > self.max_turns:
            # Remove oldest non-system turn
            for i, t in enumerate(self.turns):
                if t.role != TurnRole.SYSTEM:
                    self.turns.pop(i)
                    break
        
        return turn
    
    def get_context(self, max_turns: int = 10) -> List[Dict]:
        """Get recent conversation context for the agent."""
        recent = self.turns[-max_turns:]
        return [
            {"role": t.role.value, "content": t.content}
            for t in recent
        ]
    
    def get_full_history(self) -> List[Dict]:
        """Get full conversation history with all metadata."""
        return [t.to_dict() for t in self.turns]
    
    def verify_chain(self) -> bool:
        """Verify the hash chain integrity."""
        if not self.turns:
            return True
        
        # Check first turn
        if self.turns[0].prev_hash != "GENESIS":
            return False
        
        # Check chain
        for i in range(1, len(self.turns)):
            expected_prev = self.turns[i - 1].hash
            if self.turns[i].prev_hash != expected_prev:
                return False
            
            # Verify hash computation
            computed = self._compute_hash(
                self.turns[i].content,
                self.turns[i].prev_hash,
                self.turns[i].timestamp
            )
            if self.turns[i].hash != computed:
                return False
        
        return True
    
    def export_audit_trail(self) -> Dict:
        """Export full audit trail for verification."""
        return {
            "conversation_id": self.conversation_id,
            "total_turns": len(self.turns),
            "chain_valid": self.verify_chain(),
            "turns": self.get_full_history(),
            "exported_at": int(time.time()),
        }
    
    def clear(self):
        """Clear conversation history."""
        self.turns = []
        self.conversation_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
