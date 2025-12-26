import { Router } from "express";
import { feedController } from "../controllers/feed.controller";
import { authenticate } from "../middleware/auth.middleware";

const router = Router();

// Routes
router.get(
  "/custom",
  authenticate,
  feedController.getCustomFeed.bind(feedController),
);

export default router;
