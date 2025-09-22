import React, { useState, useEffect } from 'react';
import { convertUrlToPng, needsPngConversion, decodeUrlIfNeeded, generateChartFilename, downloadImageAsPng } from '../lib/utils';
import { Download } from 'lucide-react';
import type { ChartData } from '../types';

// Function to detect and extract JSON chart configurations
const extractJsonChartConfigs = (content: string): Array<{ config: any; startIndex: number; endIndex: number; title?: string }> => {
  const jsonCharts: Array<{ config: any; startIndex: number; endIndex: number; title?: string }> = [];

  // Look for JSON objects that contain chart-related keywords
  const chartKeywords = ['type', 'data', 'labels', 'datasets'];
  const chartTypes = ['bar', 'line', 'pie', 'doughnut', 'scatter', 'radar', 'polarArea', 'bubble'];

  // Find all potential JSON objects in the text
  // This pattern handles nested braces properly
  const jsonPattern = /\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}/g;
  let match;

  while ((match = jsonPattern.exec(content)) !== null) {
    try {
      const configStr = match[0];
      const config = JSON.parse(configStr);

      // Skip JSON that's part of a URL (like in QuickChart parameters)
      const beforeText = content.substring(0, match.index);
      const afterText = content.substring(match.index + match[0].length);
      const surroundingText = beforeText + afterText;

      // Check if this JSON is within a URL context - more comprehensive check
      const urlIndicators = [
        'quickchart.io/chart?',
        '?c=',
        '&c=',
        'chart?',
        'https://',
        'http://',
        '.io/chart?',
        'width=',
        'height=',
        'format='
      ];

      const isWithinUrl = urlIndicators.some(indicator =>
        surroundingText.includes(indicator) ||
        beforeText.includes(indicator) ||
        afterText.includes(indicator)
      );

      // Additional check: if JSON contains URL-encoded characters, it's likely part of a URL
      const hasUrlEncodedChars = /%[0-9A-Fa-f]{2}/.test(match[0]);

      if (isWithinUrl || hasUrlEncodedChars) {
        continue;
      }

      // Check if this looks like a valid chart configuration
      if (isValidChartConfig(config)) {
        // Try to extract title from surrounding context
        const titleMatch = beforeText.match(/(?:chart|graph|visualization)[^.\n]*[:\-]?\s*([^\n]+)/i);
        const title = titleMatch ? titleMatch[1].trim() : undefined;

        jsonCharts.push({
          config,
          startIndex: match.index,
          endIndex: match.index + match[0].length,
          title
        });
      }
    } catch (error) {
      // Invalid JSON, skip this match
      continue;
    }
  }

  // Remove overlapping matches and sort by start index
  return jsonCharts
    .sort((a, b) => a.startIndex - b.startIndex)
    .filter((chart, index, array) => {
      if (index === 0) return true;
      return chart.startIndex >= array[index - 1].endIndex;
    });
};

// Check if a parsed JSON object looks like a valid chart configuration
const isValidChartConfig = (config: any): boolean => {
  if (!config || typeof config !== 'object') return false;

  // Must have either type or data
  if (!config.type && !config.data) return false;

  // If it has type, it should be a valid chart type
  if (config.type && !['bar', 'line', 'pie', 'doughnut', 'scatter', 'radar', 'polarArea', 'bubble'].includes(config.type)) {
    return false;
  }

  // If it has data, it should have labels and datasets
  if (config.data) {
    if (!config.data.labels || !Array.isArray(config.data.labels)) return false;
    if (!config.data.datasets || !Array.isArray(config.data.datasets)) return false;

    // At least one dataset should have data
    const hasValidDataset = config.data.datasets.some((dataset: any) =>
      dataset.data && Array.isArray(dataset.data)
    );

    if (!hasValidDataset) return false;
  }

  return true;
};

// Convert chart configuration to QuickChart URL
const convertChartConfigToUrl = (config: any, title?: string): string => {
  // Create a clean chart configuration
  const chartConfig = {
    type: config.type || 'bar',
    data: config.data,
    options: {
      responsive: true,
      plugins: {
        title: {
          display: !!title,
          text: title || 'Chart'
        },
        legend: {
          display: true,
          position: 'top'
        }
      },
      ...config.options
    }
  };

  // Convert to JSON and URL encode
  const configJson = JSON.stringify(chartConfig);
  const encodedConfig = encodeURIComponent(configJson);

  return `https://quickchart.io/chart?c=${encodedConfig}`;
};

