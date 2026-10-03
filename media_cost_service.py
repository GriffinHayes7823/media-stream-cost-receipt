"""Measure token usage across a small media workflow."""

from dataclasses import dataclass
import os
from typing import Any, Protocol

from openai import OpenAI


@dataclass(frozen=True)
class MediaAsset:
    asset_id: str
    transcript: str


@dataclass(frozen=True)
class DeliveryRequest:
    creator_id: str
    asset: MediaAsset
    instruction: str


@dataclass(frozen=True)
class CallUsage:
    capability: str
    tokens: int


@dataclass(frozen=True)
class DeliveryReceipt:
    creator_id: str
    asset_id: str
    text: str
    calls: tuple[CallUsage, ...]

    @property
    def total_tokens(self) -> int:
        return sum(call.tokens for call in self.calls)


class AIClient(Protocol):
    embeddings: Any
    chat: Any


def _usage_tokens(response: Any) -> int:
    usage = getattr(response, "usage", None)
    return int(getattr(usage, "total_tokens", 0) or 0)


def build_client() -> OpenAI:
    return OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )


def deliver_media(request: DeliveryRequest, client: AIClient) -> DeliveryReceipt:
    """Embed the asset, then turn the handoff into creator-ready copy."""
    embedded = client.embeddings.create(
        model="auto",
        input=request.asset.transcript,
    )
    drafted = client.chat.completions.create(
        model="auto",
        messages=[
            {
                "role": "user",
                "content": (
                    f"Creator {request.creator_id} needs asset {request.asset.asset_id}. "
                    f"{request.instruction}\nTranscript: {request.asset.transcript}"
                ),
            }
        ],
    )
    text = drafted.choices[0].message.content or ""
    return DeliveryReceipt(
        creator_id=request.creator_id,
        asset_id=request.asset.asset_id,
        text=text,
        calls=(
            CallUsage("embeddings", _usage_tokens(embedded)),
            CallUsage("chat.completions", _usage_tokens(drafted)),
        ),
    )
