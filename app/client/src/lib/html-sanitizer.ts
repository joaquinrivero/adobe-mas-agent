/**
 * HTML Sanitization Utility
 *
 * Safely sanitizes HTML from backend tools while allowing Adobe MAS web components
 * to render properly. Uses DOMParser for browser-native sanitization.
 */

/**
 * List of allowed HTML tags that can be rendered.
 * Includes Adobe MAS web components and standard HTML elements.
 */
const ALLOWED_TAGS = new Set([
  // Adobe MAS web components
  'merch-card',
  'merch-price',
  'checkout-link',
  'merch-icon',

  // Standard HTML elements
  'div',
  'span',
  'p',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
  'ul', 'ol', 'li',
  'a',
  'strong', 'em', 'b', 'i',
  'br',
  'style',
]);

/**
 * List of allowed attributes for HTML elements.
 * Includes data attributes and MAS-specific attributes.
 */
const ALLOWED_ATTRIBUTES = new Set([
  // Standard attributes
  'class',
  'id',
  'style',
  'href',
  'target',
  'rel',
  'slot',

  // MAS component attributes
  'variant',
  'size',
  'badge-background-color',
  'badge-color',
  'icons',
  'template',

  // Data attributes (allow all data-*)
  // Checked separately with startsWith
]);

/**
 * Protocols allowed in href and src attributes
 */
const ALLOWED_PROTOCOLS = new Set([
  'https:',
  'http:',
  'mailto:',
]);

/**
 * Domains allowed for links (Adobe domains only for CTAs)
 */
const ALLOWED_LINK_DOMAINS = new Set([
  'adobe.com',
  'www.adobe.com',
  'commerce.adobe.com',
  'creativecloud.adobe.com',
  'firefly.adobe.com',
]);

/**
 * Check if a URL is safe (correct protocol and allowed domain)
 */
function isSafeUrl(url: string): boolean {
  try {
    const urlObj = new URL(url);

    // Check protocol
    if (!ALLOWED_PROTOCOLS.has(urlObj.protocol)) {
      return false;
    }

    // For mailto, allow all
    if (urlObj.protocol === 'mailto:') {
      return true;
    }

    // Check if hostname ends with allowed domain
    const hostname = urlObj.hostname.toLowerCase();
    return Array.from(ALLOWED_LINK_DOMAINS).some(domain =>
      hostname === domain || hostname.endsWith('.' + domain)
    );
  } catch {
    return false;
  }
}

/**
 * Sanitize HTML content by removing dangerous elements and attributes
 * while preserving Adobe MAS web components.
 *
 * @param html - Raw HTML string from backend tool
 * @returns Sanitized HTML string safe for rendering
 */
export function sanitizeToolHTML(html: string): string {
  if (!html || typeof html !== 'string') {
    return '';
  }

  try {
    // Parse HTML using DOMParser
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    // Recursive function to sanitize nodes
    function sanitizeNode(node: Node): Node | null {
      if (node.nodeType === Node.TEXT_NODE) {
        return node;
      }

      if (node.nodeType === Node.ELEMENT_NODE) {
        const element = node as Element;
        const tagName = element.tagName.toLowerCase();

        // Remove scripts and dangerous elements
        if (tagName === 'script' || tagName === 'iframe' || tagName === 'object' || tagName === 'embed') {
          return null;
        }

        // Check if tag is allowed
        if (!ALLOWED_TAGS.has(tagName)) {
          return null;
        }

        // Create new clean element
        const cleanElement = document.createElement(tagName);

        // Copy allowed attributes
        Array.from(element.attributes).forEach(attr => {
          const attrName = attr.name.toLowerCase();

          // Allow data-* attributes
          if (attrName.startsWith('data-')) {
            cleanElement.setAttribute(attrName, attr.value);
            return;
          }

          // Allow other whitelisted attributes
          if (ALLOWED_ATTRIBUTES.has(attrName)) {
            // Special handling for href and src
            if (attrName === 'href' || attrName === 'src') {
              if (isSafeUrl(attr.value)) {
                cleanElement.setAttribute(attrName, attr.value);
              }
            } else {
              cleanElement.setAttribute(attrName, attr.value);
            }
          }
        });

        // Recursively sanitize children
        Array.from(element.childNodes).forEach(child => {
          const sanitizedChild = sanitizeNode(child);
          if (sanitizedChild) {
            cleanElement.appendChild(sanitizedChild);
          }
        });

        return cleanElement;
      }

      return null;
    }

    // Sanitize body content
    const sanitizedBody = document.createElement('div');
    Array.from(doc.body.childNodes).forEach(child => {
      const sanitizedChild = sanitizeNode(child);
      if (sanitizedChild) {
        sanitizedBody.appendChild(sanitizedChild);
      }
    });

    return sanitizedBody.innerHTML;

  } catch (error) {
    console.error('Error sanitizing HTML:', error);
    return '';
  }
}

/**
 * Check if HTML content appears to be tool-rendered (contains data-tool-rendered attribute)
 */
export function isToolRenderedHTML(html: string): boolean {
  return html.includes('data-tool-rendered="true"') ||
         html.includes('adobe-products-container') ||
         html.includes('<merch-card');
}