// Convert n8n multi-parameter QuickChart URL to standard format
const convertN8nToStandardQuickChartUrl = (n8nUrl: string): string => {
  try {
    const url = new URL(n8nUrl);
    const params = url.searchParams;

    // Extract parameters
    const type = params.get('type') || 'bar';
    const dataStr = params.get('data');
    const optionsStr = params.get('options');

    // Build standard chart configuration
    const chartConfig: any = {
      type: type
    };

    // Parse and add data if present
    if (dataStr) {
      try {
        chartConfig.data = JSON.parse(decodeURIComponent(dataStr));
      } catch (e) {
        console.warn('Failed to parse data parameter:', e);
        chartConfig.data = { labels: [], datasets: [] };
      }
    }

    // Parse and add options if present
    if (optionsStr) {
      try {
        chartConfig.options = JSON.parse(decodeURIComponent(optionsStr));
      } catch (e) {
        console.warn('Failed to parse options parameter:', e);
        chartConfig.options = {};
      }
    }

    // Convert to standard QuickChart URL format
    const configJson = JSON.stringify(chartConfig);
    const encodedConfig = encodeURIComponent(configJson);
    return `https://quickchart.io/chart?c=${encodedConfig}`;
  } catch (error) {
    console.error('Failed to convert n8n URL to standard format:', error);
    // Return original URL as fallback
    return n8nUrl;
  }
};

// Utility function to detect if a string is URL-encoded
const isUrlEncoded = (str: string): boolean => {
  try {
    // URL-encoded strings contain % followed by hex digits
    return str.includes('%') && /%[0-9A-Fa-f]{2}/.test(str);
  } catch {
    return false;
  }
};

// Utility function to validate JSON structure
const isValidJson = (str: string): boolean => {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
};

// Utility function to safely decode URL-encoded JSON
const safelyDecodeUrlJson = (encodedStr: string): string => {
  try {
    if (!isUrlEncoded(encodedStr)) {
      return encodedStr; // Not encoded, return as-is
    }

    // Try single decoding first
    const decodedOnce = decodeURIComponent(encodedStr);

    // Check if it's valid JSON after single decode
    if (isValidJson(decodedOnce)) {
      return decodedOnce;
    }

    // Try double decoding (rare case)
    const decodedTwice = decodeURIComponent(decodedOnce);
    if (isValidJson(decodedTwice)) {
      return decodedTwice;
    }

    // If neither produces valid JSON, return original
    console.warn('URL-encoded JSON did not produce valid JSON after decoding');
    return encodedStr;
  } catch (error) {
    console.warn('Failed to decode URL-encoded JSON:', error);
    return encodedStr; // Return original on error
  }
};

// Utility function to extract title from chart configuration
const extractTitleFromChartConfig = (configJson: string): string | null => {
  try {
    const config = JSON.parse(configJson);
    return config?.options?.plugins?.title?.text || null;
  } catch {
    return null;
  }
};

// Validate QuickChart URL has required parameters
const isValidQuickChartUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);

    // Must have 'c' parameter for chart configuration
    const configParam = urlObj.searchParams.get('c');
    if (!configParam) {
      return false;
    }

    // For QuickChart URLs, validate the config parameter contains valid JSON
    try {
      const decodedConfig = safelyDecodeUrlJson(configParam);
      JSON.parse(decodedConfig);
      return true;
    } catch {
      return false;
    }
  } catch {
    return false;
  }
};

