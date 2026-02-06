#!/usr/bin/env python3
"""Test semantic search integration."""
from newton_agent.knowledge_base import KnowledgeBase

kb = KnowledgeBase()

# Test queries - mix of keyword and semantic
tests = [
    # Keyword matches (fast)
    ('What is the capital of France?', 'keyword'),
    ('What does DNA stand for?', 'keyword'),
    
    # Semantic matches (would miss with keywords only)
    ('What city does France govern from?', 'semantic'),
    ('Tell me about the cells energy factory', 'semantic'),
    ('Who invented Python?', 'semantic'),
    ('Explain the genetic molecule', 'semantic'),
]

print('=' * 70)
print('NEWTON KNOWLEDGE BASE - SEMANTIC SEARCH TEST')
print('=' * 70)

for question, expected_type in tests:
    print(f'\nQ: {question}')
    result = kb.query(question)
    if result:
        conf = f'[{result.confidence:.2f}]' if result.confidence < 1.0 else '[1.00]'
        fact_short = result.fact[:70] + '...' if len(result.fact) > 70 else result.fact
        print(f'A: {conf} {fact_short}')
        print(f'   Type: {result.category} | Expected: {expected_type}')
    else:
        print(f'A: No match found')
        print(f'   Expected: {expected_type}')

print('\n' + '=' * 70)
print('STATS')
print('=' * 70)
stats = kb.get_stats()
print(f"Queries: {stats['queries']}")
print(f"Hits: {stats['hits']} (keyword: {stats['keyword_hits']}, semantic: {stats['semantic_hits']})")
emb_stats = stats.get('embedding_stats', {})
print(f"Embeddings indexed: {emb_stats.get('indexed_facts', 0)}")
