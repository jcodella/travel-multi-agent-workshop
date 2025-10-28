# Multi-Agent Travel Assistant Workshop

## Microsoft Ignite 2025

---

## Overview

This hands-on workshop walks you through building a production-ready multi-agent travel planning system. Over 4 hours, you'll learn how to orchestrate specialized AI agents, implement sophisticated memory patterns, and leverage Azure Cosmos DB for persistent state management.

**What you'll build:** A 6-agent system that helps users plan trips by remembering their preferences, detecting contradictions, and proactively suggesting options based on past behavior.

---

## What You'll Learn

1. **Multi-agent orchestration** - Design and coordinate specialized agents using LangGraph
2. **Agentic memory systems** - Build memory that goes beyond simple RAG retrieval
3. **Azure Cosmos DB integration** - Use vector search, checkpointing, and TTL for state management
4. **Advanced memory patterns** - Implement conflict detection, contextual filtering, and proactive suggestions
5. **Agent observability** - Monitor and debug complex agent interactions with LangSmith

---

## Workshop Flow

### Module 1: Foundation

#### Building Your First Multi-Agent System

Start by creating the core orchestrator pattern. You'll implement an orchestrator agent that routes user requests and an itinerary generator that creates trip plans.

**What you'll do:**

- Set up Azure Cosmos DB with checkpointing for conversation persistence
- Build an orchestrator that intelligently routes requests
- Create your first specialized agent (itinerary generator)
- Learn the LangGraph StateGraph and Command patterns

**Key concepts:**

- How agent orchestration differs from single-agent systems
- State management across conversation turns
- Tool-based routing with `transfer_to_*` functions
- Why checkpointing matters for production systems

**Hands-on task:** Wire up the orchestrator and itinerary generator, test conversation persistence by closing and reopening your session.

---

### Module 2: Specialization

#### Adding Domain Experts

Now scale your system by adding three specialized agents: one for hotels, one for restaurants, and one for activities. Each agent gets its own tools and expertise.

**What you'll do:**

- Implement Hotel Agent for accommodation search
- Implement Dining Agent for restaurant discovery
- Implement Activity Agent for attraction recommendations
- Configure vector search on Azure Cosmos DB for semantic place discovery
- Set up agent-to-agent handoffs

**Key concepts:**

- Designing domain-specific agents
- Vector embeddings for semantic search
- Tool distribution strategy (which tools go to which agents)
- Multi-agent collaboration patterns

**Hands-on task:** Test the full workflow - ask for hotel recommendations, then restaurants, then have the itinerary generator synthesize everything into a day-by-day plan.

---

### Module 3: Memory Foundation

#### Teaching Your Agents to Remember

This is where things get interesting. Add memory capabilities so your agents remember user preferences across sessions and conversations.

**What you'll do:**

- Implement memory storage across all specialized agents
- Design memory schemas with three types:
  - **Declarative**: Long-term facts (dietary restrictions)
  - **Procedural**: Behavioral patterns (price preferences)
  - **Episodic**: Trip-specific memories (places visited)
- Add memory recall before search operations
- Configure TTL policies for automatic memory expiration

**Key concepts:**

- Why agentic memory differs from traditional RAG
- Memory salience and confidence scoring
- When to store vs. when to recall
- Cross-session persistence

**Hands-on task:** Tell the system "I'm vegetarian" in one session, then start a new conversation and watch the dining agent automatically filter for vegetarian restaurants without being reminded.

---

### Module 4: Advanced Memory

#### Making Memory Intelligent

Take your memory system to production-grade with conflict detection, contextual filtering, and proactive suggestions.

**What you'll do:**

**Part A: Conflict Detection**

- Implement logic to catch contradictions (e.g., "I'm vegetarian" vs "I love steak")
- Handle conflicts gracefully by asking for clarification
- Test dietary, price, and style preference conflicts

**Part B: Contextual Recall**

- Filter memories based on trip context (destination, trip type, season)
- Ensure Paris memories don't pollute Tokyo trip planning
- Keep declarative/procedural memories active across all contexts

**Part C: Proactive Suggestions**

- Surface high-confidence preferences the user hasn't mentioned
- Present suggestions without being annoying (max 2-3 at a time)
- Let users confirm or decline each suggestion

**Part D: Auto-Summarization**

- Automatically compress conversations after 10 messages
- Set TTL on old messages to keep context window manageable
- Add summarizer agent to your graph

**Key concepts:**

- Detecting semantic contradictions in preferences
- Context-aware memory activation
- Balancing proactive vs. reactive behavior
- Long-term conversation management

**Hands-on task:** Create a conflict scenario, test contextual filtering with different destinations, and trigger auto-summarization with a long conversation.

---

### Module 5: Observability & Experimentation

#### Monitoring Your Agent Ecosystem

Production systems need visibility. Set up LangSmith to trace execution, measure performance, and debug failures.

**What you'll do:**

- Enable LangSmith tracing with `@traceable` decorators
- Explore execution traces in the LangSmith dashboard
- Experiment with different prompt variations to optimize agent behavior
- Create prompt experiments to A/B test itinerary generation (tentative)
- Analyze latency and token usage across agents
- Compare performance metrics across different memory recall strategies

**Key concepts:**

