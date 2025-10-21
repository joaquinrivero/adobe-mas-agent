import React from 'react';
import { AdobeProduct, AdobeProductCardsProps } from '../../types/adobe-products.types';

/**
 * Component that renders Adobe Spectrum merch-card web components
 * in a responsive grid layout with dark mode support.
 */
export const AdobeProductCards: React.FC<AdobeProductCardsProps> = ({
  products,
  className = '',
  loading = false,
  error,
}) => {
  if (loading) {
    return (
      <div className="light p-4 rounded-lg">
        <div className="animate-pulse space-y-4">
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="light p-4 rounded-lg bg-red-50 border border-red-200">
        <p className="text-red-800">Error loading products: {error}</p>
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="light p-4 rounded-lg">
        <p className="text-gray-600">No products found.</p>
      </div>
    );
  }

  return (
    <div className={`light product-cards-container ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
        {products.map((product, index) => (
          <MerchCard key={product.id || index} product={product} />
        ))}
      </div>
    </div>
  );
};

/**
 * Wrapper component for a single merch-card web component
 */
const MerchCard: React.FC<{ product: AdobeProduct }> = ({ product }) => {
  const cardRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    // Set up the merch-card web component
    if (cardRef.current) {
      const merchCard = document.createElement('merch-card');

      // Set attributes
      merchCard.setAttribute('variant', product.variant || 'catalog');
      merchCard.setAttribute('size', product.size || 'wide');

      if (product.badge) {
        merchCard.setAttribute('badge-text', product.badge);
      }

      // Set content slots
      const slots = [];

      // Product name
      if (product.name) {
        const nameSlot = document.createElement('h3');
        nameSlot.setAttribute('slot', 'heading-xs');
        nameSlot.textContent = product.name;
        slots.push(nameSlot);
      }

      // Product description
      if (product.description) {
        const descSlot = document.createElement('p');
        descSlot.setAttribute('slot', 'body-xs');
        descSlot.textContent = product.description;
        slots.push(descSlot);
      }

      // Pricing
      if (product.price) {
        const priceSlot = document.createElement('p');
        priceSlot.setAttribute('slot', 'price');
        priceSlot.textContent = typeof product.price === 'string'
          ? product.price
          : product.price.formatted;
        slots.push(priceSlot);
      }

      // CTA button
      if (product.cta) {
        const ctaSlot = document.createElement('a');
        ctaSlot.setAttribute('slot', 'cta');
        ctaSlot.setAttribute('href', product.cta.url);
        ctaSlot.setAttribute('target', '_blank');
        ctaSlot.setAttribute('rel', 'noopener noreferrer');
        ctaSlot.textContent = product.cta.text;
        slots.push(ctaSlot);
      }

      // Product line tag
      if (product.productLine) {
        const productLineSlot = document.createElement('span');
        productLineSlot.setAttribute('slot', 'detail-m');
        productLineSlot.textContent = product.productLine;
        slots.push(productLineSlot);
      }

      // Audience tag
      if (product.audience) {
        const audienceSlot = document.createElement('span');
        audienceSlot.setAttribute('slot', 'detail-s');
        audienceSlot.textContent = product.audience;
        slots.push(audienceSlot);
      }

      // Append all slots to the card
      slots.forEach(slot => merchCard.appendChild(slot));

      // Clear and append to container
      cardRef.current.innerHTML = '';
      cardRef.current.appendChild(merchCard);
    }
  }, [product]);

  return <div ref={cardRef} className="merch-card-wrapper" />;
};

export default AdobeProductCards;
