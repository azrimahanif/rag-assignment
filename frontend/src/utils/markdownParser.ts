import type { ParsedSection, ParseResult, StructuredResponse } from '../types';

export class MarkdownParser {
  /**
   * Parse markdown text into structured sections
   */
  static parseMarkdown(text: string): ParseResult {
    const lines = text.split('\n');
    const sections: ParsedSection[] = [];
    let currentSection: ParsedSection | null = null;
    let currentLevel = 0;

    // Metadata tracking
    const metadata = {
      hasMarkdown: false,
      hasLists: false,
      hasHeadings: false,
      totalSections: 0
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Skip empty lines but preserve section breaks
      if (line === '') continue;

      // Detect headings
      const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
      if (headingMatch) {
        metadata.hasHeadings = true;
        metadata.hasMarkdown = true;
        
        const level = headingMatch[1].length;
        const title = headingMatch[2];
        
        // Create new section
        const newSection: ParsedSection = {
          type: this.categorizeSection(title),
          title: title,
          content: '',
          level: level
        };
        
        // Handle nested sections
        if (currentSection && level > currentLevel) {
          if (!currentSection.subsections) {
            currentSection.subsections = [];
          }
          currentSection.subsections.push(newSection);
          currentSection = newSection;
        } else {
          sections.push(newSection);
          currentSection = newSection;
          currentLevel = level;
        }
        
        metadata.totalSections++;
        continue;
      }

      // Detect lists
      const listMatch = line.match(/^([-*]|\d+\.)\s+(.+)$/);
      if (listMatch) {
        metadata.hasLists = true;
        metadata.hasMarkdown = true;
      }

      // Add content to current section
      if (currentSection) {
        if (currentSection.content) {
          currentSection.content += '\n' + line;
        } else {
          currentSection.content = line;
        }
      } else if (line) {
        // Create default section for content before first heading
        const defaultSection: ParsedSection = {
          type: 'overview',
          title: 'Overview',
          content: line,
          level: 1
        };
        sections.push(defaultSection);
        currentSection = defaultSection;
        metadata.totalSections++;
      }
    }

    return { sections, metadata };
  }

  /**
   * Categorize section based on title keywords
   */
  private static categorizeSection(title: string): string {
    const lowerTitle = title.toLowerCase();
    
    if (lowerTitle.includes('overview') || lowerTitle.includes('summary')) return 'overview';
    if (lowerTitle.includes('key finding') || lowerTitle.includes('finding')) return 'keyFindings';
    if (lowerTitle.includes('how to') || lowerTitle.includes('guide')) return 'howTo';
    if (lowerTitle.includes('coverage') || lowerTitle.includes('applicability')) return 'coverage';
    if (lowerTitle.includes('limitation')) return 'limitations';
    if (lowerTitle.includes('dataset') || lowerTitle.includes('data info')) return 'datasetInfo';
    if (lowerTitle.includes('reference') || lowerTitle.includes('source')) return 'references';
    if (lowerTitle.includes('total population') || lowerTitle.includes('gender') || 
        lowerTitle.includes('age') || lowerTitle.includes('ethnic')) return 'comparison';
    
    return 'custom';
  }

  /**
   * Convert parsed sections to structured response
   */
  static toStructuredResponse(sections: ParsedSection[]): StructuredResponse {
    const response: StructuredResponse = {};

    sections.forEach(section => {
      switch (section.type) {
        case 'overview':
          response.overview = {
            title: section.title,
            content: section.content,
            keyStats: this.extractStatistics(section.content)
          };
          break;
        case 'keyFindings':
          response.keyFindings = {
            title: section.title,
            findings: this.extractFindings(section.content)
          };
          break;
        case 'howTo':
          response.howToUse = {
            title: section.title,
            steps: this.extractHowToSteps(section.content)
          };
          break;
        case 'coverage':
          response.coverage = {
            title: section.title,
            coverage: this.extractListItems(section.content)
          };
          break;
        case 'limitations':
          response.limitations = {
            title: section.title,
            limitations: this.extractListItems(section.content)
          };
          break;
        case 'datasetInfo':
          response.datasetInfo = {
            title: section.title,
            info: this.extractDatasetInfo(section.content)
          };
          break;
        case 'references':
          response.references = {
            title: section.title,
            sources: this.extractReferences(section.content)
          };
          break;
        case 'comparison':
        case 'custom':
          if (!response.customSections) response.customSections = [];
          response.customSections.push({
            title: section.title,
            content: section.content,
            type: section.type === 'comparison' ? 'comparison' : 'text',
            items: this.extractListItems(section.content)
          });
          break;
      }
    });

    return response;
  }

