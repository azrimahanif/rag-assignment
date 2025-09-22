import { MarkdownParser } from './markdownParser';
import type { StructuredResponse } from '../types';

export class ResponseAnalyzer {
  /**
   * Main entry point for analyzing and structuring agent responses
   */
  static analyzeResponse(content: string): StructuredResponse {
    // First, try to parse as markdown
    const parseResult = MarkdownParser.parseMarkdown(content);
    
    // If no meaningful structure found, try plain text fallback
    if (parseResult.sections.length === 0 || !parseResult.metadata.hasHeadings) {
      const fallbackResult = MarkdownParser.parsePlainText(content);
      return MarkdownParser.toStructuredResponse(fallbackResult.sections);
    }
    
    // Convert parsed sections to structured response
    return MarkdownParser.toStructuredResponse(parseResult.sections);
  }

  /**
   * Detect if content needs preprocessing
   */
  static needsPreprocessing(content: string): boolean {
    const hasMarkdown = /#{1,6}\s+/.test(content) || // Headings
                     /^[-*]\s+/.test(content) ||        // Bullet lists
                     /^\d+\.\s+/.test(content) ||        // Numbered lists
                     /\*\*.*?\*\*/.test(content) ||      // Bold
                     /\*.*?\*/.test(content) ||           // Italic
                     /\[.*?\]\(.*?\)/.test(content);     // Links

    return !hasMarkdown;
  }

  /**
   * Extract key insights from content
   */
  static extractInsights(content: string): string[] {
    const insights: string[] = [];
    const lines = content.split('\n');
    
    lines.forEach(line => {
      const trimmed = line.trim();
      
      // Look for insight keywords
      const insightKeywords = [
        'insight', 'summary', 'conclusion', 'finding', 'key', 'important',
        'notable', 'significant', 'trend', 'pattern', 'observation'
      ];
      
      const hasInsightKeyword = insightKeywords.some(keyword => 
        trimmed.toLowerCase().includes(keyword)
      );
      
      // Look for comparative language
      const hasComparative = /(more|less|higher|lower|greater|smaller|compared|versus|vs)/i.test(trimmed);
      
      // Look for percentage or number highlights
      const hasNumbers = /\d+%/i.test(trimmed) || /\d+(?:,\d+)*\s*(people|million|billion|thousand)/i.test(trimmed);
      
      if ((hasInsightKeyword || hasComparative || hasNumbers) && trimmed.length > 20) {
        insights.push(trimmed);
      }
    });
    
    return insights.slice(0, 5); // Limit to top 5 insights
  }

  /**
   * Detect data comparisons in content
   */
  static detectComparisons(content: string): Comparison[] {
    const comparisons: Comparison[] = [];
    const lines = content.split('\n');
    
    lines.forEach(line => {
      const trimmed = line.trim();
      
      // Look for vs, versus, compared to patterns
      const vsPattern = /(.+?)\s*(?:vs\.?|versus|compared to)\s*(.+)/i;
      const match = trimmed.match(vsPattern);
      
      if (match) {
        comparisons.push({
          item1: match[1].trim(),
          item2: match[2].trim(),
          fullText: trimmed,
          type: this.detectComparisonType(trimmed)
        });
      }
      
      // Look for side-by-side comparisons (Selangor: X, Kedah: Y)
      const sideBySidePattern = /(.+?):\s*([^,]+),\s*(.+?):\s*(.+)/i;
      const sideBySideMatch = trimmed.match(sideBySidePattern);
      
      if (sideBySideMatch) {
        comparisons.push({
          item1: sideBySideMatch[1].trim(),
          item2: sideBySideMatch[3].trim(),
          value1: sideBySideMatch[2].trim(),
          value2: sideBySideMatch[4].trim(),
          fullText: trimmed,
          type: 'side-by-side'
        });
      }
    });
    
    return comparisons;
  }

  /**
   * Detect comparison type
   */
  private static detectComparisonType(text: string): ComparisonType {
    const lower = text.toLowerCase();
    
    if (lower.includes('population') || lower.includes('people')) return 'demographic';
    if (lower.includes('percent') || lower.includes('%')) return 'percentage';
    if (lower.includes('age') || lower.includes('years')) return 'temporal';
    if (lower.includes('ethnic') || lower.includes('race')) return 'ethnic';
    if (lower.includes('gender') || lower.includes('male') || lower.includes('female')) return 'gender';
    
    return 'general';
  }

