module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
    '!src/**/*.spec.ts',
    '!src/index.ts',
  ],
  // Relaxed coverage thresholds for local runs; CI may enforce stricter gates.
  coverageThreshold: {
    global: {
      branches: 50,
      functions: 80,
      lines: 75,
      statements: 75,
    },
  },
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
  ],
  setupFilesAfterEnv: ['<rootDir>/src/test/setup.ts'],
};
