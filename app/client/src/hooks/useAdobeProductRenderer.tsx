import { useCopilotAction } from '@copilotkit/react-core';
import { AdobeProductCards } from '../components/adobe/AdobeProductCards';
import { AdobeProduct, UseAdobeProductRendererReturn } from '../types/adobe-products.types';

/**
 * Custom hook that registers a CopilotKit action to intercept
 * Adobe product tool calls and render them as merch-cards.
 *
 * This hook must be called at the top level of a component that's
 * wrapped in a CopilotKit provider.
 *
 * @returns {UseAdobeProductRendererReturn} Hook registration status
 */
export const useAdobeProductRenderer = (): UseAdobeProductRendererReturn => {
  useCopilotAction({
    // CRITICAL: This name must match the backend tool name exactly
    name: 'get_adobe_products',

    // Mark as frontend-only (handled by rendering, not execution)
    available: 'frontend',

    // Description for the action (shown in CopilotKit dev tools)
    description: 'Render Adobe products as interactive merch-cards',

    // The render function that intercepts the tool call
    render: ({ status, args, result }) => {
      // Show loading state while the tool is executing
      if (status === 'executing') {
        return <AdobeProductCards products={[]} loading={true} />;
      }

      // Handle errors
      if (status === 'complete' && result?.error) {
        return (
          <AdobeProductCards
            products={[]}
            error={result.error}
          />
        );
      }

      // Parse and render the products
      if (status === 'complete' && result) {
        try {
          // The result is a JSON string from the backend tool
          let products: AdobeProduct[] = [];

          // Try to parse the result
          if (typeof result === 'string') {
            const parsed = JSON.parse(result);
            // Handle both direct array and object with products field
            products = Array.isArray(parsed) ? parsed : parsed.products || [];
          } else if (Array.isArray(result)) {
            products = result;
          } else if (result.products && Array.isArray(result.products)) {
            products = result.products;
          }

          return <AdobeProductCards products={products} />;
        } catch (error) {
          console.error('Error parsing Adobe products:', error);
          return (
            <AdobeProductCards
              products={[]}
              error="Failed to parse product data"
            />
          );
        }
      }

      // Default: return null for other statuses
      return null;
    },
  });

  return {
    isRegistered: true,
  };
};

export default useAdobeProductRenderer;
