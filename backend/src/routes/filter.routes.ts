import { Router } from "express";
import { body } from "express-validator";
import { filterController } from "../controllers/filter.controller";
import { authenticate } from "../middleware/auth.middleware";
import { validate } from "../middleware/validator.middleware";

const router = Router();

// Validation rules
const createFilterValidation = [
  body("name")
    .notEmpty()
    .trim()
    .isLength({ max: 100 })
    .withMessage("Name is required"),
  body("filter_query").isObject().withMessage("filter_query must be an object"),
];

const updateFilterValidation = [
  body("name").optional().trim().isLength({ max: 100 }),
  body("filter_query").optional().isObject(),
];

// Routes
router.post(
  "/",
  authenticate,
  validate(createFilterValidation),
  filterController.create.bind(filterController),
);
router.get("/", authenticate, filterController.list.bind(filterController));
router.put(
  "/:id",
  authenticate,
  validate(updateFilterValidation),
  filterController.update.bind(filterController),
);
router.delete(
  "/:id",
  authenticate,
  filterController.delete.bind(filterController),
);

export default router;
