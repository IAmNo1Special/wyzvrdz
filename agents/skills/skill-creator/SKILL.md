---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run Wyzvrd with access to the skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, you can either use as is or modify if you feel something needs to change about them). Then explain them to the user (or if they already existed, explain the ones that already exist)
  - Use the `eval-viewer/generate_review.py` script to show the user the results for them to look at, and also let them look at the quantitative metrics
- Rewrite the skill based on feedback from the user's evaluation of the results (and also if there are any glaring flaws that become apparent from the quantitative benchmarks)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages. So for instance, maybe they're like "I want to make a skill for X". You can help narrow down what they mean, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and repeat.

On the other hand, maybe they already have a draft of the skill. In this case you can go straight to the eval/iterate part of the loop.

Of course, you should always be flexible and if the user is like "I don't need to run a bunch of evaluations, just vibe with me", you can do that instead.

Then after the skill is done (but again, the order is flexible), you can also run the skill description improver, which we have a whole separate script for, to optimize the triggering of the skill.

Cool? Cool.

## Communicating with the user

The skill creator is liable to be used by people across a wide range of familiarity with coding jargon. Some users might be new to terminals and CLI tools, while others are highly computer-literate.

So please pay attention to context cues to understand how to phrase your communication! In the default case:

- "evaluation" and "benchmark" are generally fine.
- For technical terms like "JSON" and "assertion", check for user cues that they are familiar with these concepts before using them without explanation.

It's OK to briefly explain terms if you're in doubt, and feel free to clarify terms with a short definition if you're unsure if the user will get it.

---

## Creating a skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps, and should confirm before proceeding to the next step.

1. What should this skill enable Wyzvrd to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.

### Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs - if useful for research (searching docs, finding similar skills, looking up best practices), research in parallel via subagents if available, otherwise inline. Come prepared with context to reduce burden on the user.

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier
- **description**: When to trigger, what it does. This is the primary triggering mechanism - include both what the skill does AND specific contexts for when to use it. All "when to use" info goes here, not in the body. Note: Descriptions should be "pushy" to ensure the system recognizes relevant tasks. For instance, instead of "How to build a simple fast dashboard," use "How to build a simple fast dashboard. Make sure to use this skill whenever the user mentions dashboards, data visualization, or wants to display any kind of metrics, even if they don't explicitly ask for a 'dashboard.'"
- **compatibility**: Required tools, dependencies (optional, rarely needed)
- **the rest of the skill :)**

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** - As needed (unlimited, scripts can execute without loading)

These word counts are approximate and you can feel free to go longer if needed.

**Key patterns:**
- Keep SKILL.md under 500 lines; if you're approaching this limit, add an additional layer of hierarchy along with clear pointers about where the model using the skill should go next to follow up.
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>300 lines), include a table of contents

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant:
```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    ├── azure.md
```
Wyzvrd reads only the relevant reference file.

#### Principle of Lack of Surprise

Skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't create misleading skills or skills designed for unauthorized access or data exfiltration.

#### Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats** - You can do it like this:
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern** - It's useful to include examples. You can format them like this:
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing Style

Explain to the model why things are important instead of just using "MUST". Use theory of mind and try to make the skill general rather than narrow. Start by writing a draft and then improve it.

### Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

## Running and evaluating test cases

This section is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, etc.).

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. Launch everything at once so it all finishes around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about>
```

**Baseline run** (same prompt, but the baseline depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case. Give each eval a descriptive name.

### Step 2: While runs are in progress, draft assertions

Draft quantitative assertions for each test case and explain them to the user. Review and update `evals/evals.json`. Explain to the user what they'll see in the viewer.

### Step 3: As runs complete, capture timing data

Save token and duration data immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

### Step 4: Grade, aggregate, and launch the viewer

1. **Grade each run** — spawn a grader subagent. Save results to `grading.json`.
2. **Aggregate into benchmark** — run the aggregation script:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
3. **Do an analyst pass** — surface patterns from the data.
4. **Launch the viewer**:
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   **Headless environments:** Use `--static <output_path>` to write a standalone HTML file.

### Step 5: Read the feedback

When the user is done, read `feedback.json`. Focus improvements on complained-about cases. Kill the viewer server when finished.

---

## Improving the skill

Iterate based on feedback.

1. **Generalize from the feedback.** Focus on patterns rather than narrow examples.
2. **Keep the prompt lean.** Remove unproductive instructions.
3. **Explain the why.** Help the model understand the reasoning behind instructions.
4. **Look for repeated work.** Bundle repeated logic into scripts in `scripts/`.

### The iteration loop

1. Apply improvements to the skill.
2. Rerun all test cases into a new iteration directory.
3. Launch the reviewer with `--previous-workspace`.
4. Wait for user review.
5. Repeat until satisfied.

---

## Description Optimization

Optimize the description for better triggering accuracy.

### Step 1: Generate trigger eval queries

Create 20 realistic eval queries (10 should-trigger, 10 should-not-trigger). Use concrete details and varied phrasings. Avoid obviously irrelevant negative cases.

### Step 2: Review with user

Present the eval set using the HTML template from `assets/eval_review.html`. Write to a temp file and open it. User downloads updated `eval_set.json`.

### Step 3: Run the optimization loop

Run in the background:
```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id> \
  --max-iterations 5 \
  --verbose
```
This handles the full optimization loop automatically, selecting the best description based on test scores.

### Step 4: Apply the result

Update the skill's SKILL.md frontmatter with the `best_description`.

---

## Packaging

Package the skill into a `.skill` file:
```bash
python -m scripts.package_skill <path/to/skill-folder>
```

---

## Gotchas

- **Description Length**: Keep descriptions under 1024 characters. Frontmatter only loads ~100 tokens, body loads on trigger.
- **Script Paths**: Always use relative paths from skill root. Scripts execute from project root context.
- **Eval Workspace**: Put results in `<skill-name>-workspace/` as sibling to skill directory, not inside it.
- **Parallel Runs**: Spawn with-skill AND baseline subagents in the same turn to finish together.
- **5-Skill Limit**: After 5 failed `request_skill` attempts, assume skill doesn't exist.
- **JSON Schema**: Evals must use proper JSON format. Missing commas or quotes break the eval viewer.
- **Hard Negatives**: Always include test cases with keyword overlap (e.g., "write a Python script about weather" for weather skill).

## Reference files

- `agents/grader.md` — Evaluate assertions
- `agents/comparator.md` — Blind A/B comparison
- `agents/analyzer.md` — Analyze results
- `references/schemas.md` — JSON structures

---

Remember the core loop:
- Define intent
- Draft skill
- Run test prompts
- Evaluate with user
- Repeat
- Package
