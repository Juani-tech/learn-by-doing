# Frontend Integration Requirements - LearnByDoing

**Document Purpose**: Requirements for integrating the Next.js frontend with the new Python/FastAPI backend.

**Backend Location**: `learn-by-doing-backend/` directory
**Backend API**: `http://localhost:8000/api/v1`

---

## 🎯 Overview

The frontend needs to integrate with a new agentic backend that generates custom learning paths using AI. Key changes needed:

1. **New "Generate Path" feature** - Allow users to create custom paths
2. **API integration** - Replace static JSON with backend API calls
3. **Generation UI** - Show progress during path generation (30-120 seconds)
4. **Display AI-generated paths** - Show metadata for AI-generated content

---

## 🔧 API Integration

### Base Configuration

```typescript
// lib/api.ts or services/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = {
  async generatePath(request: GeneratePathRequest): Promise<GeneratePathResponse> {
    const response = await fetch(`${API_URL}/api/v1/paths/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  },

  async getPath(pathId: string): Promise<PathDetail> {
    const response = await fetch(`${API_URL}/api/v1/paths/${pathId}`);
    if (!response.ok) throw new Error('Path not found');
    return response.json();
  },

  async getPathBySlug(slug: string): Promise<PathDetail> {
    const response = await fetch(`${API_URL}/api/v1/paths/slug/${slug}`);
    if (!response.ok) throw new Error('Path not found');
    return response.json();
  },

  async listPaths(filters?: PathFilters): Promise<PathListItem[]> {
    const params = new URLSearchParams();
    if (filters?.language) params.append('language', filters.language);
    if (filters?.area) params.append('area', filters.area);
    
    const response = await fetch(`${API_URL}/api/v1/paths?${params}`);
    return response.json();
  },
};
```

### TypeScript Types

Add to existing `types/index.ts`:

```typescript
// API Request/Response Types

export interface GeneratePathRequest {
  topic: string;
  context?: string;
  experience_level?: 'beginner' | 'intermediate' | 'advanced';
}

export interface GeneratePathResponse {
  pathId: string;
  path: LearningPath;
  metadata: GenerationMetadata;
}

export interface GenerationMetadata {
  iterationCount: number;
  qualityScore: number;
  generationTimeSeconds: number;
  approved: boolean;
  maxIterationsReached: boolean;
}

export interface PathListItem {
  id: string;
  slug: string;
  title: string;
  description: string;
  language?: string;
  area?: string;
  totalTasks: number;
  estimatedHours: number;
  qualityScore?: number;
  createdAt: string;
  isAIGenerated: boolean; // Computed from qualityScore presence
}

export interface PathDetail extends LearningPath {
  id: string;
  slug: string;
  metadata?: {
    generationTimestamp: string;
    topic: string;
    context?: string;
    experience_level: string;
    iteration_count: number;
    expert_feedback: any;
    quality_review: any;
  };
  qualityScore?: number;
  generationAttempts: number;
  createdAt: string;
  updatedAt?: string;
}

// Update existing LearningPath type
export interface LearningPath {
  id: string;
  title: string;
  description: string;
  version: string;
  language: string;
  area: string;
  prerequisites: string[];
  totalTasks: number;
  estimatedHours: number;
  phases: Phase[];
  isAIGenerated?: boolean; // Frontend-computed
  qualityScore?: number;   // For AI-generated paths
}
```

---

## 📱 New Pages/Features

### 1. Path Generation Page (`/generate`)

**Purpose**: Allow users to create custom learning paths

**Requirements**:

```typescript
// app/generate/page.tsx
export default function GeneratePathPage() {
  return (
    <div className="max-w-2xl mx-auto py-12">
      <h1 className="text-3xl font-bold mb-2">Generate Custom Path</h1>
      <p className="text-gray-600 mb-8">
        Tell us what you want to learn and our AI will create a personalized path.
      </p>
      
      <GeneratePathForm />
    </div>
  );
}
```

**Form Fields**:

1. **Topic** (required)
   - Text input
   - Placeholder: "e.g., Rust CLI tools, Docker fundamentals"
   - Label: "What do you want to learn?"

2. **Context/Goals** (optional)
   - Textarea
   - Placeholder: "e.g., Want to build system utilities, working on a web app"
   - Label: "What are your goals? (optional)"
   - Help text: "This helps us tailor the path to your needs"

3. **Experience Level** (optional, default: intermediate)
   - Select dropdown
   - Options: Beginner, Intermediate, Advanced
   - Label: "Your experience level"

**Form Validation**:
- Topic: Required, min 3 characters, max 100
- Context: Optional, max 500 characters
- Experience: Must be one of the three options

**Submit Button**:
- Text: "Generate Path"
- Loading state: "Generating..." with spinner
- Disabled while loading
- Estimate: "This may take 30-120 seconds"

### 2. Generation Progress Component

**Purpose**: Show real-time progress during path generation

**Display**:

```typescript
// components/GenerationProgress.tsx
interface GenerationProgressProps {
  isGenerating: boolean;
  estimatedTimeRemaining?: number;
}

