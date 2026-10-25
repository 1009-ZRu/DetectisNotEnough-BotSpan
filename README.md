BotSpan dataset is in the `data` folder:
Timelines are in `timelines/{sample_id}.jsonl`.
Each event has `event_time`, `event_id`, `action`, `targets`, and `text`.
`samples.jsonl` gives `sample_id`, `split`, and `account_id`.
Labels are in `labels.jsonl`.

`history/{account_id}.jsonl` is that account's human history, in the same line order as the original cache. It is used only to build the personal anchor, and must not be used as features.
