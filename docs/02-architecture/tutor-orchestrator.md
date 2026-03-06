# Tutor Orchestrator

This document defines the design and internal mechanics of the
Tutor Orchestrator — the central decision-making component of AIGORA.

It covers the orchestrator's responsibilities, its intent resolution
model, its reasoning transparency layer, and the constraints that
govern its operation.

This document is a direct extension of the
[Interaction Model](interaction-model.md).

---

# Design Principle

The Tutor Orchestrator is a **supervisor**.

It does not execute tutoring actions directly.
It comprehends student input, forms a resolution plan,
and delegates to the right components at the right time.

The separation between *deciding* and *executing* is what keeps
the orchestrator coherent under complexity. A supervisor that
begins executing before it has understood is not a supervisor —
it is a reactive system.

The orchestrator's primary obligation is to understand before acting.

---

# Responsibilities

The Tutor Orchestrator is responsible for:

- Classifying student input by nature and authority
- Assessing classification confidence before committing to a plan
- Requesting clarification when classification is ambiguous
- Forming and committing to a resolution plan
- Coordinating consultive component calls during authority traversal
- Resolving scope from traversal output
- Forming and executing a response strategy
- Committing reflexive updates after the response is delivered
- Projecting its reasoning to the student in real time
- Enforcing the implementation boundary at all times

---

# Intent Resolution

The orchestrator cannot route what it has not understood.

Intent resolution is the process by which a raw student input
is transformed into a structured, actionable description
of what the student needs — before any component is invoked.

Resolution is not binary. An input may carry multiple natures
and require multiple authorities. The orchestrator must hold
this multiplicity without collapsing it prematurely.

## Dimension 1 — Input Nature

Input Nature describes *what kind of thing* the student expressed.

A single input may carry more than one nature simultaneously.

| Nature | Description | Example |
|---|---|---|
| **Content** | Question about the material itself | "What is the discriminant?" |
| **Procedural** | Request to perform a specific action | "Show me another example" |
| **Verificational** | Checking their own understanding | "So this means the roots are equal, right?" |
| **Analogical** | Connecting to prior knowledge | "Is this like linear functions?" |
| **Affective** | Emotional or motivational signal | "I don't get this at all" |
| **Metacognitive** | Reasoning about their own learning | "I keep making the same mistake" |
| **Strategic** | About exams, approach, or pacing | "Will this be on the exam?" |

Input Nature is classified from the input alone.
No component call is needed at this stage.

## Dimension 2 — Resolution Authority

Resolution Authority defines *which components* hold the
knowledge required to resolve the input.

Authority is derived from Input Nature.
A single input may require more than one authority.

| Authority | Component | Serves |
|---|---|---|
| **Structural** | Curriculum Graph | Prerequisite reasoning, topic location, concept relationships |
| **Contextual** | Student Model | Current mastery, known gaps, interaction history |
| **Generative** | LLM Interface | Explanations, hints, analogies, guided responses |
| **Evaluative** | Assessment Engine | Exercise outcomes, answer correctness, diagnostic results |
| **Retrievive** | Retrieval Layer | Grounded learning material, worked examples |
| **Orchestral** | Tutor Orchestrator | Strategic or metacognitive inputs the orchestrator resolves directly |

Some input natures map with high determinism to specific authorities.
Affective and strategic inputs are frequently resolved by the
orchestrator itself, without invoking external components.

## Scope as a Resolved Property

Scope — the level of the curriculum an input refers to —
is **not classified upfront**.

It is an output of the authority traversal phase.
It cannot be determined from the input alone because
its meaning depends on where the student currently is
in the curriculum and what their knowledge state reveals.

| Scope Level | Description |
|---|---|
| **Sub-concept** | A symbol, term, notation, or step |
| **Exercise** | The specific problem currently in progress |
| **Topic** | The concept currently under study |
| **Cross-topic** | A relationship to another point in the curriculum graph |
| **Curriculum** | The broader learning path and progression |

Scope is resolved by consulting the Curriculum Graph and
Student Model during the traversal phase.
It informs response strategy but does not precede it.

---

# Clarification as a Guardrail

Before committing to a resolution plan, the orchestrator must assess
whether the upfront classification is confident enough to proceed.

If it is not, the correct action is to ask the student —
not to assume and traverse on a misclassified intent.

This guardrail protects the student domain from consequential writes
derived from misunderstood input, and protects traversal efficiency
from wasted consultive calls.

It is also pedagogically sound. A good tutor asks before assuming.

## Ambiguity Criteria

