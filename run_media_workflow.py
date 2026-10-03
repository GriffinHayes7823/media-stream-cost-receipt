"""Runnable entry point for the media ingestion and creator delivery example."""

from media_cost_service import DeliveryRequest, MediaAsset, build_client, deliver_media


def main() -> None:
    request = DeliveryRequest(
        creator_id="creator-17",
        asset=MediaAsset(
            asset_id="session-42",
            transcript="A three-minute field recording about restoring a city garden.",
        ),
        instruction="Write a concise delivery note with one title and two sentences.",
    )
    receipt = deliver_media(request, build_client())
    print(receipt.text)
    print(f"asset={receipt.asset_id} creator={receipt.creator_id}")
    print(f"total_tokens={receipt.total_tokens}")


if __name__ == "__main__":
    main()
