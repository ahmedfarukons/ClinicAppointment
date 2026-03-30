# ChatDoctor - Klinik AI Asistanı

Klinik web asistanı: Intent Router + RAG (Qdrant) + Randevu Ajanı + Explainable AI (XAI).

## Mimari

```
Hasta Sorusu
     |
Intent Classifier (medical_info / appointment_request / escalation)
     |                    |                     |
RAG Pipeline        Randevu Ajanı         Acil Yönlendirme
(Qdrant + LLM)     (slot-filling)        (112 / acil servis)
     |                    |                     |
     +-------- XAI Explanation -----------------+
     (decision_path, feature_contributions, retrieval_quality, sources, confidence)
```

## Kurulum

```bash
pip install -r requirements.txt
```

## Ortam Degiskenleri

`.env.example` dosyasini `.env` olarak kopyalayip GROQ_API_KEY'i ekleyin:

```bash
cp .env.example .env
```

| Degisken | Aciklama | Varsayilan |
|---|---|---|
| `GROQ_API_KEY` | Groq API anahtari (free tier yeterli) | (bos = fallback mod) |
| `EMBEDDING_MODEL` | Sentence-transformers modeli | `all-MiniLM-L6-v2` |
| `LLM_MODEL` | Groq LLM modeli | `llama-3.1-8b-instant` |
| `QDRANT_PATH` | Yerel Qdrant veri dizini | `./qdrant_data` |
| `COLLECTION_NAME` | Qdrant koleksiyon adi | `chatdoctor` |

## Veri Yukleme (Ingestion)

ChatDoctor dataset'ini Kaggle'dan indirip Qdrant'a yukler:

```bash
python -m scripts.ingest                     # tam dataset
python -m scripts.ingest --limit 500         # hizli test icin 500 satir
python -m scripts.ingest --csv dosya.json    # yerel dosya
```

## API Calistirma

```bash
uvicorn app.main:app --reload
```

## Endpointler

- `GET  /health` - saglik kontrolu
- `POST /chat`   - ana sohbet endpoint'i

### Ornek Istek

```json
{
  "message": "I have a severe headache and dizziness"
}
```

### Ornek Cevap (XAI dahil)

```json
{
  "answer": "Sorunuza en yakin kaynak bilgisi ...",
  "route": "medical_info",
  "xai": {
    "route": "medical_info",
    "confidence": 0.48,
    "rationale": "Mesaj bilgilendirme talebi olarak siniflandirildi ...",
    "decision_path": [
      {"step": "red_flag_check", "outcome": "clear", "detail": "..."},
      {"step": "appointment_keyword_check", "outcome": "clear", "detail": "..."},
      {"step": "default_route", "outcome": "medical_info", "detail": "..."},
      {"step": "rag_retrieval", "outcome": "3 sources found", "detail": "Top score: 0.58"},
      {"step": "llm_generation", "outcome": "answer_generated", "detail": "..."}
    ],
    "feature_contributions": {"token_weight:headache": 0.14},
    "sources": [
      {"id": "700", "title": "ChatDoctor row 267", "snippet": "...", "score": 0.58}
    ],
    "retrieval_quality": {
      "avg_score": 0.55,
      "max_score": 0.58,
      "min_score": 0.52,
      "source_count": 3.0
    },
    "safety_note": "Bu sistem bilgilendirme amaclidir, doktor muayenesinin yerine gecmez."
  }
}
```

## RAGAS Degerlendirme

```bash
python -m scripts.evaluate_ragas --samples 10
```

## XAI (Explainable AI) Ozellikleri

Her cevap su aciklanabilirlik alanlarini icerir:

| Alan | Aciklama |
|---|---|
| `decision_path` | Sistemin izledigi adimlar (red_flag_check, routing, retrieval, generation) |
| `feature_contributions` | Hangi kelimeler/sinyaller karara ne kadar etki etti |
| `retrieval_quality` | Retrieval metrikleri (avg/max/min skor, kaynak sayisi) |
| `sources` | Kullanilan kaynaklar ve benzerlik skorlari |
| `confidence` | Genel guven skoru (0-1 arasi) |
| `safety_note` | Zorunlu medikal uyari |

## Teknoloji Stack

- **FastAPI** - Backend API
- **Qdrant** - Vector store (yerel, sunucusuz mod)
- **sentence-transformers** - Embedding (all-MiniLM-L6-v2)
- **LangChain + Groq** - LLM entegrasyonu
- **RAGAS** - RAG kalite degerlendirmesi
- **Pydantic** - Veri modelleme ve validasyon