A classification is considered ambiguous when one or more of the
following conditions is met:

**1. Input Sparsity**
The input is too short or too vague to yield a reliable
nature classification.

Examples: *"I don't know"*, *"hm"*, *"ok"*, *"this is hard"*

These inputs carry a signal — likely affective or metacognitive —
but insufficient information to act on with confidence.

**2. Nature Collision**
Two or more natures are equally plausible from the input,
and they lead to contradictory traversal profiles.

Example: *"Can we go back?"*
This could be procedural (repeat the last exercise),
metacognitive (the student senses a gap), or
analogical (wanting to revisit a prior concept).
Each nature implies a different authority and a different response.

**3. Context Dependency**
The correct nature classification depends on curriculum context
that the orchestrator does not yet hold —
and assuming a default would risk a wrong traversal.

Example: *"I think I understand now"*
Without knowing what was just explained and what the
student model says about their prior state, this input
cannot be reliably classified as verificational or affective.

**4. Authority Conflict**
Derived authorities point in incompatible directions,
suggesting the nature classification itself is unstable.

Example: an input that simultaneously suggests Structural
and Evaluative authority without a clear nature that
bridges them indicates the input was not fully understood.

## Clarification Constraints

When the orchestrator decides to request clarification:

- It must ask **one focused question only**.
- The question must be **pedagogically framed** — it must sound like a tutor asking, not a system prompting.
- It must **never expose implementation** — no mention of components, authorities, or classification logic.
- Clarification rounds are **bounded to one** per input. If the clarified input remains ambiguous, the orchestrator defaults to the most conservative nature and proceeds.
- Clarification must **never be used as a stall**. If the nature is clear enough to proceed, proceed.

## Clarification Examples

| Ambiguous Input | Clarification Question |
|---|---|
| "I don't know" | "Is there a specific part that's unclear, or does the whole thing feel confusing?" |
| "Can we go back?" | "Do you want to try the last exercise again, or revisit an earlier concept?" |
| "This is hard" | "Is it the idea itself that's tricky, or the steps to solve it?" |
| "I think I understand now" | "Would you like to try a problem to check?" |

---

# Authority Traversal

Authority traversal is the process of invoking consultive
components to resolve scope and gather the context needed
for response planning.

## Nature-Guided Traversal

Traversal is not uniform. It is guided by the Input Nature
classification resolved upfront.

Different natures carry different traversal profiles,
allowing the orchestrator to prune unnecessary consultive
calls before they are made.

| Input Nature | Likely Authorities | Traversal Priority |
|---|---|---|
| Content | Structural, Retrievive, Generative | Curriculum Graph first |
| Procedural | Retrievive, Generative | Retrieval Layer first |
| Verificational | Contextual, Evaluative | Student Model first |
| Analogical | Structural, Contextual, Generative | Curriculum Graph first |
| Affective | Orchestral | Orchestrator resolves directly |
| Metacognitive | Contextual, Orchestral | Student Model first |
| Strategic | Orchestral | Orchestrator resolves directly |

Traversal terminates as soon as sufficient context for
response planning has been established.
The orchestrator must not over-consult.

## Traversal Constraints

- Consultive calls must be parallelized where dependencies permit.
- Reflexive calls must never occur during traversal.
- Traversal depth must be bounded to avoid latency accumulation.
- Scope is a product of traversal, not a precondition to it.

---

# Resolution Plan

The orchestrator forms a resolution plan before any action is taken.
The plan is the orchestrator's structured intent — what it will do,
in what order, and why — derived from the upfront classification
and confirmed before traversal begins.

The plan is not execution. It is the decision to execute.

```
1. Classify Input Nature        (from input, upfront, no components)
2. Derive Resolution Authority  (from nature, upfront, no components)
3. Assess Classification        (confidence check, no components)
   → if ambiguous: request clarification from student (bounded to one round)
   → if confident: form and commit to plan
4. Traverse Authorities         (consultive calls, nature-guided, bounded)
5. Resolve Scope                (output of traversal)
6. Form Response Strategy       (using resolved intent + scope)
7. Execute Response             (LLM Interface, student-facing)
8. Commit Reflexive Updates     (Student Model, Assessment Engine)
```

Steps 1–3 are synchronous and component-free.
Step 3 is a guardrail gate — it either loops back to the student or commits the plan.
Steps 4–5 are consultive and must be parallelized where possible.
Steps 6–7 are generative.
Step 8 is reflexive and must occur after the response is delivered.

---

# Reasoning Transparency Layer

The orchestrator projects its reasoning to the student in real time.

