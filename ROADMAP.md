#  VidSnapAI Roadmap

Reels and Shorts generation moves incredibly fast. Below summarizes our internal logic upgrade goals pushing this tool directly towards professional cloud-platform capability.

### Q2 2026: Performance & Scalability
- [ ] **FastAPI Migration**: Upgrade from synchronous Flask to asynchronous FastAPI to support massive parallel API request handling seamlessly.
- [ ] **Real-Time Canvas Preview**: WebSockets implementation tracking visual states natively to allow browser-based preview maps cleanly checking AI visual outputs.
- [ ] **Cloud Storage Targets**: Integrate AWS S3 & Google Cloud storage buckets rather than forcing logic internally upon user_uploads/ mappings for large user volume limits.

### Q3 2026: Complex LLM Pipeline
- [ ] **Agentic Video Context Models**: Provide simple text strings allowing GPT-4 to autonomously fetch appropriate Pexels / Unsplash images autonomously bypassing manual user local uploads cleanly.
- [ ] **Multi-Voice Architecture Structure**: Switch arrays supporting bridging between ElevenLabs, Google TTS, and HF Coqui seamlessly providing diverse tonal logic.
- [ ] **Sentiment Pacing Algorithm**: Upgrade beat-sync variables to actively measure script "tone." Intense/Angry tones generate rapid durations. Calm tones dynamically swap durations toward slow transitions.

### Q4 2026: Pro Platform Deployment
- [ ] **Authentication Engine**: JWT-based session logic mapping outputs reliably tracking user generations logically to personal dashboard accounts.
- [ ] **Docker Engine Refactor**: Fully containerizing the entire build including strict internal FFmpeg compiling dependencies.
