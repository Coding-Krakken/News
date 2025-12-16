import { Router } from 'express';
import { body } from 'express-validator';
import { bookmarkController } from '../controllers/bookmark.controller';
import { authenticate } from '../middleware/auth.middleware';
import { validate } from '../middleware/validator.middleware';

const router = Router();

// Validation rules
const createBookmarkValidation = [
  body('target_type').isIn(['article', 'story']).withMessage('target_type must be article or story'),
  body('target_id').notEmpty().trim().withMessage('target_id is required'),
];

// Routes
router.post('/', authenticate, validate(createBookmarkValidation), bookmarkController.create.bind(bookmarkController));
router.get('/', authenticate, bookmarkController.list.bind(bookmarkController));
router.delete('/:id', authenticate, bookmarkController.delete.bind(bookmarkController));

export default router;
