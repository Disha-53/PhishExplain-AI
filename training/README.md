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

A rules-based URL analyzer is used instead of a large trained model for interpretability. This remains transparent and local.
