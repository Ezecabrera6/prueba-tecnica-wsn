from __future__ import annotations


class ChallengeError(Exception):
    """Base error for domain/application failures."""


class RecipeNotFoundError(ChallengeError):
    pass


class IngredientPriceNotFoundError(ChallengeError):
    pass


class InvalidQuoteDateError(ChallengeError):
    pass


class FXApiError(ChallengeError):
    pass
