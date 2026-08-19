# Dataset Strategy

The repository does not include downloaded datasets. Raw and processed data are
ignored by Git. The preprocessing and training commands must be run locally
after each source has been obtained and its usage terms reviewed.

| Dataset | Use | Status and access | Expected location |
|---|---|---|---|
| Enron Email Corpus | Legitimate email text | Hugging Face dataset page was not machine-readable during verification. Inspect the actual schema before use; do not assume a loader column name. | `data/raw/enron/` |
| Nazario Phishing Corpus | Phishing email text | Public mbox files are listed at `http://monkey.org/~jose/phishing/`; the current downloader uses the published `phishing-2024` file. Review `README.txt` and `LICENSE.txt`. | `data/raw/nazario/` |
| AI-Generated Phishing Detection | Optional AI-generated phishing evaluation | The cited GitHub URL returned HTTP 404 on 2026-08-19. It is not used or replaced silently. | `data/raw/ai_generated/` |
| Spam/Genuine Mail Dataset | Optional supplemental comparison | Kaggle page describes 100,000 synthetic realistic records, with 0=ham and 1=spam, Apache-2.0, and requires Kaggle sign-in/API credentials. It is not downloaded automatically. | `data/raw/spam_genuine/` |
| PhiUSIIL Phishing URL | URL model training | UCI dataset 967 was downloaded and verified locally during this implementation. Label 1 is legitimate and 0 is phishing; it contains 235,795 published rows and 54 fields. | `data/raw/phiusiil/` |
| ISCX-URL2016 | External URL validation | UNB publishes category descriptions and a download link. Access and archive format must be verified manually before ingestion. | `data/raw/iscx_url2016/` |

## Text labels

The first unified text task is binary: `0=LEGITIMATE` and `1=MALICIOUS`.
The current ingestion maps ham, genuine, legitimate, and safe to 0, and spam,
phishing, and malicious to 1. AI-generated phishing is not assigned a special
class until a verified dataset with an explicit label is available.

## Download commands

```powershell
python scripts/download_datasets.py nazario
python scripts/download_datasets.py phiusiil
```

For Kaggle, configure the Kaggle CLI using environment-managed credentials and
download manually into `data/raw/spam_genuine/`. Never commit `kaggle.json` or
API keys. Enron and ISCX-URL2016 require schema inspection before adding a
source-specific adapter.

## Usage and licensing

Dataset licenses and terms belong to their respective publishers. Keep source
attribution and license files beside manually downloaded data. No dataset is
claimed as downloaded until the local files are present and preprocessing has
verified their schema.