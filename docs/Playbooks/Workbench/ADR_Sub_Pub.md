# Sub-Pub (Module Communication)

## Context and Intent
This system defines how modules within JARVIS communicate state and events.

It currently combines:
- A state store (latest values per topic)
- A publish/subscribe system (event propagation)

These responsibilities should be clearly defined to avoid ambiguity and scaling issues.

### Goals:
- Loose coupling: Modules should not depend on each other directly
- Non-blocking communication: Publishing must not be delayed by subscribers
- Clear data model: Distinguish between state and events
- Namespaced architecture: Hierarchical topic structure (including "trie")
- Extensibility: New modules should integrate without modifying existing ones

### Secondary Robust Goals:
- Fault isolation (subscriber failures do not cascade)
- Observability (debuggable flow of data/events)
- Controlled data lifecycle (avoid unbounded growth)
- Networked communication between machines (future)

### Non-Goals:
- Distributed messaging (e.g., Kafka, Redis streams)
- Persistent event storage

## The Problem (Current State)

### Frictions
**Description**<br>
Bus is passed to each module at creation. There is one variable that is required for any communication per bus. All data should be accessible in JARVIS within clearance levels.

**Talking points:**
- A central DataBus stores all topic data in a single dictionary
- Subscribers are registered per topic
- Bus is passed into modules during initialization
- publish():
  - Updates stored value
  - Iterates through subscribers synchronously

### Limitations
All data is passed through one variable. This could prove trivial as data size grows and demand increases.
- Single shared structure for all communication
- No prioritization, batching, or backpressure handling
- No concurrency model beyond a single lock

### Scalability
**Blocking Subscriber Execution:**
Subscribers execute sequentially on the publisher’s thread
- One slow subscriber delays all others
- Real-time responsiveness degrades
- Severity: High

**Mixed Responsibilities (State vs Events):**
What happens: `_data` acts as both: Latest state store and event trigger mechanism.
- Unclear semantics (is publish overwriting state or emitting an event?)
- Harder to evolve system cleanly
- Severity: High



**Tight Coupling via Bus Injection:**
Bus is passed into each module manually.
- Boilerplate and friction during module creation
- Hidden dependency patterns
- Severity: Medium

**Data:** All data persists in a single dictionary indefinitely

Impact:
- Memory growth over time
- No lifecycle or expiration policy
- Severity: Medium (context-dependent)

## Solution(s)
`asyncio`

`NATS io`

### Goals

### Additions
Prefix tree (trie) for special lookups. *Examples:*

- "[camera].frame" retrieves all available most current camera frames
- "[Servo].pos" gives all servo positions
- "*camera" gives all data published by that device

Devices should be found with some form of ID and not a specific name. That would require managing unique names per device.

### Trade-offs (Compare)
**Pros:**

**Cons:**

## Implementation Blueprint
- Research options and learn some standard protocals
- Create basic async implementation
- Add this method of communication to existing modules
- Test and improve system for ease of use
- Eliminate old (current) method of communication

### Key Logic

### Code Snippets / Pseudo-code (AI)

``` python
import asyncio
from collections import defaultdict
import logging

class AsyncDataBus:
    def __init__(self):
        self._data = {}
        self._subscribers = defaultdict(set)
        # Use an asyncio.Lock if modifying shared state across tasks
        self._lock = asyncio.Lock()

    async def publish(self, topic: str, value):
        """Dispatches data to all async queues subscribed to the topic."""
        async with self._lock:
            self._data[topic] = value
            # Get a snapshot of subscribers to avoid issues if they change during iteration
            queues = list(self._subscribers[topic])
        
        for queue in queues:
            await queue.put(value)

    def subscribe(self, topic: str):
        """Returns an async generator so the subscriber can 'loop' over messages."""
        queue = asyncio.Queue()
        self._subscribers[topic].add(queue)
        
        # We use a generator to make usage very clean for the 'Skill' modules
        async def message_generator():
            try:
                while True:
                    yield await queue.get()
            finally:
                # Cleanup if the subscriber stops listening
                self._subscribers[topic].discard(queue)
        
        return message_generator()

    async def get(self, topic, default=None):
        async with self._lock:
            return self._data.get(topic, default)
```

## Open Questions
How much rigor does this need at the current state?

How can this be made so that modification and additions can be made, but the implemented side remains the same?

What budget of time do I give this?

Is basic enough, or is a proper foundation required at this point?