# Interview_project
creating a project that an ai who takes an interview

voice-interview-ai/
│
├── app.py
├── config.py
│
├── routes/
│   ├── interview.py
│   ├── audio.py
│   └── analysis.py
│
├── services/
│   ├── whisper_service.py
│   ├── adaptive_engine.py
│   ├── quick_scoring.py
│   └── question_selector.py
│
├── models/
│   ├── interview.py
│   ├── question.py
│
├── utils/
│   └── audio_features.py
│
├── storage/
│   └── audio/
│
└── data/
    └── questions.json


NEW ARCHITECTURE VIA DOCKER 
voice-interview-system/
│
├── docker-compose.yml
│
├── flask_app/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── routes/
│       └── health.py
│
├── whisper_worker/
│   ├── Dockerfile
│   ├── worker.py
│   └── requirements.txt
│
└── nginx/
    └── nginx.conf   (empty for now)

