# Context Metadata Format

## Schema

The file `.automaker/context/context-metadata.json` stores descriptions for each context file:

```json
{
  "files": {
    "<filename>": {
      "description": "<string describing the file's purpose>"
    }
  }
}
```

## How Descriptions Are Used

When `loadContextFiles()` builds the prompt, each file is presented as:

```
## <filename>
**Path:** `.automaker/context/<filename>`
**Purpose:** <description from metadata>

<file content>
```

The description helps agents understand a file's relevance before reading its full content.

## Writing Effective Descriptions

### Good Descriptions

Specific, action-oriented, explain what the agent gains from the file:

```json
{
  "files": {
    "CLAUDE.md": {
      "description": "Primary project instructions including tech stack, directory structure, coding conventions, and critical constraints that must be followed"
    },
    "API_CONVENTIONS.md": {
      "description": "REST API design rules: route naming, request validation with Zod, response shapes, error codes, and authentication middleware patterns"
    },
    "TESTING.md": {
      "description": "Test framework configuration, fixture patterns, mock strategies, and coverage requirements for unit and integration tests"
    }
  }
}
```

### Bad Descriptions

Vague, unhelpful, or redundant with the filename:

```json
{
  "files": {
    "CLAUDE.md": {
      "description": "Project context"
    },
    "API_CONVENTIONS.md": {
      "description": "API conventions"
    },
    "TESTING.md": {
      "description": "Testing information"
    }
  }
}
```

## Best Practices

- Include key topics covered (helps agent decide relevance)
- Mention specific tools, libraries, or patterns referenced in the file
- Keep descriptions to one sentence (50-100 words)
- Update descriptions when file content changes significantly
- Include descriptions for ALL files in the context directory
- Missing descriptions result in the file being loaded without context about its purpose
