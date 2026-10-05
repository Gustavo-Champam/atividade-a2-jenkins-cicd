const { defineConfig } = require('cypress');
module.exports = defineConfig({
  video: true,
  reporter: 'junit',
  reporterOptions: { mochaFile: 'cypress/results/e2e-[hash].xml', toConsole: true },
  e2e: { baseUrl: process.env.CYPRESS_BASE_URL || 'http://localhost:3000', supportFile: false }
});
