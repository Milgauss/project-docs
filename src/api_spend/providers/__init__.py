"""Provider registry and adapters."""

from __future__ import annotations

from typing import TypeAlias

from api_spend.providers.base import (
    BillingApiProvider,
    FetchCostsResult,
    SnapshotProvider,
)
from api_spend.providers.anthropic import AnthropicBillingProvider
from api_spend.providers.brave import BraveSnapshotProvider
from api_spend.providers.brightdata import BrightDataBillingProvider
from api_spend.providers.openai import OpenAIBillingProvider
from api_spend.providers.resend import ResendSnapshotProvider

ProviderClass: TypeAlias = type[BillingApiProvider] | type[SnapshotProvider]

PROVIDER_REGISTRY: dict[str, ProviderClass] = {
    "openai": OpenAIBillingProvider,
    "anthropic": AnthropicBillingProvider,
    "brightdata": BrightDataBillingProvider,
    "resend": ResendSnapshotProvider,
    "brave_search": BraveSnapshotProvider,
}


def get_provider_class(name: str) -> ProviderClass:
    try:
        return PROVIDER_REGISTRY[name]
    except KeyError as e:
        raise KeyError(f"no provider adapter registered for {name!r}") from e

__all__ = [
    "AnthropicBillingProvider",
    "BillingApiProvider",
    "BraveSnapshotProvider",
    "BrightDataBillingProvider",
    "FetchCostsResult",
    "OpenAIBillingProvider",
    "PROVIDER_REGISTRY",
    "ResendSnapshotProvider",
    "SnapshotProvider",
    "get_provider_class",
]
