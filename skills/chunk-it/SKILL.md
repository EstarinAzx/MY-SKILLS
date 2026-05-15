---
name: chunk-it
description: Annotate code with section banners above functions and inline chunk comments explaining each logical part in plain English, making unfamiliar code readable at a glance. Use when user runs /chunk-it, says "chunk it" or "chunk this file", or asks for an annotated / readable version of a file. If user adds "with glossary" or "/chunk-it --glossary", also include a glossary of unfamiliar symbols at the bottom.
---

# Chunk It

Take a piece of code and return it with a banner above each function and short inline comments above each logical chunk inside. The goal is to make the code skimmable — someone reading just the banners and inline comments should understand what the file does.

## Workflow

1. Read the whole file first to understand its overall shape.
2. Above each function (or major section), add a banner comment derived from the function name in spaced ALL-CAPS:
```
   // ---- GET TOP CUSTOMERS ----
```
   Convert `camelCase` or `snake_case` to spaced uppercase (`getTopCustomers` → `GET TOP CUSTOMERS`).
3. Inside the function, identify the logical sections — usually 3–7 chunks. Each chunk should do *one conceptual thing*.
4. Insert a plain inline comment above each chunk: `// <plain-English description>`. No numbering, no "CHUNK" prefix — just the description.
5. Use the right comment syntax for the language: `//` for JS/TS/Java/C/Go/Rust, `#` for Python/Ruby/Bash, `--` for SQL/Lua, `<!-- -->` for HTML. Adapt the banner accordingly (e.g. `# ---- GET TOP CUSTOMERS ----` in Python).
6. Add a blank line before each chunk comment (except the first inside a function) for visual separation.
7. Preserve the original code exactly — do not refactor, rename, or "fix" anything. Only add comments.
8. After the annotated code, add a one-sentence summary: *"This function [verb-chain summary]."*
9. **Only if the user explicitly asked for it** (e.g. "with glossary", "explain the symbols", `--glossary` flag): include a Glossary section.

## Banner rules

- Format: `// ---- FUNCTION NAME IN CAPS ----` (use the language's comment syntax).
- Skip the banner for tiny helper functions under ~5 lines.
- Banner every major function in the file.

## Inline chunk comment rules

- Use verbs: "validate inputs", "fetch data", "format response", "return result".
- Keep each comment under 10 words.
- Describe **intent**, not syntax. ✅ "calculate total"  ❌ "use reduce on orders array".
- Plain `// description` — no numbering, no labels.

## Glossary rules (ONLY when requested)

- Do not include a glossary by default. Only when the user explicitly asks for it.
- Only include symbols/patterns that actually appear in the code.
- Focus on things a beginner-to-intermediate dev might not recognize:
  - **JavaScript/TypeScript:** `=>`, `...spread`, `?.`, `??`, ternary `? :`, destructuring `{ a, b } =`, template literals, `async`/`await`, array methods (`.map`, `.reduce`, `.filter`, `.sort`, `.slice`, `.find`).
  - **React:** JSX (`<Component />`), hooks (`useState`, `useEffect`, anything `use*`), `{expression}` inside JSX, prop spreading `{...props}`.
  - **Python:** list/dict comprehensions, decorators `@`, `*args` / `**kwargs`, lambda, walrus `:=`, f-strings, `with` blocks.
- Skip basic stuff like `if`, `for`, `return`.
- Format: `` **`symbol`** — what it means. *Example: brief example if helpful.* ``

## Example

Input:
```js
export async function getTopCustomers(limit) {
  const allCustomers = await db.customers.findAll();
  const withTotals = allCustomers.map(c => ({
    name: c.name,
    totalSpent: c.orders.reduce((s, o) => s + o.amount, 0),
  }));
  const sorted = withTotals.sort((a, b) => b.totalSpent - a.totalSpent);
  return sorted.slice(0, limit);
}
```

Output:
```js
// ---- GET TOP CUSTOMERS ----
export async function getTopCustomers(limit) {
  // get all customers from the database
  const allCustomers = await db.customers.findAll();

  // for each customer, calculate their total spending
  const withTotals = allCustomers.map(c => ({
    name: c.name,
    totalSpent: c.orders.reduce((s, o) => s + o.amount, 0),
  }));

  // sort customers from highest spender to lowest
  const sorted = withTotals.sort((a, b) => b.totalSpent - a.totalSpent);

  // return only the top `limit` customers
  return sorted.slice(0, limit);
}
```

**Summary:** *This function gets all customers, calculates each one's total spending, sorts by highest spender, and returns the top N.*

## What this skill does NOT do

- It does not refactor, rewrite, or "improve" code.
- It does not quiz the user.
- It does not include a glossary unless explicitly requested.