// Normalize QuickChart URL by ensuring proper parameter order and encoding
const normalizeQuickChartUrl = (url: string): string => {
  try {
    const urlObj = new URL(url);
    const params = urlObj.searchParams;

    // Extract the 'c' parameter (chart configuration)
    const configParam = params.get('c');

    if (!configParam) {
      // If no 'c' parameter, return original URL
      return url;
    }

    // Handle URL-encoded JSON in config parameter
    let finalConfigParam = configParam;
    if (isUrlEncoded(configParam)) {
      finalConfigParam = safelyDecodeUrlJson(configParam);
          }

    // Build URL manually to avoid double-encoding the JSON config
    const baseUrl = 'https://quickchart.io/chart';

    // Create query parameters for non-JSON parameters
    const queryParams = new URLSearchParams();
    queryParams.set('format', 'png');

    // Add width/height if present
    const width = params.get('width');
    const height = params.get('height');

    if (width) {
      queryParams.set('width', width);
    }

    if (height) {
      queryParams.set('height', height);
    }

    // Manually construct the query string with clean JSON (no double-encoding)
    const queryString = `c=${finalConfigParam}&${queryParams.toString()}`;
    return `${baseUrl}?${queryString}`;
  } catch (error) {
    console.error('Failed to normalize QuickChart URL:', error);
    return url; // Return original URL as fallback
  }
};

// Early detection function to check if content likely contains charts
const contentLikelyContainsCharts = (content: string): boolean => {
  const chartKeywords = [
    '![', 'chart', 'graph', 'visualization', 'plot',
    'quickchart.io', '{"type":', '{"data":', '{"labels":',
    'https://', 'http://'  // Include URLs for bare link detection
  ];

  const lowerContent = content.toLowerCase();
  return chartKeywords.some(keyword => lowerContent.includes(keyword.toLowerCase()));
};

