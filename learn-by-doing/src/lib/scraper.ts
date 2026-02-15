import { Resource } from '@/types';

// Blocked domains that contain tutorials, solutions, or hand-holding content
const BLOCKED_DOMAINS = [
  'github.com', // Repositories with solutions
  'geeksforgeeks.org',
  'tutorialspoint.com',
  'javatpoint.com',
  'w3schools.com',
  'programiz.com',
  'codecademy.com',
  'udemy.com',
  'coursera.org',
  'youtube.com',
  'youtu.be',
  'stackoverflow.com', // Often has complete solutions
  'repl.it',
  'codepen.io',
  'codesandbox.io',
];

// Blocked URL patterns
const BLOCKED_PATTERNS = [
  '/tutorial',
  '/example',
  '/sample',
  '/solution',
  '/walkthrough',
  '/guide/',
  '/how-to',
  '/step-by-step',
  '/complete',
  '/full-example',
];

// Allowed domains (whitelist for documentation)
const ALLOWED_DOMAINS = [
  'en.cppreference.com',
  'cppreference.com',
  'learn.microsoft.com',
  'docs.microsoft.com',
  'cmake.org',
  'google.github.io',
  'redis.io',
  'man7.org',
  'datatracker.ietf.org',
  'isocpp.github.io',
  'openssl.org',
  'gcc.gnu.org',
  'clang.llvm.org',
  'llvm.org',
  'c++', // Pattern match
];

export function isResourceAllowed(url: string): boolean {
  try {
    const urlObj = new URL(url);
    const domain = urlObj.hostname.toLowerCase();
    const pathname = urlObj.pathname.toLowerCase();
    
    // Check if domain is explicitly allowed
    const isAllowedDomain = ALLOWED_DOMAINS.some(allowed => 
      domain.includes(allowed) || allowed.includes(domain)
    );
    
    if (isAllowedDomain) {
      return true;
    }
    
    // Check if domain is blocked
    const isBlockedDomain = BLOCKED_DOMAINS.some(blocked => 
      domain === blocked || domain.endsWith(`.${blocked}`)
    );
    
    if (isBlockedDomain) {
      return false;
    }
    
    // Check if URL contains blocked patterns
    const hasBlockedPattern = BLOCKED_PATTERNS.some(pattern => 
      pathname.includes(pattern)
    );
    
    if (hasBlockedPattern) {
      return false;
    }
    
    // Default to allowing documentation/reference sites
    return true;
  } catch {
    return false;
  }
}

export function filterResources(resources: Resource[]): Resource[] {
  return resources.filter(resource => isResourceAllowed(resource.url));
}

// Keywords to use in search queries to find good resources
export const SEARCH_KEYWORDS = {
  documentation: [
    'official documentation',
    'reference manual',
    'language specification',
    'API reference',
  ],
  blocked: [
    'tutorial',
    'example code',
    'sample project',
    'complete solution',
    'step by step',
    'walkthrough',
    'how to build',
  ],
};

// Build a search query that emphasizes documentation
export function buildSearchQuery(topic: string): string {
  const docTerms = SEARCH_KEYWORDS.documentation.join(' OR ');
  const blockedTerms = SEARCH_KEYWORDS.blocked.join(' -');
  
  return `${topic} (${docTerms}) -${blockedTerms}`;
}