// Shows:
// - Animated progress indicator
// - Current status: "Researching topic...", "Designing curriculum...", etc.
// - Elapsed time
// - Estimated time remaining
// - Cancel button (optional)
```

**Progress Steps** (shown sequentially):

1. 🔍 **Researching** - "Understanding {topic}..."
2. ✏️ **Designing** - "Creating learning structure..."
3. 👨‍💻 **Validating** - "Checking technical accuracy..."
4. ✅ **Reviewing** - "Final quality check..."
5. 🎉 **Complete** - "Your path is ready!"

**Implementation Notes**:
- Since backend doesn't stream progress, simulate with:
  - Step 1: 0-20% (first 10-20 seconds)
  - Step 2: 20-60% (next 30-40 seconds)
  - Step 3: 60-85% (next 20-30 seconds)
  - Step 4: 85-100% (final 10-20 seconds)
- Update progress bar every 2 seconds
- Show elapsed time counter

### 3. AI-Generated Path Badge

**Purpose**: Visually distinguish AI-generated paths from manual ones

**Design**:

```typescript
// components/AIGeneratedBadge.tsx
interface AIGeneratedBadgeProps {
  qualityScore: number;
  iterationCount: number;
}

// Shows:
// - "AI Generated" badge (golden/orange color)
// - Quality score: "Quality: 92%"
// - Iterations: "Refined 3 times"
// - Tooltip: "This path was generated by AI and validated by multiple expert agents"
```

**Placement**:
- Path card (PathCard.tsx)
- Path detail page header
- Task page (small badge)

**Visual Design**:
- Badge: `bg-orange-100 text-orange-800 border border-orange-200`
- Icon: Sparkles or Robot icon from lucide-react
- Size: Small badge on cards, medium on detail pages

### 4. Path Detail Enhancements

**Metadata Section** (add to path detail page):

```typescript
// Add to path detail page
{path.isAIGenerated && (
  <div className="bg-gray-50 rounded-lg p-4 mb-6">
    <h3 className="font-semibold mb-2 flex items-center gap-2">
      <Sparkles className="h-4 w-4" />
      Generation Details
    </h3>
    <div className="grid grid-cols-2 gap-4 text-sm">
      <div>
        <span className="text-gray-500">Quality Score:</span>
        <span className="ml-2 font-medium">{path.qualityScore}%</span>
      </div>
      <div>
        <span className="text-gray-500">Iterations:</span>
        <span className="ml-2 font-medium">{path.metadata?.iteration_count}</span>
      </div>
      <div>
        <span className="text-gray-500">Generated:</span>
        <span className="ml-2 font-medium">
          {new Date(path.createdAt).toLocaleDateString()}
        </span>
      </div>
    </div>
  </div>
)}
```

---

## 🔗 Integration Points

### 1. Landing Page (`/page.tsx`)

**Changes**:

1. Add "Generate Custom Path" button next to existing paths

```typescript
// Add to landing page
<div className="flex justify-between items-center mb-8">
  <h2 className="text-3xl font-bold">Learning Paths</h2>
  <Link
    href="/generate"
    className="bg-[#cc9543] text-white px-6 py-2 rounded-lg hover:bg-[#b88539] transition-colors"
  >
    Generate Custom Path
  </Link>
</div>
```

2. Update PathCard to show AI badge

```typescript
// In PathCard component
{path.isAIGenerated && (
  <div className="flex items-center gap-1 text-xs text-orange-600 mb-2">
    <Sparkles className="h-3 w-3" />
    <span>AI Generated ({path.qualityScore}% quality)</span>
  </div>
)}
```

### 2. Path Card Updates (`components/PathCard.tsx`)

**Props Update**:

```typescript
interface PathCardProps {
  path: PathListItem;  // Updated type
  completedCount: number;
}
```

**Visual Changes**:
- Show AI badge if `path.qualityScore` exists
- Different border style for AI paths: `border-orange-200`
- Hover effect: `hover:border-[#cc9543]`

### 3. Path Service Updates (`lib/paths.ts`)

**New Functions**:

```typescript
// Add to lib/paths.ts

export async function fetchPathFromAPI(pathId: string): Promise<LearningPath | null> {
  try {
    const response = await fetch(`${API_URL}/api/v1/paths/${pathId}`);
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export async function generateNewPath(
  request: GeneratePathRequest
): Promise<GeneratePathResponse> {
  const response = await fetch(`${API_URL}/api/v1/paths/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error('Failed to generate path');
  }
  
  return response.json();
}

