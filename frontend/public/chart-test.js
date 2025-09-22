// Simple test for chart detection
console.log('🔍 Testing chart detection...');

// Test content
const testContent = `Here is the requested comparison of total population between Kedah and Selangor in 2015:

**Total Population Comparison between Kedah and Selangor in 2015**

Based on the available data, here are the total population figures:

- **Kedah**: 2,045,300 people
- **Selangor**: 6,231,800 people

This shows that Selangor had approximately 3 times the population of Kedah in 2015.

**Chart Visualization**
https://quickchart.io/chart?width=200&c=%7B%22type%22%3A%22bar%22%2C%22data%22%3A%7B%22labels%22%3A%5B%22Kedah%22%2C%22Selangor%22%5D%2C%22datasets%22%3A%5B%7B%22label%22%3A%22Population%202015%22%2C%22data%22%3A%5B2045300%2C6231800%5D%2C%22backgroundColor%22%3A%5B%22rgba(75%2C%20192%2C%20192%2C%200.2)%22%2C%22rgba(54%2C%20162%2C%20235%2C%200.2)%22%5D%2C%22borderColor%22%3A%5B%22rgba(75%2C%20192%2C%20192%2C%201)%22%2C%22rgba(54%2C%20162%2C%20235%2C%201)%22%5D%2C%22borderWidth%22%3A1%7D%5D%7D%2C%22options%22%3A%7B%22scales%22%3A%7B%22yAxes%22%3A%5B%7B%22ticks%22%3A%7B%22max%22%3A7000000%2C%22min%22%3A0%2C%22stepSize%22%3A1000000%2C%22beginAtZero%22%3Atrue%7D%2C%22stacked%22%3Afalse%7D%5D%2C%22xAxes%22%3A%7B%22stacked%22%3Afalse%7D%7D%2C%22plugins%22%3A%7B%22title%22%3A%7B%22display%22%3Atrue%2C%22text%22%3A%22Total%20Population%20Comparison%20between%20Kedah%20and%20Selangor%20in%202015%22%7D%2C%22legend%22%3A%7B%22display%22%3Atrue%2C%22position%22%3A%22top%22%7D%7D%7D%7D`;

// Test contentLikelyContainsCharts
const contentLikelyContainsCharts = (content: string): boolean => {
  const chartKeywords = [
    '![', 'chart', 'graph', 'visualization', 'plot',
    'quickchart.io', '{"type":', '{"data":', '{"labels":',
    'https://', 'http://'  // Include URLs for bare link detection
  ];

  const lowerContent = content.toLowerCase();
  return chartKeywords.some(keyword => lowerContent.includes(keyword.toLowerCase()));
};

console.log('🔍 contentLikelyContainsCharts:', contentLikelyContainsCharts(testContent));

// Test bare URL pattern
const bareUrlPattern = /https?:\/\/quickchart\.io\/chart\?[^\s)]+/gi;
const bareUrlMatches = testContent.match(bareUrlPattern);
console.log('🔍 Bare URL matches:', bareUrlMatches ? bareUrlMatches.length : 0);
if (bareUrlMatches) {
    bareUrlMatches.forEach((url, index) => {
        console.log(`🔍 URL ${index + 1}:`, url);
    });
}

// Test JSON extraction interference
const jsonPattern = /\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}/g;
let jsonMatch;
let jsonCount = 0;
let skippedJsonCount = 0;

while ((jsonMatch = jsonPattern.exec(testContent)) !== null) {
    jsonCount++;
    const beforeText = testContent.substring(0, jsonMatch.index);
    const afterText = testContent.substring(jsonMatch.index + jsonMatch[0].length);

    const isWithinUrl =
        beforeText.includes('quickchart.io/chart?') ||
        beforeText.includes('?c=') ||
        beforeText.includes('&c=') ||
        beforeText.includes('chart?') ||
        afterText.includes('quickchart.io') ||
        afterText.includes('&') ||
        afterText.includes('?');

    if (isWithinUrl) {
        skippedJsonCount++;
        console.log(`🔍 JSON ${jsonCount}: Skipped (within URL context)`);
    } else {
        console.log(`🔍 JSON ${jsonCount}: Would be extracted`);
    }
}

console.log('🔍 Total JSON found:', jsonCount);
console.log('🔍 JSON skipped:', skippedJsonCount);
console.log('🔍 JSON that would be processed:', jsonCount - skippedJsonCount);

console.log('🔍 Test complete - if bare URL matches > 0, chart detection should work');