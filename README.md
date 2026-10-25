The dataset released here is a sample. The full release is held back for now because of anonymity, and the complete files are too large. It will be made public later.

BotSpan dataset is in the `data` folder:
Timelines are in `timelines/{sample_id}.jsonl`.
Each event has `event_time`, `event_id`, `action`, `targets`, and `text`.
`samples.jsonl` gives `sample_id`, `split`, and `account_id`.
Labels are in `labels.jsonl`.

`history/{account_id}.jsonl` is that account's human history, in the same line order as the original cache. It is used only to build the personal anchor, and must not be used as features.

Human timelines in this dataset are drawn from the Cresci-17 dataset. The official release is the dataset page: https://botometer.osome.iu.edu/bot-repository/datasets.html

This paper releases the data-synthesis code and our method LCD in `lcd/`. It is provided for research only, so that detection methods can be studied and compared. Do not use it to synthesize bots for deployment, spam, impersonation, or any other malicious purpose. Researchers may change the configuration or the generator for further research.
