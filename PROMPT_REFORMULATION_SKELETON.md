# Prompt Reformulation Skeleton - Technology-First Narrative

## Core Philosophy Shift
**OLD**: Business consultant → ROI, budgets, market sizing, competitive positioning
**NEW**: Software architect → Algorithms, system design, implementation formulation, research directions

---

## Output Structure (9k-14k words, flexible range)

### Section 1: Technical Context & Innovation (800-1200 words)
**Instead of**: "Market Intelligence" (market sizing, trends, competitors)
**Now**: "Technology Landscape & Research Context"
- What academic research/papers exist on this problem?
- What existing frameworks/libraries solve parts of this?
- What are the known limitations in current approaches?
- What technology trends are relevant?
- **Output mode**: Educational + forward-thinking (not market-speak)

### Section 2: Problem Decomposition (1000-1500 words)
**Instead of**: "Problem Analysis" (ROI impact, pain points, market demand)
**Now**: "Algorithmic & Technical Challenge Breakdown"
- What are the computational bottlenecks?
- What algorithms currently exist and why are they insufficient?
- Complexity analysis: time/space tradeoffs?
- What edge cases break existing solutions?
- **Output mode**: Technical rigor + research perspective

### Section 3: Solution Architecture Deep-Dive (1500-2000 words)
**Instead of**: "Solution Architecture & Mechanisms" (competitive differentiation)
**Now**: "Technical Architecture & Algorithm Design"
- Core algorithms: pseudocode + complexity analysis
- Data structures: why these choices? (indexing, hashing, trees, graphs, etc.)
- System components and their interactions
- Query optimization strategies
- Performance characteristics with concrete examples
- **Output mode**: Implementation-ready (code sketches, not actual code)

### Section 4: Software Implementation Formulation (1000-1500 words)
**NEW SECTION** (user specifically requested this):
- Technology stack rationale: Why Python + Framework X? Why database Y?
- Design patterns: MVC, event-driven, pipeline architecture, etc.
- Pseudocode for 2-3 critical algorithms/functions
- Library selection: requests, sklearn, torch, fastapi, sqlalchemy, etc. - and why
- Scalability approach: caching layers, parallelization, async patterns
- **Output mode**: "How would a senior engineer implement this?"

### Section 5: Advanced Technical Topics (1000-1500 words)
**Instead of**: "Implementation Roadmap" (timeline, budget, staffing)
**Now**: "Innovation Angles & Performance Optimization"
- Novel algorithmic approaches beyond the obvious
- Distributed/parallel computation strategies
- Memory optimization and profiling
- Real-time vs batch processing tradeoffs
- Experimental variations and research directions
- **Output mode**: Advanced/experimental thinking

### Section 6: Integration & System Flows (800-1200 words)
**Instead of**: "KPI Framework & Business Case" (ROI projections, financial impact)
**Now**: "System Integration & Data Pipeline Architecture"
- How does this connect to existing systems?
- API design and data contract specifications
- Data flow diagrams (textual descriptions)
- Error handling and fault tolerance strategies
- Consistency and synchronization mechanisms
- **Output mode**: Systems thinking, robustness focus

### Section 7: Algorithm Comparison & Tradeoffs (800-1000 words)
**Instead of**: "Competitive & Market Analysis" (competitor positioning)
**Now**: "Alternative Approaches & Technical Tradeoffs"
- Algorithm A vs B vs C: when to use each?
- Speed vs accuracy vs memory tradeoffs
- Why the chosen approach wins on technical merit
- Benchmarking methodology (how to measure performance)
- **Output mode**: Technical decision framework

### Section 8: Testing & Validation Strategy (700-1000 words)
**Instead of**: "Critical Success Factors" (business dependencies)
**Now**: "Technical Testing & Verification**
- Unit test structure and coverage targets
- Performance benchmarking protocols
- Edge case identification and testing
- Integration testing approach
- Robustness validation (stress testing, chaos engineering mindset)
- **Output mode**: Quality assurance + rigor

### Section 9: Research & Future Evolution (500-800 words)
**Instead of**: "Strategic Vision & Long-Term Impact" (market transformation)
**Now**: "Research Directions & Next-Gen Approaches"
- Emerging technologies relevant to this domain (ML, quantum, GPU acceleration, etc.)
- Open problems in this space (unsolved research questions)
- Potential extensions and variations
- Long-term technical vision (5+ years)
- **Output mode**: Future-oriented, exploratory

---

## Key Content Rules (Reformulated)

