---
name: prompt-caching
description: Reference for Claude API prompt caching. Use when building applications that call the Claude API and need to optimize costs/latency with caching. Covers automatic caching, explicit breakpoints, pricing, and best practices.
source: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
---

# Prompt Caching Reference

Prompt caching optimizes API usage by allowing resuming from specific prefixes in prompts, reducing processing time and costs for repetitive tasks.

## Two Approaches

### 1. Automatic Caching (Simplest)

Add a single `cache_control` at the top level. The system auto-applies the breakpoint to the last cacheable block.

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    cache_control={"type": "ephemeral"},  # top-level
    system="Your system prompt here",
    messages=[...],
)
```

```typescript
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  cache_control: { type: "ephemeral" },  // top-level
  system: "Your system prompt here",
  messages: [...]
});
```

The cache breakpoint auto-moves forward as conversations grow. Previous content is read from cache.

### 2. Explicit Cache Breakpoints (Fine-grained)

Place `cache_control` on individual content blocks. Up to 4 breakpoints allowed.

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": "Long system prompt...",
        "cache_control": {"type": "ephemeral"}  # block-level
    }],
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Large context...", "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": "User question"}
        ]
    }],
)
```

## How It Works

1. System checks if a prompt prefix (up to a cache breakpoint) is already cached
2. If found, uses the cached version (reduced time and cost)
3. Otherwise, processes the full prompt and caches the prefix once response begins

Cache hierarchy order: `tools` → `system` → `messages`. Changes at any level invalidate that level and all subsequent levels.

## Pricing (per million tokens)

| Model | Base Input | 5m Cache Write | 1h Cache Write | Cache Read | Output |
|-------|-----------|----------------|----------------|------------|--------|
| Opus 4.6/4.5 | $5 | $6.25 | $10 | $0.50 | $25 |
| Opus 4.1/4 | $15 | $18.75 | $30 | $1.50 | $75 |
| Sonnet 4.6/4.5/4 | $3 | $3.75 | $6 | $0.30 | $15 |
| Haiku 4.5 | $1 | $1.25 | $2 | $0.10 | $5 |

Multipliers: Cache writes = 1.25x base, 1h writes = 2x base, Cache reads = 0.1x base.

## Minimum Cacheable Lengths

- **4096 tokens**: Opus 4.6, Opus 4.5, Haiku 4.5
- **2048 tokens**: Sonnet 4.6, Haiku 3.5, Haiku 3
- **1024 tokens**: Sonnet 4.5, Opus 4.1, Opus 4, Sonnet 4

Shorter prompts cannot be cached even if marked with `cache_control`.

## Cache Lifetime

- Default: **5 minutes**, refreshed each time cached content is used (no additional cost)
- Optional: **1 hour** TTL at 2x base input price

```json
{ "cache_control": { "type": "ephemeral", "ttl": "1h" } }
```

## What Can Be Cached

- Tool definitions (`tools` array)
- System messages (`system` array)
- Text messages (user and assistant turns)
- Images & Documents (user turns)
- Tool use and tool results

## What Cannot Be Cached

- Thinking blocks (cannot be marked directly, but get cached alongside other content in subsequent API calls)
- Sub-content blocks (citations) — cache the top-level block instead
- Empty text blocks

## What Invalidates the Cache

| Change | Tools | System | Messages |
|--------|-------|--------|----------|
| Tool definitions | Invalidated | Invalidated | Invalidated |
| Web search toggle | Valid | Invalidated | Invalidated |
| Citations toggle | Valid | Invalidated | Invalidated |
| Speed setting | Valid | Invalidated | Invalidated |
| Tool choice | Valid | Valid | Invalidated |
| Images | Valid | Valid | Invalidated |
| Thinking params | Valid | Valid | Invalidated |

## Tracking Cache Performance

Response `usage` fields:
- `cache_creation_input_tokens`: tokens written to cache
- `cache_read_input_tokens`: tokens read from cache
- `input_tokens`: tokens after last cache breakpoint (uncached)

Total: `cache_read + cache_creation + input_tokens`

## Best Practices

1. **Put static content first**: tools, system prompt, context — then dynamic content
2. **Cache stable content**: long system prompts, large documents, many-shot examples
3. **Use automatic caching for conversations**: simplest approach for multi-turn
4. **Use explicit breakpoints when**: sections change at different frequencies, or content exceeds 20 blocks before the final breakpoint
5. **20-block lookback window**: system only checks 20 blocks before each explicit breakpoint. Add extra breakpoints for long prompts.
6. **Concurrent requests**: cache entry only available after first response begins. Wait for first response before sending parallel requests.
7. **Order matters**: place `cache_control` after the content block, not before

## Caching with Extended Thinking

- Thinking blocks get cached alongside other content when passing tool results back
- Cached thinking blocks count as input tokens
- Non-tool-result user content causes all previous thinking blocks to be stripped from context

## Common Patterns

### Multi-turn conversation (automatic)
```python
# Just add top-level cache_control — it handles the rest
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    cache_control={"type": "ephemeral"},
    system="...",
    messages=conversation_history,
)
```

### RAG with large context
```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[{"type": "text", "text": "...", "cache_control": {"type": "ephemeral"}}],
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": large_retrieved_context, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": "User question about the context"}
        ]
    }],
)
```

### Tool use with stable definitions
```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[
        # ... many tool definitions ...
        {**last_tool, "cache_control": {"type": "ephemeral"}}  # cache all tools
    ],
    messages=[...],
)
```
