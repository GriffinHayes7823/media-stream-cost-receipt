from types import SimpleNamespace

from media_cost_service import DeliveryRequest, MediaAsset, deliver_media


class FakeEmbeddings:
    def create(self, **kwargs):
        assert kwargs == {"model": "auto", "input": "A short clip transcript."}
        return SimpleNamespace(usage=SimpleNamespace(total_tokens=7))


class FakeCompletions:
    def create(self, **kwargs):
        assert kwargs["model"] == "auto"
        assert kwargs["messages"][0]["content"].startswith("Creator c-1 needs asset a-1.")
        return SimpleNamespace(
            usage=SimpleNamespace(total_tokens=11),
            choices=[SimpleNamespace(message=SimpleNamespace(content="Delivered note"))],
        )


class FakeClient:
    embeddings = FakeEmbeddings()
    chat = SimpleNamespace(completions=FakeCompletions())


def test_delivery_receipt_sums_ingestion_and_processing_tokens():
    request = DeliveryRequest(
        creator_id="c-1",
        asset=MediaAsset(asset_id="a-1", transcript="A short clip transcript."),
        instruction="Summarize it.",
    )
    receipt = deliver_media(request, FakeClient())
    assert receipt.text == "Delivered note"
    assert receipt.total_tokens == 18
    assert [call.capability for call in receipt.calls] == ["embeddings", "chat.completions"]
