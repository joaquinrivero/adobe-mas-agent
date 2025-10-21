/**
 * TypeScript type definitions for Adobe product data from Commerce Fragment API
 */

/**
 * Represents a single Adobe product from the Commerce Fragment API
 */
export interface AdobeProduct {
  /** Unique product identifier */
  id: string;

  /** Product name/title */
  name: string;

  /** Product description */
  description: string;

  /** Pricing information (can be a string with currency symbol or price object) */
  price?: string | {
    amount: number;
    currency: string;
    formatted: string;
  };

  /** Call-to-action information */
  cta?: {
    text: string;
    url: string;
  };

  /** Target audience for the product */
  audience?: string;

  /** Product line or category */
  productLine?: string;

  /** Product icon URL or identifier */
  icon?: string;

  /** Product image URL */
  image?: string;

  /** Whether this is a promotional/featured product */
  promo?: boolean;

  /** Product variant (e.g., "catalog", "special-offers", "segment") */
  variant?: string;

  /** Product size (e.g., "wide", "super-wide") */
  size?: string;

  /** Badge text for the product */
  badge?: string;

  /** Additional metadata */
  metadata?: Record<string, any>;
}

/**
 * Response format from the get_adobe_products tool
 */
export interface AdobeProductsResponse {
  /** Array of Adobe products matching the query */
  products: AdobeProduct[];

  /** Total number of products found */
  total?: number;

  /** Query that was used to filter products */
  query?: string;
}

/**
 * Props for the AdobeProductCards component
 */
export interface AdobeProductCardsProps {
  /** Array of products to display */
  products: AdobeProduct[];

  /** Optional CSS class name for container */
  className?: string;

  /** Loading state */
  loading?: boolean;

  /** Error message if any */
  error?: string;
}

/**
 * Hook return type for useAdobeProductRenderer
 */
export interface UseAdobeProductRendererReturn {
  /** Whether the hook is registered */
  isRegistered: boolean;
}
