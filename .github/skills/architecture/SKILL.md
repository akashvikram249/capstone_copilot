---
name: architecture
description: "Design the architecture for approved requirements: components, data flow, interfaces, security boundaries and technology choices."
argument-hint: "Approved requirements document"
---

# Architecture

1. Read the approved `requirements.md`, then look at the build files and the patterns the repository already uses.
2. Match each major requirement to the component that handles it and say what that component is responsible for.
3. Describe the boundaries, interfaces and data flow. For each technology choice, give the reason and what it costs.
4. Add a Mermaid diagram if it helps. Cover error handling, security and privacy boundaries, how the design will be tested, and what it assumes about where it runs.
5. In `architecture.md`, list what is in scope, what is out, and what is still uncertain.
6. Make sure every acceptance criterion has a path through the design. Flag the ones that don't, and note the risks.
7. Show the design and wait for approval before design review.

Don't write production code, and don't edit approved requirements without telling the user.
