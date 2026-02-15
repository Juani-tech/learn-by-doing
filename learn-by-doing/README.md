# LearnByDoing

A hands-on learning platform for programmers. No hand-holding. No copy-paste tutorials. Just clear requirements, curated resources, and challenging projects that build real skills.

## Philosophy

LearnByDoing follows these core principles:

- **Bottom-up learning**: Start with core concepts, build complexity gradually
- **Zero hand-holding**: Requirements only, no hints or solutions shown
- **Fast-paced**: No repetition unless constructing something more sophisticated
- **Hands-on only**: Every concept must be applied immediately through projects
- **Curated resources**: Documentation and references only, filtered tutorials

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/learn-by-doing.git
cd learn-by-doing
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Learning Paths

### C++ Systems Programming (C++20)

A comprehensive path taking you from C++ fundamentals to building production-ready systems:

**Phase 1: Foundations** (4 tasks)
- Development environment setup
- Memory fundamentals
- Pointers & references
- RAII principle

**Phase 2: Language Core** (6 tasks)
- Classes & OOP
- Templates
- Smart pointers
- STL containers
- Error handling
- Move semantics

**Phase 3: Systems Programming** (6 tasks)
- File I/O & filesystem
- Network programming
- Advanced memory management
- Concurrency
- Async programming
- Build systems (CMake)

**Phase 4: Production** (4 tasks)
- Modern C++20 features (concepts, ranges, coroutines)
- Testing (Google Test)
- Performance optimization
- Capstone: Key-value store

**Total**: 20 tasks, ~120 hours

## How to Use

1. **Choose a path**: Select a learning path that matches your goals
2. **Start with Phase 1**: Begin with the foundational tasks
3. **Read requirements**: Each task lists clear requirements and acceptance criteria
4. **Study resources**: Use the curated documentation links (no tutorials!)
5. **Build**: Implement the requirements yourself
6. **Mark complete**: When you meet all acceptance criteria, mark the task complete
7. **Move on**: Proceed to the next task - no review, no repetition

## Task Structure

Each task includes:
- **Title**: Clear, action-oriented name
- **Description**: Brief overview of what you'll learn
- **Difficulty**: 1-5 scale (dots)
- **Estimated Time**: Hours to completion
- **Requirements**: Bullet list of what to build
- **Acceptance Criteria**: How to verify your solution
- **Resources**: Curated documentation links
- **Prerequisites**: Tasks that should be completed first

## Progress Tracking

Progress is automatically saved to your browser's localStorage:
- Completed tasks are tracked
- Current task position is remembered
- Progress percentage is calculated

## Resource Filtering

We carefully curate resources to ensure they:
- ✅ Are official documentation
- ✅ Are language/API references
- ✅ Are specifications
- ❌ Are NOT tutorials with solutions
- ❌ Are NOT step-by-step guides
- ❌ Are NOT example code repositories

Blocked domains include:
- GitHub (potential solutions)
- Tutorial sites (GeeksforGeeks, Tutorialspoint, etc.)
- Video platforms (YouTube)
- Q&A sites with complete solutions

## Adding New Learning Paths

To add a new learning path:

1. Create a JSON file in `src/data/paths/`:
```json
{
  "id": "your-path-id",
  "title": "Path Title",
  "description": "Path description",
  "version": "1.0",
  "language": "Language Name",
  "area": "Specialization Area",
  "prerequisites": [],
  "totalTasks": 10,
  "estimatedHours": 60,
  "phases": [
    {
      "id": "phase-1",
      "title": "Phase 1 Title",
      "description": "Phase description",
      "order": 1,
      "tasks": [
        {
          "id": "task-id",
          "phaseId": "phase-1",
          "title": "Task Title",
          "description": "Task description",
          "difficulty": 3,
          "estimatedHours": 4,
          "requirements": ["Requirement 1", "Requirement 2"],
          "acceptanceCriteria": ["Criteria 1", "Criteria 2"],
          "prerequisites": [],
          "resources": [
            {
              "title": "Resource Title",
              "url": "https://example.com/docs",
              "type": "documentation",
              "description": "Resource description"
            }
          ]
        }
      ]
    }
  ]
}
```

2. Register the path in `src/lib/paths.ts`

3. The path will automatically appear on the homepage

## Resource Enrichment

To automatically find additional resources using Brave Search:

1. Get a Brave API key: https://brave.com/search/api/

2. Set the environment variable:
```bash
export BRAVE_API_KEY="your-api-key"
```

3. Run the enrichment script:
```bash
npx ts-node scripts/enrich-resources.ts cpp-systems-cpp20
```

## Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Icons**: Lucide React
- **State**: localStorage
- **Build**: Static site generation

## Contributing

Contributions are welcome! Areas for contribution:
- New learning paths
- Additional tasks
- Resource improvements
- UI/UX enhancements
- Bug fixes

## License

MIT License - feel free to use this for your own learning or teaching!

## Inspiration

This project is heavily inspired by [The Odin Project](https://www.theodinproject.com/), which shares our philosophy of hands-on, self-directed learning.

## Roadmap

- [ ] Add more learning paths (Rust, Go, Python, etc.)
- [ ] User authentication for cross-device progress
- [ ] Task discussion forums
- [ ] Progress sharing
- [ ] Code submission system
- [ ] Achievement badges
- [ ] Dark mode

---

**Happy learning! Remember: The best way to learn programming is by programming.**
