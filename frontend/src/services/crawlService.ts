import { rawApi } from './apiClient';

interface CrawlRequest {
  url: string;
  max_depth?: number;
  max_pages?: number;
  generate_tests?: boolean;
}

interface CrawlResponse {
  status: string;
  pages_discovered: number;
  elements_found: number;
  tests_generated: number;
  site_map: PageInfo[];
  generated_files: string[];
}

interface PageInfo {
  url: string;
  title: string;
  elements_count: number;
  links_count: number;
}

export const crawlService = {
  async triggerCrawl(request: CrawlRequest): Promise<CrawlResponse> {
    const { data } = await rawApi.post<CrawlResponse>('/crawl', request);
    return data;
  },
};

export type { CrawlRequest, CrawlResponse, PageInfo };
