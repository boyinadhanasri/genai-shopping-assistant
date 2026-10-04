/**
 * Category Budget Rules Configuration
 * Curated dynamic budget chips, prompts, and examples for each category.
 */

export const CATEGORY_BUDGET_RULES = {
  'Home & Kitchen': {
    chips: [500, 1000, 2500, 5000, 10000],
    labels: ['Under ₹500', 'Under ₹1,000', 'Under ₹2,500', 'Under ₹5,000', 'Under ₹10,000'],
    prompts: [
      'Cookware essentials under ₹1,000',
      'Air Fryer under ₹5,000',
      'Mixer Grinder 750W under ₹2,500',
      'Stainless steel pressure cooker under ₹1,500',
      'Airtight storage container set under ₹1,000',
      'Cotton bedsheet king size under ₹1,000',
    ],
    heroPrompt: 'Cookware essentials under ₹1,000',
    heroQuery: 'Cookware fry pan under 1000',
    examples: ['Cookware', 'Kitchen Appliances', 'Air Fryers', 'Mixer Grinders', 'Home Decor', 'Furniture', 'Bedsheets'],
  },
  Books: {
    chips: [200, 500, 1000],
    labels: ['Under ₹200', 'Under ₹500', 'Under ₹1,000'],
    prompts: [
      'Python programming books under ₹500',
      'Machine Learning & AI books under ₹1,000',
      'The Psychology of Money under ₹500',
      'Atomic Habits under ₹500',
      'System Design Interview guide under ₹1,000',
      'UPSC Indian Polity by Laxmikanth under ₹1,000',
    ],
    heroPrompt: 'Python books under ₹500',
    heroQuery: 'Python programming book under 500',
    examples: ['Programming', 'Data Science', 'AI & ML', 'Business', 'Finance', 'Self Help', 'Novels', 'UPSC', 'JEE'],
  },
  Sports: {
    chips: [500, 1500, 3000, 5000],
    labels: ['Under ₹500', 'Under ₹1,500', 'Under ₹3,000', 'Under ₹5,000'],
    prompts: [
      'Kashmir willow cricket bat under ₹1,500',
      'Yonex badminton racket under ₹1,500',
      'Adjustable dumbbells 20kg set under ₹3,000',
      'Eco-friendly non-slip yoga mat under ₹1,000',
      'Anti-fog swimming goggles under ₹500',
      'Nivia football size 5 under ₹1,000',
    ],
    heroPrompt: 'Cricket bat under ₹1,500',
    heroQuery: 'Cricket bat under 1500',
    examples: ['Cricket', 'Football', 'Badminton', 'Gym Equipment', 'Running', 'Cycling', 'Yoga', 'Swimming'],
  },
  Electronics: {
    chips: [5000, 10000, 25000, 50000],
    labels: ['Under ₹5,000', 'Under ₹10,000', 'Under ₹25,000', 'Under ₹50,000'],
    prompts: [
      'Laptop for programming under ₹50,000',
      'Gaming laptop under ₹70,000',
      'Wireless ANC Earbuds under ₹5,000',
      'Smartwatch with AMOLED under ₹5,000',
      '4K Smart TV under ₹25,000',
      'Vlog Camera under ₹40,000',
    ],
    heroPrompt: 'Laptops under ₹50,000',
    heroQuery: 'Best laptop for coding under 50000',
    examples: ['Laptops', 'Smartphones', 'Earbuds', 'Cameras', 'Smart TVs', 'Smartwatches'],
  },
  Fashion: {
    chips: [500, 1000, 2000, 5000],
    labels: ['Under ₹500', 'Under ₹1,000', 'Under ₹2,000', 'Under ₹5,000'],
    prompts: [
      'Men slim fit jeans under ₹2,000',
      'Cotton casual t-shirts under ₹500',
      'Running sneakers under ₹2,000',
      'Party wear dresses under ₹2,000',
      'Formal leather shoes under ₹3,000',
    ],
    heroPrompt: 'Jeans under ₹2,000',
    heroQuery: 'Jeans under 2000',
    examples: ['Jeans', 'Tops', 'T-Shirts', 'Dresses', 'Shoes', 'Sneakers', 'Jackets'],
  },
  Beauty: {
    chips: [200, 500, 1000, 2000],
    labels: ['Under ₹200', 'Under ₹500', 'Under ₹1,000', 'Under ₹2,000'],
    prompts: [
      'Gentle face wash for oily skin under ₹500',
      'Hydrating gel moisturizer under ₹500',
      'Sunscreen SPF 50 matte finish under ₹500',
      'Long-lasting matte lipstick under ₹500',
      'Luxury perfume EDP under ₹2,000',
    ],
    heroPrompt: 'Moisturizer under ₹500',
    heroQuery: 'Best moisturizer under 500',
    examples: ['Face Wash', 'Moisturizer', 'Lipstick', 'Perfume', 'Sunscreen', 'Serum'],
  },
  Toys: {
    chips: [300, 500, 1000, 2000],
    labels: ['Under ₹300', 'Under ₹500', 'Under ₹1,000', 'Under ₹2,000'],
    prompts: [
      'LEGO building blocks set under ₹2,000',
      'High speed remote control car under ₹1,000',
      'STEM science learning kit under ₹1,000',
      'Classic board games under ₹500',
    ],
    heroPrompt: 'LEGO sets under ₹2,000',
    heroQuery: 'LEGO building toy under 2000',
    examples: ['LEGO', 'RC Cars', 'Board Games', 'STEM Toys', 'Action Figures', 'Puzzles'],
  },
};

export function getCategoryBudgetRule(category) {
  if (!category) return CATEGORY_BUDGET_RULES['Home & Kitchen'];
  const key = Object.keys(CATEGORY_BUDGET_RULES).find(
    k => k.toLowerCase() === category.toLowerCase() || category.toLowerCase().includes(k.toLowerCase())
  );
  return key ? CATEGORY_BUDGET_RULES[key] : CATEGORY_BUDGET_RULES['Home & Kitchen'];
}