  /**
   * Extract statistics with context
   */
  static extractStatisticsWithContext(content: string): StatWithContext[] {
    const stats: StatWithContext[] = [];
    const lines = content.split('\n');
    
    lines.forEach((line, index) => {
      const trimmed = line.trim();
      
      // Match numbers with context
      const numberPatterns = [
        /(\d+(?:,\d+)*)\s*(people?|%|years?)/gi,
        /(\d+(?:\.\d+)*)\s*%/gi,
        /(\d+(?:,\d+)*)/g
      ];
      
      numberPatterns.forEach(pattern => {
        let match;
        while ((match = pattern.exec(trimmed)) !== null) {
          const value = match[1];
          const unit = match[2] || '';
          
          // Get context around the statistic
          const context = this.getStatisticContext(content, index);
          
          stats.push({
            value: value,
            unit: unit,
            context: context,
            line: trimmed,
            position: { line: index, column: match.index }
          });
        }
      });
    });
    
    return stats;
  }

  /**
   * Get context around a statistic
   */
  private static getStatisticContext(content: string, lineIndex: number): string {
    const lines = content.split('\n');
    const contextLines = [];
    
    // Include current line and adjacent lines
    for (let i = Math.max(0, lineIndex - 1); i <= Math.min(lines.length - 1, lineIndex + 1); i++) {
      contextLines.push(lines[i]);
    }
    
    return contextLines.join(' ').trim();
  }

  /**
   * Generate summary from content
   */
  static generateSummary(content: string): string {
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);
    
    if (sentences.length === 0) return content;
    
    // Extract key sentences based on importance indicators
    const importantSentences = sentences.filter(sentence => {
      const lower = sentence.toLowerCase();
      return (
        lower.includes('total') ||
        lower.includes('overall') ||
        lower.includes('summary') ||
        lower.includes('conclusion') ||
        lower.includes('key finding') ||
        /\d+/.test(sentence) // Contains numbers
      );
    });
    
    // If we have important sentences, use the first one
    if (importantSentences.length > 0) {
      return importantSentences[0].trim() + '.';
    }
    
    // Otherwise use the first sentence
    return sentences[0].trim() + '.';
  }

  /**
   * Detect data quality indicators
   */
  static assessDataQuality(content: string): DataQuality {
    const quality: DataQuality = {
      hasStructure: false,
      hasComparisons: false,
      hasStatistics: false,
      hasSources: false,
      hasInsights: false,
      score: 0
    };

    // Check for structure
    quality.hasStructure = /#{1,6}\s+/.test(content) || /^[-*]\s+/.test(content);
    
    // Check for comparisons
    quality.hasComparisons = /(vs\.?|versus|compared to|more|less|higher|lower)/i.test(content);
    
    // Check for statistics
    quality.hasStatistics = /\d+(?:,\d+)*\s*(people?|%|years?)/i.test(content);
    
    // Check for sources
    quality.hasSources = /source|reference|data from|dosm/i.test(content);
    
    // Check for insights
    quality.hasInsights = /(insight|finding|conclusion|summary|trend)/i.test(content);
    
    // Calculate score
    let score = 0;
    if (quality.hasStructure) score += 2;
    if (quality.hasComparisons) score += 2;
    if (quality.hasStatistics) score += 2;
    if (quality.hasSources) score += 1;
    if (quality.hasInsights) score += 1;
    
    quality.score = Math.min(8, score);
    
    return quality;
  }
}

// Supporting interfaces
export interface Comparison {
  item1: string;
  item2: string;
  value1?: string;
  value2?: string;
  fullText: string;
  type: ComparisonType;
}

export type ComparisonType = 'demographic' | 'percentage' | 'temporal' | 'ethnic' | 'gender' | 'general';

export interface StatWithContext {
  value: string;
  unit: string;
  context: string;
  line: string;
  position: { line: number; column: number };
}

export interface DataQuality {
  hasStructure: boolean;
  hasComparisons: boolean;
  hasStatistics: boolean;
  hasSources: boolean;
  hasInsights: boolean;
  score: number;
}