export const parseChartsFromContent = (content: string): { text: string; charts: ChartData[] } => {
  const charts: ChartData[] = [];
  let processedText = content;

  // Track processed URLs to prevent duplicates
  const processedUrls = new Set<string>();

  // Early exit if no chart indicators found (performance optimization)
  if (!contentLikelyContainsCharts(content)) {
    return {
      text: processedText,
      charts: []
    };
  }

  // First, handle JSON chart configurations
  const jsonCharts = extractJsonChartConfigs(content);

  // Process JSON charts (in reverse order to maintain indices)
  for (let i = jsonCharts.length - 1; i >= 0; i--) {
    const jsonChart = jsonCharts[i];
    const url = convertChartConfigToUrl(jsonChart.config, jsonChart.title);

    charts.unshift({
      url,
      title: jsonChart.title || 'Population Chart',
      alt: jsonChart.title || 'Chart showing population data'
    });

    // Remove the JSON configuration from text
    processedText =
      processedText.substring(0, jsonChart.startIndex) +
      processedText.substring(jsonChart.endIndex);
  }

  // Handle n8n multi-parameter QuickChart URLs first (specific format)
  const n8nChartPattern = /!\[([^\]]*)\]\((https?:\/\/quickchart\.io\/chart\?[^\)]+(?:type|data|options)=[^)]+)\)/gi;

  let n8nMatch;
  while ((n8nMatch = n8nChartPattern.exec(processedText)) !== null) {
    const title = n8nMatch[1];
    const n8nUrl = n8nMatch[2];

    // Skip if this URL has already been processed
    if (processedUrls.has(n8nUrl)) {
      processedText = processedText.replace(n8nMatch[0], '');
      continue;
    }
    processedUrls.add(n8nUrl);

    // Convert n8n multi-parameter format to standard QuickChart format
    const standardUrl = convertN8nToStandardQuickChartUrl(n8nUrl);
    processedUrls.add(standardUrl); // Also track the converted URL

    // Validate the converted URL before adding
    if (isValidQuickChartUrl(standardUrl)) {
      charts.push({
        url: standardUrl,
        title: title || 'Population Chart',
        alt: title || 'Chart showing population data'
      });
    } else {
      console.warn('Invalid n8n chart URL skipped:', standardUrl);
    }

    // Remove the n8n chart markdown from the text
    processedText = processedText.replace(n8nMatch[0], '');
  }

  // Then, handle existing QuickChart URLs in markdown format (standard format)
  const chartPattern = /!\[([^\]]*)\]\((https?:\/\/(?:quickchart\.io\/chart\?[^\)]+|(?:%3A%2F%2Fquickchart\.io%2Fchart%3F[^\)]+)))\)/gi;

  let match;
  while ((match = chartPattern.exec(processedText)) !== null) {
    const title = match[1];
    const url = decodeUrlIfNeeded(match[2]);

    // Skip if this URL has already been processed
    if (processedUrls.has(url) || processedUrls.has(match[2])) {
      processedText = processedText.replace(match[0], '');
      continue;
    }
    processedUrls.add(url);

    // Validate the URL before adding
    if (isValidQuickChartUrl(url)) {
      charts.push({
        url,
        title: title || 'Population Chart',
        alt: title || 'Chart showing population data'
      });
    } else {
      console.warn('Invalid markdown chart URL skipped:', url);
    }

    // Remove the chart markdown from the text
    processedText = processedText.replace(match[0], '');
  }

  // Finally, handle bare QuickChart URLs (AI agent format) - only if not already processed
  const bareUrlPattern = /https?:\/\/quickchart\.io\/chart\?[^\s)]+/gi;

  let bareUrlMatch;
  while ((bareUrlMatch = bareUrlPattern.exec(processedText)) !== null) {
    const bareUrl = bareUrlMatch[0];

    // Skip if this URL has already been processed in any format
    if (processedUrls.has(bareUrl)) {
      // Remove the duplicate URL from text
      processedText = processedText.replace(bareUrl, '');
      continue;
    }
    processedUrls.add(bareUrl);

    // Extract title with enhanced strategies (including JSON config)
    let title = 'Population Chart';

    // Strategy 1: Extract from JSON configuration (if URL-encoded)
    try {
      const urlObj = new URL(bareUrl);
      const configParam = urlObj.searchParams.get('c');
      if (configParam) {
        // Decode URL-encoded JSON to extract title
        const decodedConfig = safelyDecodeUrlJson(configParam);
        const jsonTitle = extractTitleFromChartConfig(decodedConfig);
        if (jsonTitle) {
          title = jsonTitle;
        }
      }
    } catch (error) {
      console.warn('Failed to extract title from JSON config:', error);
    }

    // Strategy 2: Extract from context if JSON title not found
    if (title === 'Population Chart') {
      const beforeText = processedText.substring(0, bareUrlMatch.index);
      const titlePatterns = [
        /([A-Z][^.]*?\s*(?:Comparison|Chart|Graph|Visualization|Analysis|Report)[^.]*?)\n/i,
        /Chart\s*([^.:]*?):/i,
        /([A-Z][^.]*?\s*(?:Population|Data|Statistics)[^.]*?)\n/i,
        /(?:population|chart|graph|visualization|comparison)[^.]*?[:\-]?\s*([^\n]+)/i
      ];

      for (const pattern of titlePatterns) {
        const titleMatch = beforeText.match(pattern);
        if (titleMatch) {
          title = titleMatch[1] || titleMatch[0];
          title = title.trim().replace(/[.!,?]+$/, '');
          break;
        }
      }
    }

    // Normalize the URL (handle parameters like width, height, etc.)
    const normalizedUrl = normalizeQuickChartUrl(bareUrl);
    processedUrls.add(normalizedUrl); // Also track the normalized URL

    // Validate the URL before adding
    if (isValidQuickChartUrl(normalizedUrl)) {
      charts.push({
        url: normalizedUrl,
        title: title,
        alt: title || 'Chart showing population data'
      });
    } else {
      console.warn('Invalid bare chart URL skipped:', normalizedUrl);
    }

    // Remove the bare URL from the text
    processedText = processedText.replace(bareUrl, '');
  }

  // Clean up any extra whitespace but be less aggressive with content removal
  processedText = processedText
    .replace(/\n{3,}/g, '\n\n')
    .trim();

  return {
    text: processedText,
    charts
  };
};

