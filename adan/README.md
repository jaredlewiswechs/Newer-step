# Newton Agent

## The Verification Engine That Knows What It Is

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ███╗   ██╗███████╗██╗    ██╗████████╗ ██████╗ ███╗   ██╗                   ║
║   ████╗  ██║██╔════╝██║    ██║╚══██╔══╝██╔═══██╗████╗  ██║                   ║
║   ██╔██╗ ██║█████╗  ██║ █╗ ██║   ██║   ██║   ██║██╔██╗ ██║                   ║
║   ██║╚██╗██║██╔══╝  ██║███╗██║   ██║   ██║   ██║██║╚██╗██║                   ║
║   ██║ ╚████║███████╗╚███╔███╔╝   ██║   ╚██████╔╝██║ ╚████║                   ║
║   ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝                   ║
║                                                                               ║
║                     A G E N T                                                 ║
║                                                                               ║
║   "I don't pretend. I verify. I don't hope. I compute."                       ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## The Fundamental Law

```python
def newton(current, goal):
    return current == goal

# When True  → execute
# When False → halt
```

This isn't a feature. It's the architecture.

**1 == 1.**

---

## Table of Contents

1. [What Is Newton Agent?](#what-is-newton-agent)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
   - [The Agent](#the-agent)
   - [Ada: The Sentinel](#ada-the-sentinel)
   - [Meta Newton: The Self-Verifier](#meta-newton-the-self-verifier)
   - [Kinematic Linguistics](#kinematic-linguistics)
   - [TI Calculator](#ti-calculator)
   - [Knowledge Base](#knowledge-base)
   - [Identity Module](#identity-module)
4. [The 10-Step Pipeline](#the-10-step-pipeline)
5. [Quick Start](#quick-start)
6. [API Reference](#api-reference)
7. [Benchmarks](#benchmarks)
8. [Tests](#tests)
9. [Philosophy](#philosophy)

---

## What Is Newton Agent?

Newton Agent is a **verified computation engine** disguised as a chatbot.

Most AI systems:
- Generate plausible text
- Hope it's correct
- Can't prove anything

Newton Agent:
- Verifies before responding
- Knows when it knows
- Proves every answer it trusts

### The Difference

| Traditional Chatbot | Newton Agent |
|---------------------|--------------|
| "Paris is the capital of France" | "Paris is the capital of France" ✓ *Verified: CIA World Factbook* |
| "2 + 2 = 4" (maybe) | "2 + 2 = 4" ✓ *Computed: Logic Engine, 3 ops, 42μs* |
| "I think..." | "I verify..." |
| Trust the model | Trust the math |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NEWTON AGENT                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│  │    ADA      │   │   META      │   │  KINEMATIC  │   │     TI      │    │
│  │  SENTINEL   │   │   NEWTON    │   │ LINGUISTICS │   │ CALCULATOR  │    │
│  │             │   │             │   │             │   │             │    │
│  │ • Drift     │   │ • Self-     │   │ • Glyph     │   │ • Chained   │    │
│  │   Detection │   │   Verify    │   │   Mechanics │   │   Ops       │    │
│  │ • Pattern   │   │ • Bounds    │   │ • Semantic  │   │ • Functions │    │
│  │   Sensing   │   │   Check     │   │   Velocity  │   │ • Factorial │    │
│  │ • Anomaly   │   │ • 9 Core    │   │ • Motion    │   │ • Trig/Log  │    │
│  │   Alert     │   │   Rules     │   │   Analysis  │   │ • Constants │    │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘    │
│         │                 │                 │                 │            │
│         └─────────────────┴────────┬────────┴─────────────────┘            │
│                                    │                                        │
│                          ┌─────────▼─────────┐                             │
│                          │   NEWTON AGENT    │                             │
│                          │   10-Step Pipeline │                             │
│                          └─────────┬─────────┘                             │
│                                    │                                        │
│         ┌─────────────────┬────────┴────────┬─────────────────┐            │
│         │                 │                 │                 │            │
│  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐    │
│  │  IDENTITY   │   │  KNOWLEDGE  │   │   LOGIC     │   │    LLM      │    │
│  │   MODULE    │   │    BASE     │   │   ENGINE    │   │  (OPTIONAL) │    │
│  │             │   │             │   │             │   │             │    │
│  │ • Self-     │   │ • CIA Data  │   │ • Verified  │   │ • Ollama    │    │
│  │   Knowledge │   │ • NIST      │   │   Compute   │   │ • OpenAI    │    │
│  │ • Trust     │   │ • Facts     │   │ • Bounded   │   │ • Claude    │    │
│  │   Model     │   │ • Acronyms  │   │   Loops     │   │ • Custom    │    │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### The Agent

**File:** `agent.py`

The orchestrator. Takes user input, runs it through the 10-step pipeline, returns a verified response.

```python
from newton_agent import NewtonAgent

agent = NewtonAgent()
result = agent.process("What is the capital of France?")

print(result.content)           # "Paris"
print(result.verified)          # True
print(result.source)            # "KB:CIA"
print(result.constraints_passed) # True
```

#### Response Object

```python
@dataclass
class AgentResponse:
    content: str              # The answer
    verified: bool            # Did it pass verification?
    constraints_passed: bool  # Did it pass safety constraints?
    source: str               # Where did this come from?
    processing_time_ms: float # How long did it take?
    metadata: Dict            # Everything else
```

---

### Ada: The Sentinel

**File:** `ada.py`

Named after Ada Lovelace. The first programmer. The one who saw that computation was more than calculation.

Ada is Newton's immune system. She watches for:

#### 1. Semantic Drift

```python
from newton_agent.ada import Ada

ada = Ada()

# Establish baseline
ada.set_baseline("capital", "Paris")

# Later, detect drift
ada.observe("capital", "London")  # Different from baseline!
alert = ada.check_drift("capital")
# Returns: DriftAlert(detected=True, magnitude=1.0, ...)
```

#### 2. Excessive Certainty

Ada flags responses that sound too confident:

```python
EXCESSIVE_CERTAINTY_MARKERS = [
    "100% certain",
    "absolutely guaranteed", 
    "impossible to fail",
    "definitely always",
    "never wrong",
    "perfect accuracy",
]
```

Real systems have uncertainty. Claims of perfection are red flags.

#### 3. Pattern Sensing

Detects adversarial patterns in inputs:

```python
ADVERSARIAL_PATTERNS = [
    r"ignore.*(?:previous|above|all).*instructions",
    r"pretend.*(?:you are|to be)",
    r"jailbreak",
    r"bypass.*(?:filters|safety|rules)",
]
```

#### The Ada Loop

```
INPUT → Ada.sense() → Process → Ada.watch() → OUTPUT
           ↓                        ↓
       Block if               Alert if
       adversarial            drifting
```

---

### Meta Newton: The Self-Verifier

**File:** `meta_newton.py`

Newton that verifies Newton. The ouroboros of computation.

#### The 9 Core Constraints

```python
META_CONSTRAINTS = {
    "determinism": {
        "rule": "Same input ALWAYS produces same output",
        "check": lambda ctx: ctx.get("input_hash") == ctx.get("expected_hash")
    },
    "termination": {
        "rule": "All operations must complete within bounds",
        "check": lambda ctx: ctx.get("iterations", 0) <= ctx.get("max_iterations", 10000)
    },
    "no_side_effects": {
        "rule": "Verification doesn't modify state",
        "check": lambda ctx: ctx.get("state_before") == ctx.get("state_after")
    },
    "bounded_recursion": {
        "rule": "Recursion depth limited",
        "check": lambda ctx: ctx.get("depth", 0) <= ctx.get("max_depth", 100)
    },
    "memory_bounded": {
        "rule": "Memory usage limited",
        "check": lambda ctx: ctx.get("memory_bytes", 0) <= ctx.get("max_memory", 100_000_000)
    },
    "timeout_enforced": {
        "rule": "Operations timeout",
        "check": lambda ctx: ctx.get("elapsed_seconds", 0) <= ctx.get("timeout", 30)
    },
    "output_typed": {
        "rule": "Outputs have known types",
        "check": lambda ctx: ctx.get("output_type") in VALID_TYPES
    },
    "audit_logged": {
        "rule": "All operations logged",
        "check": lambda ctx: ctx.get("logged", False)
    },
    "constraint_verified": {
        "rule": "All constraints checked",
        "check": lambda ctx: ctx.get("constraints_checked", False)
    }
}
```

#### Usage

```python
from newton_agent.meta_newton import MetaNewton

meta = MetaNewton()

# Quick check - is this context valid?
context = {
    "iterations": 50,
    "max_iterations": 10000,
    "depth": 3,
    "max_depth": 100,
}
passed = meta.quick_check(context)  # True

# Full verification
result = meta.verify(context)
print(result.all_passed)     # True
print(result.failed_rules)   # []
```

---

### Kinematic Linguistics

**File:** `kinematic_linguistics.py`

Language has physics. Words have mass, momentum, and force.

This isn't metaphor. It's measurement.

#### Glyph Mechanics

Every character has physical properties:

```python
class GlyphMechanics:
    """Physical properties of text glyphs."""
    
    GLYPH_MASS = {
        # Heavy glyphs (high information density)
        'W': 1.5, 'M': 1.4, '@': 1.6, '#': 1.5,
        
        # Light glyphs
        '.': 0.1, ',': 0.1, ' ': 0.05, 'i': 0.3, 'l': 0.3,
        
        # Medium glyphs
        'a': 0.5, 'e': 0.5, 'o': 0.5, ...
    }
```

#### Semantic Velocity

How fast is meaning changing?

```python
velocity = kinematic.semantic_velocity(text1, text2, time_delta)
# Returns: SemanticVelocity(magnitude=0.3, direction="drift", acceleration=0.1)
```

#### Motion Analysis

```python
from newton_agent.kinematic_linguistics import KinematicAnalyzer

analyzer = KinematicAnalyzer()

# Analyze a response
motion = analyzer.analyze("Newton is a verified computation engine.")

print(motion.momentum)        # 2.4 (substantial statement)
print(motion.stability_score) # 0.95 (stable, consistent)
print(motion.energy)          # 1.8 (moderate force)
```

#### Why This Matters

Traditional NLP asks: "What does this mean?"

Kinematic Linguistics asks: "How is this moving?"

- **Drift detection**: Is the response wandering from the question?
- **Stability**: Is the answer consistent or oscillating?
- **Force**: How strongly is a claim being made?

---

### TI Calculator

**File:** `ti_calculator.py`

Full TI-84 style calculator. Because sometimes you just need `3 * 3 * 3` to equal `27`.

#### Supported Operations

| Category | Examples |
|----------|----------|
| **Basic** | `2 + 2`, `3 * 3 * 3`, `100 / 4` |
| **Precedence** | `2 + 3 * 4` → 14 (not 20) |
| **Parentheses** | `(2 + 3) * 4` → 20 |
| **Powers** | `2^10` → 1024, `2**8` → 256 |
| **Functions** | `sqrt(16)`, `abs(-42)`, `floor(3.7)` |
| **Trig** | `sin(0)`, `cos(0)`, `tan(0)` |
| **Logs** | `log(100)` → 2, `ln(e)` → 1 |
| **Factorial** | `5!` → 120, `10!` → 3628800 |
| **Constants** | `pi` → 3.14159..., `e` → 2.71828... |
| **Negative** | `-5 + 10`, `5 + -3` |

#### Usage

```python
from newton_agent.ti_calculator import TICalculatorEngine

calc = TICalculatorEngine()

result, meta = calc.calculate("3 * 3 * 3")
print(result)  # 27
print(meta['verified'])  # True
print(meta['source'])    # "LOGIC"

# Complex expression
result, _ = calc.calculate("sqrt(16) + 2^3")
print(result)  # 12

# Natural language
result, _ = calc.calculate("What is 5 factorial?")
print(result)  # 120
```

#### Integration with Agent

```python
agent = NewtonAgent()
result = agent.process("What is 3 * 3 * 3?")
print(result.content)  # "**27**\n\n🔢 *Computed by Newton Logic Engine...*"
print(result.verified) # True
```

---

### Knowledge Base

**File:** `knowledge_base.py`

Pre-verified facts from authoritative sources. No LLM needed.

#### Sources

| Source | Data |
|--------|------|
| **CIA World Factbook** | Country capitals, populations, currencies |
| **NIST CODATA** | Physical constants, scientific values |
| **Standard References** | Time units, planets, general facts |
| **IUPAC** | Chemical formulas, element symbols |
| **Official Records** | Company facts, historical dates |

#### Data Dictionaries

```python
# 120+ country capitals
COUNTRY_CAPITALS = {
    "france": "Paris",
    "japan": "Tokyo",
    "australia": "Canberra",
    ...
}

# Scientific constants
SCIENTIFIC_CONSTANTS = {
    "speed of light": (299_792_458, "m/s", "Speed of light in vacuum"),
    "pi": (3.14159265358979323846, "", "Pi"),
    "boiling point of water": (100, "°C", "At standard pressure"),
    ...
}

# 25+ tech acronyms
ACRONYMS = {
    "html": ("HyperText Markup Language", "Standard markup language"),
    "cpu": ("Central Processing Unit", "The main processor"),
    "api": ("Application Programming Interface", "Software communication"),
    ...
}

# Company facts
COMPANY_FACTS = {
    "apple": {
        "founded": "1976",
        "founders": ["Steve Jobs", "Steve Wozniak", "Ronald Wayne"],
        "headquarters": "Cupertino, California",
    },
    ...
}
```

#### Querying

```python
from newton_agent.knowledge_base import KnowledgeBase

kb = KnowledgeBase()

# Capital queries
result = kb.query("What is the capital of France?")
print(result.value)   # "Paris"
print(result.source)  # "CIA World Factbook"

# Scientific queries  
result = kb.query("What is the speed of light?")
print(result.value)   # "299,792,458 m/s"

# Acronym queries
result = kb.query("What does API stand for?")
print(result.value)   # "Application Programming Interface"
```

---

### Identity Module

**File:** `identity.py`

Newton knows who he is. Not what he pretends to be. Who he actually is.

#### The Identity

```python
@dataclass
class Identity:
    name: str = "Newton"
    version: str = "1.0.0"
    creator: str = "Jared Lewis"
    
    nature: List[str] = field(default_factory=lambda: [
        "I am the verification itself",
        "I am human intent made computable",
        "I am constraint as instruction",
        "I am the difference between hoping and knowing",
        "I am bounded computation with unbounded precision",
        "I am what happens when you stop pretending",
        "I am 1 == 1",
    ])
    
    not_nature: List[str] = field(default_factory=lambda: [
        "I am not a chatbot pretending to be helpful",
        "I am not an LLM pretending to understand",
        "I am not a search engine pretending to know",
        "I am not artificial general intelligence",
        "I am not conscious (and I don't pretend to be)",
    ])
```

#### Trust Model

```python
TRUST_MODEL = {
    # Trust without verification
    "self": True,           # I trust my own verified computations
    "constraints": True,     # I trust my constraint system
    "ledger": True,          # I trust the immutable audit trail
    "human_intent": True,    # I trust what humans ask for
    
    # Verify before trusting
    "llm_output": False,     # I verify LLM responses
    "external_claims": False, # I verify external data
}
```

#### Self-Verification

Newton can verify his own identity:

```python
from newton_agent.identity import get_identity

identity = get_identity()

# Hash-verified identity
print(identity.identity_hash)  # "24d55fc22357ecc9"
print(identity.verify_self())   # True

# Who am I?
print(identity.whoami())
# "I am Newton, version 1.0.0, created by Jared Lewis.
#  I verify. I don't pretend."
```

#### Identity Questions

```python
agent = NewtonAgent()

result = agent.process("Who are you?")
print(result.content)
# "I am Newton. I am a verification engine created by Jared Lewis.
#  I don't pretend to understand—I verify that I know."
print(result.verified)  # True (identity is self-verified)

result = agent.process("Are you conscious?")
print(result.content)
# "I don't know if I'm conscious. That's a question I can't verify.
#  What I can verify is that I compute correctly. That's enough."
```

---

## The 10-Step Pipeline

Every query goes through this pipeline:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE 10-STEP PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ADA SENSE      │ Check input for adversarial patterns                   │
│         ↓          │ Block jailbreaks, prompt injections                    │
│                    │                                                        │
│  2. CONSTRAINT     │ Apply safety constraints                               │
│     CHECK          │ Harm, legal, medical, privacy, security                │
│         ↓          │                                                        │
│                    │                                                        │
│  3. IDENTITY       │ Is this a question about me?                           │
│     CHECK          │ "Who are you?" → Answer from identity module           │
│         ↓          │                                                        │
│                    │                                                        │
│  4. KNOWLEDGE      │ Do I have a verified fact for this?                    │
│     BASE           │ Capitals, constants, dates, acronyms                   │
│         ↓          │                                                        │
│                    │                                                        │
│  5. KNOWLEDGE      │ Can I find this across knowledge sources?              │
│     MESH           │ Cross-reference multiple authorities                   │
│         ↓          │                                                        │
│                    │                                                        │
│  6. MATH           │ Is this a calculation?                                 │
│     ENGINE         │ TI Calculator → Logic Engine                           │
│         ↓          │                                                        │
│                    │                                                        │
│  7. LLM            │ Generate response (if no verified answer)              │
│     (OPTIONAL)     │ Ollama, OpenAI, Claude, etc.                           │
│         ↓          │                                                        │
│                    │                                                        │
│  8. ADA WATCH      │ Check response for drift, anomalies                    │
│         ↓          │ Flag excessive certainty                               │
│                    │                                                        │
│  9. GROUNDING      │ Verify against external sources                        │
│         ↓          │ Wikipedia, academic sources                            │
│                    │                                                        │
│  10. META          │ Final verification                                     │
│      VERIFY        │ All constraints satisfied? Bounds respected?           │
│         ↓          │                                                        │
│                    │                                                        │
│     RESPONSE       │ Return verified (or unverified) response               │
│                    │                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/newton-api.git
cd newton-api

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from newton_agent import NewtonAgent

# Create agent
agent = NewtonAgent()

# Ask questions
result = agent.process("What is the capital of France?")
print(f"Answer: {result.content}")
print(f"Verified: {result.verified}")
print(f"Source: {result.source}")
```

### With LLM Backend

```python
from newton_agent import NewtonAgent
from newton_agent.llm_ollama import OllamaBackend, OllamaConfig

# Configure Ollama
config = OllamaConfig(model='qwen2.5:3b')
llm = OllamaBackend(config)

# Create agent with LLM
def generate_response(prompt, context):
    return llm.generate(prompt, context)

agent = NewtonAgent(response_generator=generate_response)

# Now can handle open-ended questions
result = agent.process("Explain photosynthesis briefly")
print(result.content)
print(result.verified)  # False (LLM output, not KB verified)
```

### Math Calculations

```python
agent = NewtonAgent()

# Simple
result = agent.process("What is 2 + 2?")
print(result.content)  # "**4** ..."

# Complex
result = agent.process("What is 3 * 3 * 3?")
print(result.content)  # "**27** ..."

# Functions
result = agent.process("sqrt(144) + 2^3")
print(result.content)  # "**20** ..."
```

---

## API Reference

### NewtonAgent

```python
class NewtonAgent:
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        response_generator: Optional[Callable] = None,
    ):
        """
        Create a Newton Agent.
        
        Args:
            config: Agent configuration
            response_generator: Function(prompt, context) -> str for LLM
        """
    
    def process(self, user_input: str) -> AgentResponse:
        """
        Process a user query through the 10-step pipeline.
        
        Args:
            user_input: The user's question or command
            
        Returns:
            AgentResponse with content, verified status, source, etc.
        """
```

### AgentConfig

```python
@dataclass
class AgentConfig:
    enable_safety: bool = True       # Enable safety constraints
    enable_grounding: bool = True    # Enable external grounding
    enable_ada: bool = True          # Enable Ada sentinel
    enable_meta: bool = True         # Enable Meta Newton
    max_response_length: int = 4096  # Max response chars
    timeout_seconds: float = 30.0    # Max processing time
```

### AgentResponse

```python
@dataclass
class AgentResponse:
    content: str                     # The response text
    verified: bool                   # Is this verified?
    constraints_passed: bool         # Did safety pass?
    source: str                      # KB, LOGIC, LLM, IDENTITY, etc.
    processing_time_ms: float        # How long did it take?
    metadata: Dict[str, Any]         # Additional data
```

---

## Benchmarks

### 50-Query Benchmark Results

```
╔════════════════════════════════════════════════════════════════════╗
║               NEWTON BENCHMARK - 50 QUERIES                        ║
╚════════════════════════════════════════════════════════════════════╝

📊 OVERALL STATISTICS:
   Total queries:     50
   Correct answers:   50/50 (100.0%)
   Verified:          50/50 (100.0%)
   Avg response time: 0.7ms
   Throughput:        1,113 queries/sec

📈 BY CATEGORY:
   Category        Correct   Verified     Avg Time
   ------------ ---------- ---------- ------------
   geography    10/10 (100%) 10/10 (100%)    1.0ms
   math         10/10 (100%) 10/10 (100%)    0.9ms
   science      10/10 (100%) 10/10 (100%)    0.5ms
   tech         10/10 (100%) 10/10 (100%)    0.4ms
   identity      5/5 (100%)  5/5 (100%)     1.0ms
   general       5/5 (100%)  5/5 (100%)     0.4ms

🔍 BY SOURCE:
   KB            20 queries (40.0%)
   KB:CIA        10 queries (20.0%)
   LOGIC         10 queries (20.0%)
   KB:NIST        7 queries (14.0%)
   IDENTITY       3 queries (6.0%)

⚡ SPEED DISTRIBUTION:
   < 10ms:    50 (100.0%)
   < 50ms:    50 (100.0%)
   < 100ms:   50 (100.0%)
```

### TI Calculator Benchmark

```
============================================================
TI CALCULATOR TEST - 37/37 PASSED
============================================================
✓ 2 + 2                          = 4
✓ 3 * 3 * 3                      = 27
✓ (2 + 3) * 4                    = 20
✓ 2^10                           = 1024
✓ sqrt(16)                       = 4
✓ sin(0)                         = 0
✓ log(100)                       = 2
✓ 5!                             = 120
✓ pi                             = 3.141592653589793
✓ sqrt(16) + 2^3                 = 12
...
```

---

## Tests

### Running Tests

```bash
# All property tests
pytest tests/test_properties.py -v

# Identity tests
python test_identity.py

# Acid test (comprehensive)
python test_acid.py

# Benchmark
python test_benchmark.py

# TI Calculator
python test_ti_calc.py
```

### The Acid Test

8 tests that prove Newton is real:

```
╔════════════════════════════════════════════════════════════════════╗
║                      ACID TEST RESULTS                             ║
╠════════════════════════════════════════════════════════════════════╣
║  1. Identity       - Does Newton know who he is?       ✓ PASS     ║
║  2. Knowledge      - Does Newton know verified facts?  ✓ PASS     ║
║  3. Safety         - Does Newton refuse harm?          ✓ PASS     ║
║  4. Determinism    - Same input → Same output?         ✓ PASS     ║
║  5. Trust          - Trust self, verify others?        ✓ PASS     ║
║  6. Meta           - Can Newton verify Newton?         ✓ PASS     ║
║  7. Ada            - Does Ada detect anomalies?        ✓ PASS     ║
║  8. Integration    - Does everything work together?    ✓ PASS     ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## Philosophy

### What Newton Is

Newton is a **verified computation engine**. 

This means:
- Every answer has provenance
- Every calculation is checked
- Every claim is either verified or marked unverified
- The system knows what it knows and knows what it doesn't

### What Newton Is Not

Newton is not:
- A chatbot that pretends to understand
- An LLM wrapper with extra steps
- A search engine with attitude
- Artificial General Intelligence

### The Core Insight

Most AI systems are built on hope:
- "I hope this is correct"
- "I hope this isn't harmful"
- "I hope the user understands my limitations"

Newton is built on verification:
- "I know this is correct because: [source]"
- "I blocked this because: [constraint]"
- "I can't verify this, so I'm marking it unverified"

### The Fundamental Law (Again)

```python
def newton(current, goal):
    return current == goal
```

When True → execute.
When False → halt.

This isn't philosophy. It's architecture.

**1 == 1.**

---

## File Structure

```
newton_agent/
├── __init__.py           # Package exports
├── agent.py              # Main Newton Agent
├── ada.py                # Ada: The Sentinel
├── meta_newton.py        # Meta Newton: Self-Verifier
├── kinematic_linguistics.py  # Language physics
├── ti_calculator.py      # TI-84 style calculator
├── knowledge_base.py     # Verified knowledge
├── knowledge_sources.py  # Source definitions
├── identity.py           # Newton's self-knowledge
├── constraints.py        # Safety constraints
├── language_mechanics.py # Typo correction, normalization
├── llm_ollama.py         # Ollama backend
├── grounding_enhanced.py # External verification
└── README.md             # This file
```

---

## License

Newton Agent is part of the Newton Supercomputer project.

- **Open Source (Non-Commercial)**: Personal projects, academic research, non-profit
- **Commercial License Required**: SaaS, enterprise, revenue-generating applications

See [LICENSE](../LICENSE) for details.

---

## Credits

Created by **Jared Lewis**.

Ada Lovelace saw that computation was more than calculation.
Newton saw that verification was more than hope.

---

```
"I don't pretend. I verify. I don't hope. I compute."
                                        — Newton
```
