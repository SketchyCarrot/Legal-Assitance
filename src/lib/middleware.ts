import { NextApiRequest, NextApiResponse } from 'next';
import rateLimit from 'express-rate-limit';
import { createLogger, format, transports } from 'winston';

// Configure Winston logger
const logger = createLogger({
  format: format.combine(
    format.timestamp(),
    format.json()
  ),
  transports: [
    new transports.File({ filename: 'logs/error.log', level: 'error' }),
    new transports.File({ filename: 'logs/combined.log' })
  ]
});

// Add console transport in development
if (process.env.NODE_ENV !== 'production') {
  logger.add(new transports.Console({
    format: format.simple()
  }));
}

// Configure rate limiter
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

// Type for the handler function
type ApiHandler = (req: NextApiRequest, res: NextApiResponse) => Promise<void>;

// Middleware wrapper
export function withMiddleware(handler: ApiHandler): ApiHandler {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    try {
      // Apply rate limiting
      await new Promise((resolve, reject) => {
        limiter(req as any, res as any, (result: any) => {
          if (result instanceof Error) {
            return reject(result);
          }
          return resolve(result);
        });
      });

      // Log request
      logger.info('API Request', {
        method: req.method,
        url: req.url,
        query: req.query,
        body: req.body,
        headers: {
          ...req.headers,
          authorization: undefined // Don't log auth headers
        }
      });

      // Call the actual handler
      await handler(req, res);

      // Log response
      logger.info('API Response', {
        method: req.method,
        url: req.url,
        statusCode: res.statusCode
      });
    } catch (error) {
      // Log error
      logger.error('API Error', {
        method: req.method,
        url: req.url,
        error: error instanceof Error ? error.message : 'Unknown error'
      });

      // Send error response
      res.status(error instanceof Error && error.message.includes('rate limit') ? 429 : 500).json({
        error: error instanceof Error ? error.message : 'Internal server error'
      });
    }
  };
}

// Validate Azure OpenAI API key middleware
export function validateApiKey(req: NextApiRequest, res: NextApiResponse, next: () => void) {
  const apiKey = req.headers['x-api-key'];
  
  if (!apiKey || apiKey !== process.env.API_KEY) {
    res.status(401).json({ error: 'Unauthorized' });
    return;
  }
  
  next();
} 