  /**
   * Extract statistics from text content
   */
  private static extractStatistics(content: string) {
    const stats = [];
    const statRegex = /(\d+(?:,\d+)*)\s*(people?|%|years?)/gi;
    let match;
    
    while ((match = statRegex.exec(content)) !== null) {
      stats.push({
        label: match[0],
        value: match[1],
        unit: match[2],
        highlighted: true
      });
    }
    
    return stats;
  }

  /**
   * Extract findings from content
   */
  private static extractFindings(content: string) {
    const findings = [];
    const lines = content.split('\n');
    
    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
        const content = trimmed.replace(/^[-*]\s*/, '');
        findings.push({
          content: content,
          type: 'insight',
          icon: this.getIconForContent(content)
        });
      }
    });
    
    return findings;
  }

  /**
   * Extract how-to steps from content
   */
  private static extractHowToSteps(content: string) {
    const steps = [];
    const lines = content.split('\n');
    let stepNumber = 1;
    
    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.match(/^\d+\./) || trimmed.startsWith('-') || trimmed.startsWith('*')) {
        const content = trimmed.replace(/^\d+\.\s*|^[-*]\s*/, '');
        steps.push({
          step: stepNumber++,
          title: content.split(':')[0],
          description: content.includes(':') ? content.split(':')[1] : content
        });
      }
    });
    
    return steps;
  }

  /**
   * Extract list items from content
   */
  private static extractListItems(content: string): string[] {
    const items = [];
    const lines = content.split('\n');
    
    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('-') || trimmed.startsWith('*') || trimmed.match(/^\d+\./)) {
        items.push(trimmed.replace(/^[-*\d.]\s*/, ''));
      }
    });
    
    return items.length > 0 ? items : [content];
  }

  /**
   * Extract dataset information
   */
  private static extractDatasetInfo(content: string) {
    const info = [];
    const lines = content.split('\n');
    
    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.includes(':')) {
        const [label, value] = trimmed.split(':').map(s => s.trim());
        info.push({ label, value, type: 'text' });
      }
    });
    
    return info;
  }

  /**
   * Extract references from content
   */
  private static extractReferences(content: string) {
    const sources = [];
    const lines = content.split('\n');
    
    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.toLowerCase().includes('source:') || trimmed.toLowerCase().includes('reference:')) {
        const content = trimmed.replace(/^source:\s*/i, '').replace(/^reference:\s*/i, '');
        sources.push({
          title: content,
          type: 'dataset'
        });
      }
    });
    
    return sources;
  }

  /**
   * Get appropriate icon for content type
   */
  private static getIconForContent(content: string): string {
    const lower = content.toLowerCase();
    if (lower.includes('population') || lower.includes('people')) return '👥';
    if (lower.includes('percent') || lower.includes('%')) return '📊';
    if (lower.includes('increase') || lower.includes('decrease')) return '📈';
    if (lower.includes('divers') || lower.includes('ethnic')) return '🌍';
    return '✅';
  }

  /**
   * Preprocess plain text to add markdown structure
   */
  static preprocessPlainText(text: string): string {
    let processed = text;
    
    // Add double line breaks for paragraphs
    processed = processed.replace(/\n\n/g, '\n\n');
    
    // Convert standalone lines that look like headings
    processed = processed.replace(/^([A-Z][A-Za-z\s]+)$/gm, '## $1');
    
    // Convert lines with dashes to lists
    processed = processed.replace(/^[\s]*-[\s]+(.+)$/gm, '- $1');
    
    return processed;
  }

  /**
   * Fallback parser for non-markdown content
   */
  static parsePlainText(text: string): ParseResult {
    const processed = this.preprocessPlainText(text);
    return this.parseMarkdown(processed);
  }

  /**
   * Render markdown with custom components (moved to component file)
   */
  static renderMarkdown(content: string): string {
    // This should be implemented in a React component file
    // For now, return the content as-is
    return content;
  }
}

/**
 * Parse structured response from markdown content
 */
export function parseStructuredResponse(content: string): StructuredResponse {
  const { sections } = MarkdownParser.parseMarkdown(content);
  return MarkdownParser.toStructuredResponse(sections);
}