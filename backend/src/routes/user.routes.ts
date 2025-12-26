import { Router } from "express";
import { body } from "express-validator";
import { userController } from "../controllers/user.controller";
import { authenticate } from "../middleware/auth.middleware";
import { validate } from "../middleware/validator.middleware";

const router = Router();

// Validation rules
const updateProfileValidation = [
  body("display_name").optional().trim().isLength({ max: 100 }),
  body("avatar_url").optional().isURL().withMessage("Valid URL is required"),
];

const updatePreferencesValidation = [
  body("custom_feed_config").optional().isObject(),
  body("default_filters").optional().isObject(),
  body("timezone").optional().isString(),
];

// Routes
router.patch(
  "/me",
  authenticate,
  validate(updateProfileValidation),
  userController.updateProfile.bind(userController),
);
router.get(
  "/me/preferences",
  authenticate,
  userController.getPreferences.bind(userController),
);
router.put(
  "/me/preferences",
  authenticate,
  validate(updatePreferencesValidation),
  userController.updatePreferences.bind(userController),
);

export default router;
