#!/usr/bin/env python3
"""
Analyze a CLAUDE.md file and suggest optimizations using the 4-tier architecture.

Tier 1: CLAUDE.md (always active) — compact critical rules + mandatory operational rules
Tier 1.5: Rules files (.claude/rules/) — hard constraints, auto-loaded every session
Tier 2: Examples files (.claude/examples/) — detailed patterns with code examples
Tier 3: Skills — interactive workflow procedures

This script identifies sections and classifies them into the appropriate tier,
generating an optimization report with actionable suggestions.
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Tier(Enum):
    KEEP = "tier1_keep"               # Structural info, stays as-is
    MANDATORY = "tier1_mandatory"     # Operational/safety rules for Mandatory Rules section
    PROMOTE = "tier1_promote"         # Should be compacted into Code Standards section
    RULE = "tier1_5_rule"             # Hard constraints → .claude/rules/ (auto-loaded)
    EXAMPLE = "tier2_example"         # Detailed patterns → .claude/examples/ (on-demand)
    SKILL = "tier3"                   # Workflow → .claude/skills/
    AGENT = "agent"                   # Agent definition → .claude/agents/


@dataclass
class Section:
    """Represents a section in the CLAUDE.md file."""
    title: str
    level: int
    content: str
    line_start: int
    line_count: int

    @property
    def token_estimate(self) -> int:
        """Rough token estimate (1 token ~ 4 characters)."""
        return len(self.content) // 4


@dataclass
class ClassificationResult:
    """Represents a tier classification for a section."""
    section: Section
    tier: Tier
    reason: str
    target: str  # Where it should go (e.g., "rules/testing.md" or "skills/project-feature-dev")
    priority: str  # 'high', 'medium', 'low'
    promotable_rules: List[str] = field(default_factory=list)  # Rules to promote to Tier 1


def parse_markdown_sections(content: str) -> List[Section]:
    """Parse markdown content into sections."""
    sections = []
    lines = content.split('\n')
    current_section = None
    section_content = []
    section_start = 0

    for i, line in enumerate(lines, 1):
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

        if heading_match:
            if current_section:
                sections.append(Section(
                    title=current_section['title'],
                    level=current_section['level'],
                    content='\n'.join(section_content),
                    line_start=section_start,
                    line_count=len(section_content)
                ))

            level = len(heading_match.group(1))
            title = heading_match.group(2)
            current_section = {'title': title, 'level': level}
            section_content = []
            section_start = i
        elif current_section:
            section_content.append(line)

    if current_section and section_content:
        sections.append(Section(
            title=current_section['title'],
            level=current_section['level'],
            content='\n'.join(section_content),
            line_start=section_start,
            line_count=len(section_content)
        ))

    return sections


def extract_promotable_rules(content: str) -> List[str]:
    """Extract rules that could be promoted to Tier 1 as one-liners."""
    rules = []
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        # Look for "Always/Never/Must/Should" patterns
        if re.match(r'^[-*]\s*(always|never|must|should|do not|don\'t)\b', line, re.IGNORECASE):
            rules.append(line.lstrip('-* '))
        # Look for "Use X for Y" patterns
        elif re.match(r'^[-*]\s*use\s+\w+', line, re.IGNORECASE):
            rules.append(line.lstrip('-* '))
        # Look for naming convention patterns
        elif re.match(r'^[-*]\s*\w+\s*(should be|are) named', line, re.IGNORECASE):
            rules.append(line.lstrip('-* '))

    return rules[:5]  # Top 5 most promotable rules


def extract_hard_constraints(content: str) -> List[str]:
    """Extract binary constraints (MUST/NEVER/ALWAYS) suitable for rules files."""
    constraints = []
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        # Strong binary constraint patterns
        if re.match(r'^[-*]\s*(always|never|must|must not|forbidden|required)\b', line, re.IGNORECASE):
            constraints.append(line.lstrip('-* '))
        # declare(strict_types) and similar mandatory patterns
        elif re.search(r'(declare\(strict_types|final\s+class|private\s+readonly)', line):
            constraints.append(line.lstrip('-* '))

    return constraints[:8]


def is_operational_rule(content: str, title: str) -> bool:
    """Check if content contains operational/safety rules (tool usage, file safety)."""
    title_lower = title.lower()
    content_lower = content.lower()

    operational_keywords = [
        'tool usage', 'file safety', 'blocking policy', 'sub-agent',
        'never delete', 'never overwrite', 'never modify .env',
        'stop and report', 'stop immediately',
        'tool call', 'permission', 'denied',
        'destructive operation', 'dangerous',
    ]

    title_match = any(kw in title_lower for kw in [
        'mandatory', 'safety', 'tool usage', 'file safety', 'blocking',
        'operational', 'guardrail',
    ])

    content_matches = sum(1 for kw in operational_keywords if kw in content_lower)

    return title_match or content_matches >= 2


def is_agent_content(content: str, title: str) -> bool:
    """Check if content describes agent definitions or delegation patterns."""
    title_lower = title.lower()
    content_lower = content.lower()

    agent_keywords = [
        'sub-agent', 'subagent', 'agent type', 'agent model',
        'task-executor', 'code-reviewer', 'architecture-reviewer',
        'delegate to', 'delegation', 'orchestrator',
        'spawn agent', 'launch agent',
    ]

    title_match = any(kw in title_lower for kw in [
        'agent', 'delegation', 'orchestrat', 'sub-agent',
    ])

    content_matches = sum(1 for kw in agent_keywords if kw in content_lower)

    return title_match or content_matches >= 2


def has_code_examples(content: str) -> bool:
    """Check if content contains code examples (code blocks or inline code patterns)."""
    # Fenced code blocks
    if re.search(r'```\w*\n', content):
        return True
    # Multiple lines with "Good/Bad" patterns
    if re.search(r'(//\s*(Good|Bad|Wrong|Correct|Right)|✅|❌)', content):
        return True
    # Multiple inline code snippets suggesting patterns
    code_spans = re.findall(r'`[^`]+`', content)
    return len(code_spans) > 5


def classify_section(section: Section, project_name: str) -> Optional[ClassificationResult]:
    """Classify a section into the appropriate tier."""
    content_lower = section.content.lower()
    title_lower = section.title.lower()

    # Structural sections that should stay in CLAUDE.md
    structural_keywords = [
        'tech stack', 'technology', 'stack',
        'project structure', 'directory',
        'commands', 'scripts', 'how to run',
        'mcp server', 'installation',
        'skills', 'skill matrix',
        'references', 'documentation',
        'overview', 'description',
        'delegation', 'reference documentation',
    ]

    for keyword in structural_keywords:
        if keyword in title_lower:
            return ClassificationResult(
                section=section,
                tier=Tier.KEEP,
                reason=f"Structural/navigational section ('{keyword}')",
                target="CLAUDE.md (keep as-is)",
                priority='low'
            )

    # Already-compact "Code Standards" sections should stay
    if 'code standards' in title_lower or 'always active' in title_lower:
        return ClassificationResult(
            section=section,
            tier=Tier.KEEP,
            reason="Already a Tier 1 Code Standards section",
            target="CLAUDE.md (keep as-is)",
            priority='low'
        )

    # Mandatory Rules sections should stay in CLAUDE.md
    if 'mandatory' in title_lower and 'rule' in title_lower:
        return ClassificationResult(
            section=section,
            tier=Tier.KEEP,
            reason="Already a Mandatory Rules section",
            target="CLAUDE.md (keep as-is)",
            priority='low'
        )

    # Operational/safety rules → Mandatory Rules section in CLAUDE.md
    if is_operational_rule(section.content, section.title):
        return ClassificationResult(
            section=section,
            tier=Tier.MANDATORY,
            reason=f"Operational/safety rules ({section.line_count} lines)",
            target="CLAUDE.md Mandatory Rules section",
            priority='high',
            promotable_rules=extract_promotable_rules(section.content),
        )

    # Agent/delegation content → agent definitions
    if is_agent_content(section.content, section.title):
        return ClassificationResult(
            section=section,
            tier=Tier.AGENT,
            reason=f"Agent/delegation content ({section.line_count} lines, ~{section.token_estimate} tokens)",
            target="agents/ and CLAUDE.md Delegation section",
            priority='medium',
        )

    # Workflow/procedure content → Tier 3 (Skills)
    workflow_patterns = [
        r'step\s*\d+',
        r'(first|then|next|finally),?\s+(you|we|create|run|check)',
        r'workflow',
        r'procedure',
        r'deployment',
        r'release\s+process',
        r'how\s+to\s+(deploy|release|migrate|review)',
    ]

    workflow_score = 0
    for pattern in workflow_patterns:
        if re.search(pattern, content_lower):
            workflow_score += 1

    if workflow_score >= 2 or any(kw in title_lower for kw in ['workflow', 'procedure', 'deployment', 'release', 'how to']):
        skill_name = re.sub(r'[^\w\s]', '', title_lower).strip().replace(' ', '-')
        return ClassificationResult(
            section=section,
            tier=Tier.SKILL,
            reason=f"Contains step-by-step workflow/procedure ({section.line_count} lines, ~{section.token_estimate} tokens)",
            target=f"skills/{project_name}-{skill_name}/",
            priority='medium'
        )

    # Convention/pattern content → split between Tier 1.5 (rules) and Tier 2 (examples)
    convention_categories = {
        'code': (
            r'(convention|pattern|naming|import|export|class\s+structure|file\s+organization|code\s+style)',
            ['convention', 'pattern', 'naming', 'code style', 'backend', 'frontend', 'code'],
        ),
        'testing': (
            r'(test|testing|pytest|vitest|playwright|mock|coverage|fixture|faker)',
            ['test', 'testing', 'mock', 'coverage', 'fixture'],
        ),
        'api': (
            r'(api|endpoint|rest|http|status\s+code|request|response|route)',
            ['api', 'endpoint', 'rest', 'route'],
        ),
        'logging': (
            r'(log|logging|logger|structlog|monolog)',
            ['log', 'logging'],
        ),
        'database': (
            r'(database|sql|query|migration|schema|pragma|repository|doctrine|orm)',
            ['database', 'sql', 'query', 'migration', 'schema', 'repository'],
        ),
        'frontend': (
            r'(component|react|vue|state|props|css|tailwind|ui|form)',
            ['component', 'frontend', 'ui', 'react', 'vue'],
        ),
        'security': (
            r'(security|auth|authentication|authorization|permission|role)',
            ['security', 'auth', 'permission'],
        ),
    }

    for category, (regex, title_keywords) in convention_categories.items():
        title_match = any(kw in title_lower for kw in title_keywords)
        content_match = bool(re.search(regex, content_lower))

        if (title_match or content_match) and (section.line_count > 10 or section.token_estimate > 80):
            promotable = extract_promotable_rules(section.content)
            hard_constraints = extract_hard_constraints(section.content)
            has_examples = has_code_examples(section.content)
            priority = 'high' if section.line_count > 25 or section.token_estimate > 200 else 'medium'

            # Decide: rules file, examples file, or both
            if has_examples and hard_constraints:
                # Contains both constraints and examples → split
                return ClassificationResult(
                    section=section,
                    tier=Tier.EXAMPLE,
                    reason=f"Contains {category} patterns with code examples AND hard constraints — split into rules/{category}.md (constraints) + examples/{category}.md (patterns) ({section.line_count} lines, ~{section.token_estimate} tokens)",
                    target=f"rules/{category}.md + examples/{category}.md",
                    priority=priority,
                    promotable_rules=promotable,
                )
            elif has_examples:
                # Mostly patterns with examples → examples file
                return ClassificationResult(
                    section=section,
                    tier=Tier.EXAMPLE,
                    reason=f"Contains {category} patterns with code examples ({section.line_count} lines, ~{section.token_estimate} tokens)",
                    target=f"examples/{category}.md",
                    priority=priority,
                    promotable_rules=promotable,
                )
            elif hard_constraints:
                # Mostly binary constraints → rules file
                return ClassificationResult(
                    section=section,
                    tier=Tier.RULE,
                    reason=f"Contains {category} hard constraints ({section.line_count} lines, ~{section.token_estimate} tokens)",
                    target=f"rules/{category}.md",
                    priority=priority,
                    promotable_rules=promotable,
                )
            else:
                # Default: examples file (has enough content but no clear split)
                return ClassificationResult(
                    section=section,
                    tier=Tier.EXAMPLE,
                    reason=f"Contains {category} conventions/patterns ({section.line_count} lines, ~{section.token_estimate} tokens)",
                    target=f"examples/{category}.md",
                    priority=priority,
                    promotable_rules=promotable,
                )

    # Verbose sections that don't match a specific category
    if section.line_count > 25 or section.token_estimate > 200:
        promotable = extract_promotable_rules(section.content)
        hard_constraints = extract_hard_constraints(section.content)
        sanitized_title = re.sub(r'[^\w\s]', '', title_lower).strip().replace(' ', '-')

        if hard_constraints and not has_code_examples(section.content):
            return ClassificationResult(
                section=section,
                tier=Tier.RULE,
                reason=f"Verbose section with hard constraints ({section.line_count} lines, ~{section.token_estimate} tokens)",
                target=f"rules/{sanitized_title}.md",
                priority='medium',
                promotable_rules=promotable,
            )
        else:
            return ClassificationResult(
                section=section,
                tier=Tier.EXAMPLE,
                reason=f"Verbose section that could be extracted ({section.line_count} lines, ~{section.token_estimate} tokens)",
                target=f"examples/{sanitized_title}.md",
                priority='medium',
                promotable_rules=promotable,
            )

    # Short sections with convention-like content
    convention_signals = [
        r'always|never|must|should|do not|don\'t',
        r'use\s+\w+\s+for',
        r'pattern|convention',
    ]

    signal_count = sum(1 for p in convention_signals if re.search(p, content_lower))
    if signal_count >= 2 and section.line_count > 5:
        return ClassificationResult(
            section=section,
            tier=Tier.PROMOTE,
            reason=f"Contains rules that should be promoted to Code Standards ({section.line_count} lines)",
            target="CLAUDE.md Code Standards section",
            priority='high',
            promotable_rules=extract_promotable_rules(section.content),
        )

    return None


def generate_report(file_path: Path, results: List[ClassificationResult]) -> str:
    """Generate a markdown report of optimization suggestions."""
    if not results:
        return "CLAUDE.md is already well-optimized. No changes needed."

    content = file_path.read_text()
    total_tokens = len(content) // 4

    # Group by tier
    by_tier = {
        Tier.KEEP: [],
        Tier.MANDATORY: [],
        Tier.PROMOTE: [],
        Tier.RULE: [],
        Tier.EXAMPLE: [],
        Tier.SKILL: [],
        Tier.AGENT: [],
    }
    for r in results:
        by_tier[r.tier].append(r)

    extractable_tokens = sum(
        r.section.token_estimate
        for r in results
        if r.tier in (Tier.RULE, Tier.EXAMPLE, Tier.SKILL)
    )

    report = [
        "# CLAUDE.md Optimization Report",
        "",
        f"**File**: `{file_path}`",
        f"**Current size**: ~{total_tokens} tokens",
        f"**Extractable to Tier 1.5/2/3**: ~{extractable_tokens} tokens ({extractable_tokens * 100 // max(total_tokens, 1)}%)",
        "",
        "## Architecture: 4-Tier Classification",
        "",
        "| Tier | Location | Loading | Token Impact |",
        "|------|----------|---------|-------------|",
        "| Tier 1: CLAUDE.md | CLAUDE.md | Always | Every request |",
        "| Tier 1.5: Rules | `.claude/rules/` | Auto-loaded every session | Every request (but separate from CLAUDE.md) |",
        "| Tier 2: Examples | `.claude/examples/` | Read on demand | When relevant |",
        "| Tier 3: Skills | `.claude/skills/` | Invoked explicitly | When invoked |",
        "",
    ]

    # Tier 1: Keep sections
    if by_tier[Tier.KEEP]:
        report.append("## Tier 1: Keep in CLAUDE.md")
        report.append("")
        for r in by_tier[Tier.KEEP]:
            report.append(f"- **{r.section.title}** (line {r.section.line_start}) — {r.reason}")
        report.append("")

    # Tier 1: Mandatory Rules
    if by_tier[Tier.MANDATORY]:
        report.append("## Tier 1: Add to Mandatory Rules Section")
        report.append("")
        report.append("These sections contain operational/safety rules that should go in a dedicated MANDATORY RULES section in CLAUDE.md:")
        report.append("")
        for r in by_tier[Tier.MANDATORY]:
            report.append(f"### {r.section.title} (line {r.section.line_start})")
            report.append(f"  {r.reason}")
            if r.promotable_rules:
                report.append("  **Rules to include**:")
                for rule in r.promotable_rules:
                    report.append(f"  - {rule}")
            report.append("")

    # Tier 1: Promote to Code Standards
    if by_tier[Tier.PROMOTE]:
        report.append("## Tier 1: Promote to Code Standards (always active)")
        report.append("")
        report.append("These sections contain rules that should be compacted into one-liners in a 'Code Standards (always active)' section:")
        report.append("")
        for r in by_tier[Tier.PROMOTE]:
            report.append(f"### {r.section.title} (line {r.section.line_start})")
            report.append(f"  {r.reason}")
            if r.promotable_rules:
                report.append("  **Rules to promote (condense to one-liners)**:")
                for rule in r.promotable_rules:
                    report.append(f"  - {rule}")
            report.append("")

    # Tier 1.5: Rules files
    if by_tier[Tier.RULE]:
        report.append("## Tier 1.5: Extract to Rules Files (auto-loaded)")
        report.append("")
        report.append("Move these hard constraints to `.claude/rules/` — they'll be auto-loaded every session:")
        report.append("")

        for priority in ['high', 'medium', 'low']:
            priority_items = [r for r in by_tier[Tier.RULE] if r.priority == priority]
            if priority_items:
                icon = {'high': '[HIGH]', 'medium': '[MED]', 'low': '[LOW]'}[priority]
                for r in priority_items:
                    report.append(f"### {icon} {r.section.title} → `{r.target}`")
                    report.append(f"  {r.reason}")
                    report.append(f"  Lines: {r.section.line_start}-{r.section.line_start + r.section.line_count}")
                    if r.promotable_rules:
                        report.append("  **Hard constraints to extract**:")
                        for rule in r.promotable_rules:
                            report.append(f"  - {rule}")
                    report.append("")

    # Tier 2: Examples files
    if by_tier[Tier.EXAMPLE]:
        report.append("## Tier 2: Extract to Examples Files (on-demand)")
        report.append("")
        report.append("Move these detailed patterns to `.claude/examples/` as on-demand reference material:")
        report.append("")

        for priority in ['high', 'medium', 'low']:
            priority_items = [r for r in by_tier[Tier.EXAMPLE] if r.priority == priority]
            if priority_items:
                icon = {'high': '[HIGH]', 'medium': '[MED]', 'low': '[LOW]'}[priority]
                for r in priority_items:
                    report.append(f"### {icon} {r.section.title} → `{r.target}`")
                    report.append(f"  {r.reason}")
                    report.append(f"  Lines: {r.section.line_start}-{r.section.line_start + r.section.line_count}")
                    if r.promotable_rules:
                        report.append("  **Critical rules to also promote to Tier 1**:")
                        for rule in r.promotable_rules:
                            report.append(f"  - {rule}")
                    report.append("")

    # Tier 3: Skills
    if by_tier[Tier.SKILL]:
        report.append("## Tier 3: Create as Workflow Skills")
        report.append("")
        report.append("Convert these into interactive workflow skills in `.claude/skills/`:")
        report.append("")
        for r in by_tier[Tier.SKILL]:
            report.append(f"### {r.section.title} → `{r.target}`")
            report.append(f"  {r.reason}")
            report.append(f"  Lines: {r.section.line_start}-{r.section.line_start + r.section.line_count}")
            report.append("")

    # Agent definitions
    if by_tier[Tier.AGENT]:
        report.append("## Agent Definitions")
        report.append("")
        report.append("These sections describe agent/delegation patterns — consider creating `.claude/agents/` definitions:")
        report.append("")
        for r in by_tier[Tier.AGENT]:
            report.append(f"### {r.section.title} (line {r.section.line_start})")
            report.append(f"  {r.reason}")
            report.append("")

    # Recommended actions
    report.extend([
        "## Recommended Actions",
        "",
        "1. **Add Mandatory Rules section** to CLAUDE.md for operational/safety rules",
        "2. **Create Code Standards section** in CLAUDE.md with promoted rules as compact one-liners",
        "3. **Create `.claude/rules/` directory** with hard constraint files (auto-loaded):",
    ])

    rule_targets = set(r.target for r in by_tier[Tier.RULE])
    for target in sorted(rule_targets):
        report.append(f"   - `{target}`")

    report.extend([
        "4. **Create `.claude/examples/` directory** with detailed pattern files (on-demand):",
    ])

    example_targets = set(r.target for r in by_tier[Tier.EXAMPLE])
    for target in sorted(example_targets):
        report.append(f"   - `{target}`")

    report.extend([
        "5. **Create workflow skills** (if applicable):",
    ])

    skill_targets = set(r.target for r in by_tier[Tier.SKILL])
    for target in sorted(skill_targets):
        report.append(f"   - `{target}`")

    if by_tier[Tier.AGENT]:
        report.extend([
            "6. **Create `.claude/agents/` directory** with agent definitions",
            "7. **Add Delegation section** to CLAUDE.md with agent routing",
        ])
        next_step = 8
    else:
        next_step = 6

    report.extend([
        f"{next_step}. **Add cross-references**:",
        "   - Rules files: end with `## Reference` pointing to examples",
        "   - CLAUDE.md: add `## Reference Documentation` section at bottom",
    ])
    next_step += 1

    report.extend([
        f"{next_step}. **Remove extracted content** from CLAUDE.md",
    ])
    next_step += 1

    report.extend([
        f"{next_step}. **Verify structure**:",
        "   - `.claude/rules/` exists with auto-loaded constraints",
        "   - `.claude/examples/` exists with on-demand patterns",
        "   - Rules files have cross-references to examples",
        "   - CLAUDE.md has Mandatory Rules + Code Standards + Reference Documentation",
    ])

    if by_tier[Tier.AGENT]:
        report.append("   - Agent files have embedded guardrails")
        report.append("   - CLAUDE.md has Agents table and Delegation section")

    report.append("")

    return '\n'.join(report)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_claude_md.py <path-to-CLAUDE.md>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    if not file_path.name.endswith('.md'):
        print(f"Warning: Expected a .md file, got: {file_path.name}")

    # Determine project name from file path
    project_name = file_path.parent.name.lower().replace(' ', '-')
    if project_name == '.claude':
        project_name = file_path.parent.parent.name.lower().replace(' ', '-')

    print(f"Analyzing {file_path.name}...")
    print(f"Project: {project_name}")
    print()

    # Read and parse the file
    content = file_path.read_text()
    sections = parse_markdown_sections(content)

    # Classify sections
    results = []
    for section in sections:
        result = classify_section(section, project_name)
        if result:
            results.append(result)

    # Generate and print report
    report = generate_report(file_path, results)
    print(report)

    # Save report
    report_path = file_path.parent / 'CLAUDE_MD_OPTIMIZATION_REPORT.md'
    report_path.write_text(report)
    print()
    print(f"Full report saved to: {report_path}")


if __name__ == '__main__':
    main()
