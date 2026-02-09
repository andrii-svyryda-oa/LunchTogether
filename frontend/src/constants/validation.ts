export const VALIDATION = {
  PASSWORD: {
    MIN_LENGTH: 8,
    MAX_LENGTH: 128,
  },
  EMAIL: {
    MAX_LENGTH: 255,
  },
  FULL_NAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 100,
  },
} as const;

export const VALIDATION_MESSAGES = {
  REQUIRED: "This field is required",
  EMAIL: {
    INVALID: "Please enter a valid email address",
    MAX_LENGTH: `Email must be at most ${VALIDATION.EMAIL.MAX_LENGTH} characters`,
  },
  PASSWORD: {
    MIN_LENGTH: `Password must be at least ${VALIDATION.PASSWORD.MIN_LENGTH} characters`,
    MAX_LENGTH: `Password must be at most ${VALIDATION.PASSWORD.MAX_LENGTH} characters`,
  },
  FULL_NAME: {
    MIN_LENGTH: `Name must be at least ${VALIDATION.FULL_NAME.MIN_LENGTH} characters`,
    MAX_LENGTH: `Name must be at most ${VALIDATION.FULL_NAME.MAX_LENGTH} characters`,
  },
} as const;