export async function fetchAllPaths(): Promise<PathListItem[]> {
  const response = await fetch(`${API_URL}/api/v1/paths`);
  return response.json();
}
```

**Backward Compatibility**:
- Keep existing `getLearningPath` for static paths (C++, etc.)
- Add new `getPathFromAPI` for dynamic paths
- Update `getAllLearningPaths` to merge static + API paths

### 4. Path Detail Page (`app/paths/[id]/page.tsx`)

**Changes**:

1. Update to fetch from API if path not found locally

```typescript
// In PathPage component
const path = getLearningPath(pathId) || await fetchPathFromAPI(pathId);

if (!path) {
  // Try fetching from API
  const apiPath = await fetchPathFromAPI(pathId);
  if (apiPath) {
    // Use API path
  } else {
    // Show not found
  }
}
```

2. Add metadata section for AI-generated paths (see section above)

---

## 🎨 UI/UX Guidelines

### Loading States

**Generation Loading**:
- Full-screen overlay or modal
- Progress bar with steps
- Estimated time: "Usually takes 30-120 seconds"
- Cancel button (optional - requires backend support)

**Skeleton Loading**:
- Use while fetching path list
- Match PathCard layout
- 3-4 skeleton cards

### Error Handling

**API Errors**:
```typescript
// components/ErrorMessage.tsx
interface ErrorMessageProps {
  error: string;
  onRetry?: () => void;
}

// Display:
// - Red alert box
// - Error message
// - Retry button (if applicable)
// - Contact support link
```

**Network Errors**:
- "Unable to connect to generation service"
- Check backend is running
- Retry button

**Generation Errors**:
- "Failed to generate path after 5 attempts"
- Suggest trying different topic
- Show partial results if available

### Success States

**After Generation**:
- Redirect to `/paths/{pathId}`
- Show success toast: "Path generated successfully!"
- Confetti animation (optional)
- "Start Learning" button

---

## 🔒 Environment Configuration

Add to `.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Or production
# NEXT_PUBLIC_API_URL=https://api.learnbydoing.app
```

---

## 📊 State Management

### Local Storage (existing)
- Keep for progress tracking
- No changes needed

### New State (React Context or Zustand)

```typescript
// stores/pathGenerationStore.ts
interface PathGenerationState {
  isGenerating: boolean;
  progress: number;
  currentStep: string;
  generatedPathId: string | null;
  error: string | null;
  
  startGeneration: () => void;
  updateProgress: (progress: number, step: string) => void;
  completeGeneration: (pathId: string) => void;
  failGeneration: (error: string) => void;
  reset: () => void;
}
```

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] GeneratePathForm validation
- [ ] GenerationProgress component
- [ ] API client functions
- [ ] PathCard with AI badge

### Integration Tests
- [ ] Full generation flow
- [ ] API error handling
- [ ] Loading states
- [ ] Redirect after generation

### E2E Tests (Playwright/Cypress)
- [ ] Generate path for "Rust CLI tools"
- [ ] Generate path for "Docker fundamentals"
- [ ] View generated path
- [ ] Complete tasks in generated path

---

## 🚀 Implementation Priority

### Phase 1: Basic Integration
1. ✅ Add API client functions
2. ✅ Create Generate Path page with form
3. ✅ Add simple loading state
4. ✅ Display generated path

### Phase 2: Enhanced UX
1. ✅ Add GenerationProgress component with steps
2. ✅ Add AI-generated badges
3. ✅ Add metadata section to path detail
4. ✅ Improve error handling

### Phase 3: Polish
1. ✅ Add caching for API responses
2. ✅ Add optimistic UI updates
3. ✅ Add animations and transitions
4. ✅ Mobile responsiveness check

---

## 📞 Backend API Reference

**Base URL**: `http://localhost:8000/api/v1`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/paths/generate` | Generate new path |
| GET | `/paths` | List all paths |
| GET | `/paths/{id}` | Get path by ID |
| GET | `/paths/slug/{slug}` | Get path by slug |
| DELETE | `/paths/{id}` | Delete path |
| GET | `/health` | Health check |

### Response Times
- `POST /paths/generate`: 30-120 seconds
- All other endpoints: < 500ms

### Rate Limits
- Generate: 10 requests/hour per IP (configurable)
- Other endpoints: 100 requests/minute

---

## ❓ Open Questions for Frontend Dev

1. Should we allow users to rate/feedback on AI-generated paths?
2. Should generated paths be editable by users?
3. Should we show the expert feedback/quality review details?
4. Do we need a "Regenerate" button if quality is low?
5. Should we cache generated paths or fetch fresh each time?

---

## 📝 Notes

- Backend uses **synchronous** generation (30-120s response time)
- No WebSocket or Server-Sent Events currently
- All paths are saved to database immediately
- AI-generated paths have `qualityScore` field
- Static paths (C++) don't have `qualityScore`

---

**Ready for implementation!** Start with Phase 1 (basic integration) and iterate.
