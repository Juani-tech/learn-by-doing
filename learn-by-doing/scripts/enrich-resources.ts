import { LearningPath, Task, Resource } from '../src/types';
import { filterResources } from '../src/lib/scraper';
import * as fs from 'fs';
import * as path from 'path';

// Mock MCP client for demonstration
// In production, this would use the actual MCP SDK
class MockMCPClient {
  async search(query: string, count: number = 5): Promise<any[]> {
    console.log(`[MOCK] Searching: ${query}`);
    // Return empty results for now
    return [];
  }
}

async function enrichTask(task: Task, client: MockMCPClient): Promise<Resource[]> {
  const searchQuery = `${task.title} C++20 site:cppreference.com OR site:en.cppreference.com`;
  
  try {
    const results = await client.search(searchQuery, 3);
    
    const newResources: Resource[] = results.map((result: any) => ({
      title: result.title,
      url: result.url,
      type: 'reference',
      description: result.description || `Documentation for ${task.title}`,
    }));
    
    // Filter out blocked resources
    const filteredResources = filterResources(newResources);
    
    // Remove duplicates
    const existingUrls = new Set(task.resources.map(r => r.url));
    const uniqueResources = filteredResources.filter(
      r => !existingUrls.has(r.url)
    );
    
    return uniqueResources;
  } catch (error) {
    console.error(`Error enriching task ${task.id}:`, error);
    return [];
  }
}

async function enrichLearningPath(pathId: string) {
  const client = new MockMCPClient();
  
  // Load the learning path
  const dataPath = path.join(__dirname, '../src/data/paths', `${pathId}.json`);
  const pathData: LearningPath = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
  
  console.log(`Enriching learning path: ${pathData.title}`);
  console.log(`Total tasks: ${pathData.totalTasks}`);
  
  let enrichedCount = 0;
  
  // Enrich each task
  for (const phase of pathData.phases) {
    console.log(`\nPhase: ${phase.title}`);
    
    for (const task of phase.tasks) {
      console.log(`  Processing: ${task.title}`);
      
      const newResources = await enrichTask(task, client);
      
      if (newResources.length > 0) {
        task.resources.push(...newResources);
        enrichedCount += newResources.length;
        console.log(`    Added ${newResources.length} new resources`);
      }
    }
  }
  
  // Save updated data
  fs.writeFileSync(dataPath, JSON.stringify(pathData, null, 2));
  
  console.log(`\n✓ Enrichment complete!`);
  console.log(`Added ${enrichedCount} new resources`);
}

// Run if called directly
if (require.main === module) {
  const pathId = process.argv[2] || 'cpp-systems-cpp20';
  enrichLearningPath(pathId).catch(console.error);
}

export { enrichLearningPath };
