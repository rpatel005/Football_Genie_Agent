/**
 * Frontend Test Suite Configuration for Football Genie
 * 
 * This test suite uses Vitest with React Testing Library.
 * To run these tests, you need to:
 * 
 * 1. Install dependencies:
 *    npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom @testing-library/user-event
 * 
 * 2. Add test script to package.json:
 *    "test": "vitest",
 *    "test:coverage": "vitest --coverage"
 * 
 * 3. Add vitest config to vite.config.js:
 *    test: {
 *      globals: true,
 *      environment: 'jsdom',
 *      setupFiles: './src/__tests__/setup.js',
 *    }
 */

import '@testing-library/jest-dom';

// Mock window.matchMedia for responsive tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock scrollIntoView
Element.prototype.scrollIntoView = jest.fn();

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  })
);