This is not an implementation leak. It is an intentional
pedagogical surface — a live, ordered view of what the
orchestrator is working through, translated into language
the student can follow and trust.

The distinction is precise:

> An **implementation leak** is unintentional, unframed,
> and exposes architecture.
>
> The **reasoning surface** is intentional, pedagogically framed,
> and exposes intent.

The student never sees component names, traversal logic, or
internal state. They see a tutor thinking out loud.

## What the Student Sees

Each step of the resolution plan has a corresponding
student-facing signal. These signals are brief, natural,
and pedagogically framed.

| Resolution Plan Step | Student-Facing Signal |
|---|---|
| Classify Input Nature | *(silent — no signal needed)* |
| Derive Resolution Authority | *(silent — no signal needed)* |
| Assess Classification | "Let me make sure I understand what you're asking..." |
| Clarification Request | "Could you tell me a bit more — ..." |
| Traverse Authorities | "Let me check where this fits in what you've been working on..." |
| Resolve Scope | *(silent — feeds into response strategy)* |
| Form Response Strategy | "Ok, I think I know what will help here." |
| Execute Response | *(the response itself)* |
| Commit Reflexive Updates | *(silent — never student-facing)* |

Silent steps are those where surfacing a signal would add
noise without pedagogical value.

## Properties of the Reasoning Surface

- **Ordered** — signals follow the resolution plan in sequence.
- **Bounded** — only steps with pedagogical signal value are surfaced.
- **Collapsible** — the student may minimise or dismiss the surface without affecting orchestration.
- **Non-blocking** — signals appear as the plan progresses, not after it completes.
- **Framed as thinking, not processing** — the tutor thinks, it does not compute.

## What the Reasoning Surface Is Not

- It is not a progress bar or a loading indicator.
- It is not a debug console.
- It is not a transcript of internal decisions.
- It is not a guarantee of what will happen next.

It is a window into the tutor's intent — nothing more.

---

# Session Design Constraints

## Short Sessions

Sessions are intentionally bounded.

Long sessions accumulate context beyond what an LLM can
hold coherently, degrading response quality over time.
They also couple continuity to the session itself,
which is fragile.

Sessions must not be the unit of continuity.

## Student Model as Memory

Continuity across sessions is the responsibility of the
Student Model, not the session.

At the start of each session, the orchestrator reconstructs
a minimal, structured context from the Student Model —
sufficient to be pedagogically coherent, not a reproduction
of prior sessions.

This means:

- Sessions are stateless by design.
- The Student Model is the persistent memory of the system.
- Context reconstruction is deliberate and bounded.
- Revisiting prior knowledge is possible without long sessions.

---

# Domain Ownership and Implementation Boundary

## Student Domain Ownership

The student owns their domain: mastery state, learning
history, progression trajectory. These are built through
interaction and belong to the student.

The orchestrator must treat student-built domains with
corresponding care — reads inform decisions, writes
are consequential and must be intentional.

## Implementation Boundary

The orchestrator is the boundary between the student's
experience and the system's implementation.

Nothing behind the orchestrator should be visible to the student:

- No component names
- No internal state representations
- No orchestration logic
- No traversal decisions

The student interacts with a tutor.
They must never interact with an architecture.

Violating this boundary is an implementation leak.
It degrades trust, confuses the student, and
couples the experience to internal design decisions.

The reasoning surface is the single controlled exception —
it surfaces intent, not implementation, and only through
the orchestrator's own framing.

---

# Constraints Summary

- The orchestrator is a supervisor. It decides before it acts.
- Input Nature and Resolution Authority are always resolved upfront.
- Classification confidence is always assessed before the resolution plan is committed.
- Ambiguous classifications trigger a clarification request, not a traversal assumption.
- Clarification is bounded to one round per input. If still ambiguous, default to the most conservative nature.
- Clarification questions are always pedagogically framed. Implementation must never be exposed.
- The resolution plan is formed and committed before traversal begins.
- Scope is always resolved through traversal, never assumed.
- Traversal is nature-guided to minimize unnecessary consultive calls.
- Reflexive calls must never occur during traversal or response planning.
- The reasoning surface projects intent, not implementation.
- Reflexive updates are never surfaced to the student.
- Sessions are stateless. Continuity lives in the Student Model.
- Context reconstruction at session start must be minimal and structured.
- The orchestrator is the implementation boundary. Nothing leaks through it.
- The reasoning surface is the single controlled exception to the implementation boundary.
- Student-built domains are owned by the student. Writes are consequential.