- Why distributed tracing matters for multi-agent systems
- Reading execution graphs to debug routing issues
- Using LangSmith experiments to improve prompts and agent behavior
- Cost and performance optimization
- Iterative improvement through experimentation

---

### Session 6: Wrap-up & Discussion

#### Looking Back and Looking Forward

**Lessons Learned:**

- When to choose multi-agent vs. single-agent architectures
- Memory design patterns that work in production
- Azure Cosmos DB as an agentic memory store

**Production Considerations:**

- Error handling strategies for agent failures
- Rate limiting and cost management
- Security and privacy for user memories

**What's Next:**

- Memory consolidation and forgetting strategies
- Cross-user collaborative filtering (what do similar users prefer?)
- Reinforcement learning for continuous agent improvement
- Multi-modal agents (images, audio, video)

**Open discussion and Q&A**

---

## System Architecture

You'll build a 6-agent system with clear responsibilities:

**Orchestrator** → Entry point, routes all requests  
**Hotel Agent** → Searches accommodations, stores lodging preferences  
**Dining Agent** → Searches restaurants, stores food preferences  
**Activity Agent** → Searches attractions, stores activity preferences  
**Itinerary Generator** → Synthesizes recommendations into trip plans  
**Summarizer** → Compresses conversation history (auto-triggered)

### Data Flow Example

```
User: "Find hotels in Barcelona"
  ↓
Orchestrator (routes to Hotel Agent)
  ↓
Hotel Agent recalls preferences → searches → presents results
  ↓
User selects hotel
  ↓
User: "Now find restaurants"
  ↓
Orchestrator (routes to Dining Agent)
  ↓
Dining Agent recalls preferences → searches → presents results
  ↓
User: "Create my itinerary"
  ↓
Orchestrator (can directly call Itinerary Generator or route based on query)
  ↓
Itinerary Generator reads conversation context → synthesizes plan → saves trip
```

**Note:** The orchestrator intelligently decides whether to call specialized agents first (hotel, dining, activity) or go directly to the itinerary generator based on the user's query complexity and available context.

---

## Memory System Design

Three memory types work together to create personalized experiences:

**Declarative Memory** (Permanent)  
Facts about the user: "Vegetarian", "Needs wheelchair access", "Speaks Spanish"

**Procedural Memory** (Permanent)  
Behavioral patterns: "Prefers boutique hotels", "Always books window seats", "Late checkout"

**Episodic Memory** (90-day TTL)  
Trip-specific events: "Visited Colosseum on Rome trip", "Ate at La Pergola restaurant"

### Why This Matters

Traditional RAG systems treat all retrieved information equally. Agentic memory adds:

- **Salience scoring** - Some preferences matter more than others
- **Temporal awareness** - Recent preferences may override old ones
- **Context filtering** - Paris memories stay quiet during Tokyo planning
- **Conflict detection** - System catches contradictions and asks for clarification

---

## Technology Stack

**Azure Cosmos DB**

- Vector search for semantic place discovery
- NoSQL containers for flexible schema
- Checkpointing for conversation state
- TTL for automatic data expiration

**Azure OpenAI**

- GPT-4o-mini for agent reasoning
- text-embedding-3-small for vector embeddings

**LangGraph**

- Multi-agent orchestration
- State management
- Conditional routing

**LangSmith**

- Distributed tracing
- Performance monitoring
- Prompt experiments

---

## Prerequisites

**Required:**

- Python 3.11 or higher
- Azure subscription with access to Cosmos DB and OpenAI
- Basic understanding of async/await in Python
- Familiarity with REST APIs

**Helpful but not required:**

- Prior experience with LangChain or LangGraph
- Understanding of vector embeddings
- Knowledge of Azure services

## What You'll Receive

1. Four Module folders with skeleton code and clear TODOs
2. Complete reference implementation for comparison
3. Azure deployment templates using `azd`
4. Prompt templates for all six agents
5. Test scenarios and sample data (hotels, restaurants, activities)
6. Step-by-step README for each module

## Why This Workshop?

**Production-Ready Code**  
This isn't a toy example. You're using real Azure services, handling errors, managing costs, and designing for scale.

**Progressive Learning**  
Each exercise builds naturally on the previous one. By the end, you'll have a complete system you can actually deploy.

**Memory-First Approach**  
Most workshops focus on RAG retrieval. We go deeper into how agents should remember, forget, and reason about preferences over time.

**Hands-On Implementation**  
You'll write code, not just watch demos. Each exercise has clear TODOs and test scenarios to validate your work.

---

## Success Metrics

By the end of this workshop, you should be able to:

✅ **Architecture**: Explain when to use multi-agent vs. single-agent patterns  
✅ **Implementation**: Build a working 6-agent system from scratch  
✅ **Memory**: Design memory schemas with appropriate TTL policies  
✅ **Persistence**: Demonstrate memory working across sessions ("I'm vegetarian" remembered next week)  
✅ **Conflicts**: Detect and handle contradictory preferences (vegetarian vs. steak)  
✅ **Context**: Filter memories by trip context (Paris memories stay quiet for Tokyo trips)  
✅ **Proactive**: Surface unmentioned preferences at appropriate times  
✅ **Observability**: View and interpret traces in LangSmith  
✅ **Deployment**: Deploy your system to Azure using provided templates

---

_Workshop materials are available at the GitHub repository. All code follows Microsoft best practices for AI agent development and uses production-ready Azure services._
