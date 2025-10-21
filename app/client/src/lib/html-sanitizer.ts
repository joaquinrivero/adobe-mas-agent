/**
 * HTML Sanitizer for Backend Tool Rendering
 *
 * Provides DOMPurify configuration for safely rendering HTML from backend tools
 * while allowing Adobe MAS web components and required attributes.
 */

import DOMPurify from 'dompurify';

/**
 * Sanitize HTML from backend tools while allowing Adobe MAS components.
 *
 * Whitelist custom elements (merch-card, merch-price) and required
 * attributes for WCS (Web Commerce System) integration.
 *
 * @param html - Raw HTML string from backend tool
 * @returns Sanitized HTML safe for rendering with dangerouslySetInnerHTML
 */
export function sanitizeToolHTML(html: string): string {
  return DOMPurify.sanitize(html, {
    // Allow MAS web components
    ADD_TAGS: ['merch-card', 'merch-price', 'checkout-link'],

    // Allow MAS and WCS attributes
    ADD_ATTR: [
      'slot',                    // MAS slot system for content placement
      'variant',                 // Card variant (plans, special-offers)
      'size',                    // Card size (wide, super-wide)
      'badge-background-color',  // Badge styling
      'badge-color',             // Badge text color
      'data-wcs-osi',           // WCS offer selector ID
      'data-template',          // WCS template
      'data-analytics-id',      // Analytics tracking
      'is',                     // Custom element definition
      'data-tool-rendered'      // Marker for tool-rendered content
    ],

    // Security settings
    ALLOW_UNKNOWN_PROTOCOLS: false,
    ALLOW_DATA_ATTR: false, // Block data-* except whitelisted ones above
  });
}
