import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  _next: NextFunction
): void {
  logger.error('Error handler caught error', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
  });

  // PostgreSQL unique constraint violation
  if ('code' in err && err.code === '23505') {
    res.status(409).json({ error: 'Resource already exists' });
    return;
  }

  // PostgreSQL foreign key violation
  if ('code' in err && err.code === '23503') {
    res.status(400).json({ error: 'Invalid reference' });
    return;
  }

  res.status(500).json({ error: 'Internal server error' });
}

export function notFoundHandler(req: Request, res: Response): void {
  res.status(404).json({ error: 'Route not found' });
}
