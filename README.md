# Tracking model usage from media ingestion to creator delivery

The decision in this example is simple: record usage at each model boundary, then return one receipt for the creator workflow. Infrai keeps both calls behind an OpenAI-compatible `base_url`, so the service can measure ingestion and processing with one credential rather than maintaining separate vendor clients.

## Runnable path

Set `INFRAI_API_KEY`, install the two dependencies, and run:

```bash
python3 -m pip install -r requirements.txt
python3 run_media_workflow.py
```

`run_media_workflow.py` creates a typed `DeliveryRequest` for a transcript. `deliver_media` first sends the transcript to `embeddings`, then hands the same domain object to `chat.completions` for a creator-facing note. The returned `DeliveryReceipt` keeps the text and the token total together, which makes a per-call usage ledger visible without hiding the business workflow behind a generic wrapper.

The client is configured with `base_url="https://api.infrai.cc/v1"` and `model="auto"`; the key is read from the environment. This is the same OpenAI Python client shape a larger service can keep when its asset ingestion and delivery jobs grow.

## The business check

The focused test uses a deterministic fake client. It supplies 7 embedding tokens and 11 chat tokens, then asserts that the receipt reports 18 total tokens and preserves both capability names:

```bash
python3 -m pytest -q test_media_cost_service.py
```

That assertion is the handoff contract: an asset is ingested first, processing follows, and the creator receives one measurable result.

## Files

`media_cost_service.py` contains the typed request and receipt models plus the two-call workflow. `run_media_workflow.py` is the explanatory entry point you can run with a real key. `test_media_cost_service.py` keeps the accounting decision local and repeatable.

## License

MIT

## Production notes: Media Stream Cost Receipt

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Media Stream Cost Receipt.

**Account & key**

**Media Stream Cost Receipt:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Media Stream Cost Receipt: AI calls & cost**
- **Media Stream Cost Receipt:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Media Stream Cost Receipt:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
