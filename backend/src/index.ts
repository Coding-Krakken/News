import { createApp } from './app';
import { config } from './config';
import { testConnection } from './config/database';
import { logger } from './utils/logger';

async function start() {
  try {
    // Optionally skip database connection check (useful for local e2e runs)
    if (process.env.SKIP_DB_CHECK === '1') {
      logger.info('SKIP_DB_CHECK set — skipping database connection test');
    } else {
      // Test database connection
      const connected = await testConnection();
      if (!connected) {
        logger.error('Failed to connect to database');
        process.exit(1);
      }

      logger.info('Database connection established');
    }

    // Create and start server
    const app = createApp();
    
    const server = app.listen(config.port, () => {
      logger.info(`Server running on port ${config.port} in ${config.env} mode`);
    });

    // Graceful shutdown
    process.on('SIGTERM', () => {
      logger.info('SIGTERM signal received: closing HTTP server');
      server.close(() => {
        logger.info('HTTP server closed');
        process.exit(0);
      });
    });

    process.on('SIGINT', () => {
      logger.info('SIGINT signal received: closing HTTP server');
      server.close(() => {
        logger.info('HTTP server closed');
        process.exit(0);
      });
    });
  } catch (error) {
    logger.error('Failed to start server', { error });
    process.exit(1);
  }
}

start();