export const ChartRenderer: React.FC<{ charts: ChartData[] }> = ({ charts }) => {
  const [chartStates, setChartStates] = useState<ChartData[]>(() =>
    charts.map(chart => ({
      ...chart,
      convertedUrl: chart.url,
      isConverting: false,
      conversionError: undefined,
      isDownloading: false,
      loadError: false
    }))
  );

  
  useEffect(() => {
    // Only convert URLs that need PNG conversion
    charts.forEach(async (chart, index) => {
      if (needsPngConversion(chart.url)) {
        try {
          const convertedUrl = await convertUrlToPng(chart.url);
          setChartStates(prev =>
            prev.map((c, i) =>
              i === index
                ? { ...c, convertedUrl, isConverting: false }
                : c
            )
          );
        } catch (error) {
          console.error('Failed to convert chart to PNG:', error);
          setChartStates(prev =>
            prev.map((c, i) =>
              i === index
                ? { ...c, isConverting: false, conversionError: 'Failed to convert to PNG' }
                : c
            )
          );
        }
      }
    });
  }, [charts]);

  const handleDownload = async (chart: ChartData, index: number) => {
    setChartStates(prev =>
      prev.map((c, i) =>
        i === index ? { ...c, isDownloading: true } : c
      )
    );

    try {
      const filename = generateChartFilename(chart.title, index);
      const downloadUrl = chart.convertedUrl || chart.url;

      await downloadImageAsPng(downloadUrl, filename, chart.title);
    } catch (error) {
      console.error('Failed to download chart:', error);
      // Show user-friendly error message for 3 seconds
      setTimeout(() => {
        setChartStates(prev =>
          prev.map((c, i) =>
            i === index ? { ...c, conversionError: 'Download failed. Please try again.' } : c
          )
        );

        // Clear error after 3 seconds
        setTimeout(() => {
          setChartStates(prev =>
            prev.map((c, i) =>
              i === index && c.conversionError === 'Download failed. Please try again.'
                ? { ...c, conversionError: undefined }
                : c
            )
          );
        }, 3000);
      }, 100);
    } finally {
      setChartStates(prev =>
        prev.map((c, i) =>
          i === index ? { ...c, isDownloading: false } : c
        )
      );
    }
  };

  if (chartStates.length === 0) return null;

  return (
    <div className="mt-4 space-y-4">
      {chartStates.map((chart, index) => (
        <div key={index} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          {chart.title && (
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-700">
                {chart.title}
                {chart.conversionError && (
                  <span className="ml-2 text-xs text-amber-600" title={chart.conversionError}>
                    ⚠️
                  </span>
                )}
              </h4>
              <button
                onClick={() => handleDownload(chart, index)}
                disabled={chart.isDownloading}
                className={`p-2 rounded-lg transition-colors flex items-center gap-1 text-xs ${
                  chart.isDownloading
                    ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                }`}
                title={`Download ${chart.title || 'chart'} as PNG`}
              >
                {chart.isDownloading ? (
                  <div className="animate-spin w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                ) : (
                  <Download className="w-3 h-3" />
                )}
                <span>{chart.isDownloading ? 'Downloading...' : 'Download'}</span>
              </button>
            </div>
          )}
          <div className="flex justify-center">
            {chart.loadError ? (
              <div className="flex flex-col items-center justify-center p-4 bg-red-50 rounded-md border border-red-200">
                <div className="text-red-600 text-sm mb-2">⚠️ Chart failed to load</div>
                <div className="text-red-500 text-xs text-center">
                  The chart URL may be invalid or the service might be unavailable.
                </div>
                <button
                  onClick={() => {
                    // Retry loading by resetting the error state
                    setChartStates(prev =>
                      prev.map((c, i) =>
                        i === index ? { ...c, loadError: false } : c
                      )
                    );
                  }}
                  className="mt-2 px-3 py-1 bg-red-100 text-red-700 rounded text-xs hover:bg-red-200"
                >
                  Retry
                </button>
              </div>
            ) : (
              <img
                src={chart.convertedUrl || chart.url}
                alt={chart.alt || 'Chart visualization'}
                className="max-w-full h-auto rounded-md shadow-sm"
                loading="lazy"
                onError={(e) => {
                  console.error('Chart image failed to load:', {
                    url: chart.convertedUrl || chart.url,
                    index,
                    error: e
                  });
                  // Mark as failed instead of hiding
                  setChartStates(prev =>
                    prev.map((c, i) =>
                      i === index ? { ...c, loadError: true } : c
                    )
                  );
                }}
              />
            )}
          </div>
          <div className="mt-2 text-xs text-gray-500 text-center">
            {chart.url.includes('quickchart.io') ? (
              <span>Chart generated by QuickChart.io</span>
            ) : (
              <span>External chart image</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};