### What to REMOVE:
- ❌ Any mention of ROI, revenue, cost savings, pricing
- ❌ Market sizing, addressable opportunity, competitive positioning
- ❌ Budget breakdowns, staffing needs, phased timelines in business terms
- ❌ Financial projections and business case language
- ❌ Executive summary focused on business value

### What to ADD:
- ✅ **Pseudocode sketches** for critical algorithms (even if not runnable, shows formulation)
- ✅ **Data structure justifications** (why this tree over that graph?)
- ✅ **Complexity analysis** (Big-O notation, memory implications)
- ✅ **Technology stack rationale** (framework/library choices with reasoning)
- ✅ **Performance optimization techniques** (caching, parallelization, profiling)
- ✅ **Research citations & academic grounding** (even as general references)
- ✅ **Software design patterns** (Factory, Observer, MVC, pipeline, etc.)
- ✅ **Edge cases & robustness thinking**

---

## Writing Tone Transformation

| Aspect | OLD (Business) | NEW (Technology) |
|--------|---|---|
| **Audience** | Board executives | Software architects & senior engineers |
| **Language** | "Strategic opportunity", "market advantage", "ROI projection" | "Algorithmic efficiency", "system scalability", "implementation pattern" |
| **Depth** | Breadth (many topics, all business-framed) | Technical depth (fewer topics, very detailed) |
| **Examples** | Case studies of successful business implementations | Technical case studies & architectural decisions |
| **Numbers** | Revenue, market size, customer count | Latency (ms), throughput (req/sec), memory (GB), complexity (O-notation) |
| **Future Talk** | "3-5 year market vision" | "Emerging tech: GPUs for compute, GraphQL for APIs, WebAssembly for edge" |

---

## Token Range Strategy (9k-14k)

The 9k-14k range is **intentionally flexible** because:
- If a topic needs deep dive → expand that section (add more algorithm detail, more design patterns)
- If a topic is straightforward → keep it tighter (less elaboration)
- **Minimum threshold (9k)**: Ensures solid coverage of all 9 sections
- **Maximum threshold (14k)**: Prevents bloat; focus on high-value technical depth, not repetition

### Token Distribution (approximate):
- Section 1 (Context): 900 words
- Section 2 (Problems): 1200 words
- Section 3 (Architecture): 1700 words ← heaviest section (core technical depth)
- Section 4 (Implementation): 1300 words ← NEW, user-requested
- Section 5 (Advanced Topics): 1200 words
- Section 6 (Integration): 1000 words
- Section 7 (Algorithm Tradeoffs): 900 words
- Section 8 (Testing): 800 words
- Section 9 (Research): 700 words

**Total: ~10,300 words (mid-range, comfortable)**

---

## Example Reformulated Prompt Hooks

Instead of:
> "ROI projections and financial impact"

Say:
> "Performance metrics: latency (p50, p99), throughput (requests/sec), memory footprint (MB/GB), CPU efficiency; how to measure and optimize each"

Instead of:
> "Competitive differentiation: why this solution works better than alternatives"

Say:
> "Algorithm comparison: why approach A (chosen) outperforms B and C on O(n log n) vs O(n²); tradeoff analysis with real benchmark numbers"

Instead of:
> "3-5 year vision: transformative impact on market"

Say:
> "5-year technical vision: integration with emerging GPU acceleration, quantum-inspired optimization, real-time processing at scale; research opportunities in [domain]"

---

## Implementation Notes for LLM Prompting

When crafting the actual prompt to send to gpt-4o-mini:

1. **Lead with the 10-section framework** explicitly ("Section 1: ..., Section 2: ...")
2. **Add pseudocode placeholders**: "For Section 4, include pseudocode sketch like: `function(input) -> { ... }`"
3. **Specify technical metrics**: "Use concrete numbers for performance (latency in ms, throughput in req/sec)"
4. **Flexibility directive**: "Aim for 9,000-14,000 words total; if a section needs deep technical explanation, expand it; skip fluff"
5. **Tone directive**: "Assume audience is senior engineers and architects, not business stakeholders"

---

## Summary: The Mental Model Shift

**OLD MENTAL MODEL:**
"How do we sell this idea? What's the business case? How do we compete?"
→ Output: Polished business narrative with ROI projections

**NEW MENTAL MODEL:**
"How do we build this? What are the technical insights? What patterns and tradeoffs matter?"
→ Output: Technical deep-dive with algorithms, design patterns, implementation hints, research directions

**Output Length Control:**
- NOT "make it longer" (padding problem)
- BUT "go deeper on technical topics" (value-add problem)
- 9k-14k is the envelope; fill it with substance, not filler
