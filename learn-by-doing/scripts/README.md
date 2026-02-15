# LearnByDoing - Resource Enrichment Script

This script uses the Brave Search MCP to enrich learning paths with additional resources.

## Setup

1. Install the Brave Search MCP server:
```bash
npx -y @modelcontextprotocol/server-brave-search
```

2. Set your Brave API key:
```bash
export BRAVE_API_KEY="your-api-key-here"
```

3. Get a Brave API key from: https://brave.com/search/api/

## Usage

Run the enrichment script:

```bash
ts-node scripts/enrich-resources.ts cpp-systems-cpp20
```

This will:
1. Load the specified learning path
2. For each task, search for additional resources
3. Filter out tutorials and solutions
4. Add new resources to the JSON file

## Resource Filtering

The script automatically filters out:
- GitHub repositories (potential solutions)
- Tutorial sites (GeeksforGeeks, Tutorialspoint, etc.)
- Video platforms (YouTube)
- Q&A sites with complete solutions (Stack Overflow)
- URLs containing /tutorial, /example, /solution, etc.

Allowed sources include:
- Official documentation (cppreference.com, Microsoft Docs)
- Specifications and RFCs
- Reference manuals
- Language documentation

## Manual Resource Addition

To manually add resources, edit the JSON file directly:
`src/data/paths/cpp-systems-cpp20.json`

Each resource should have:
- title: Clear, descriptive title
- url: Direct link to the resource
- type: 'documentation' | 'reference' | 'article' | 'book'
- description: Brief explanation of what the resource covers
