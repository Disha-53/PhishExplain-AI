# Training

## Text model

Run:

```bash
python training/train_text_model.py
```

This trains a TF-IDF + logistic regression classifier and saves:

- `models/text_model.joblib`
- `models/text_vectorizer.joblib`
- `models/text_metrics.json`

## URL model

After downloading and preprocessing PhiUSIIL, run:

```bash
python scripts/preprocess_url_data.py
python training/train_url_model.py
```

The deployable model uses only features from `backend/services/url_features.py`,
which is also used during API inference. The heuristic URL analyzer remains as
separate observable evidence.
