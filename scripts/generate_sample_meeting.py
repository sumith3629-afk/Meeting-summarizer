import os
from pathlib import Path
import win32com.client

output_dir = Path("sample_data")
output_dir.mkdir(exist_ok=True)
output_path = output_dir / "sample_meeting.wav"

dialogue = [
    (0, "Good morning everyone. Welcome to our weekly backend engineering sync. Today we need to address our high P99 latency spikes, review our database scaling options, and assign owners for the upcoming release."),
    (1, "Thanks David. Looking at our recent production telemetry, our response times degraded by 45 percent during peak hours. Rahul suggested yesterday that we migrate our primary data store to MongoDB, but after reviewing the consistency trade-offs, we must stick with PostgreSQL. The relational schema is critical for our transactional ledger."),
    (0, "Agreed. So let us record that as a decision: we are definitely sticking with PostgreSQL and will not migrate to MongoDB this quarter. Regarding the latency issue, what is our plan?"),
    (1, "Alex proposed rewriting our microservices communication layer from REST to gRPC. While gRPC is faster, we do not have enough benchmark data yet to make that switch right now. Instead, adding a Redis cache in front of our read-heavy endpoints will immediately bring our P99 latency back under 120 milliseconds."),
    (0, "That makes complete sense. We will defer any decision on gRPC until after benchmarking. But the Redis caching layer is approved. Zira, can you take ownership of implementing that Redis cache layer?"),
    (1, "Yes, I will implement and test the Redis cache cluster by this Friday, October 10th."),
    (0, "Perfect. Another item: Rahul is assigned to configure Prometheus alerts and Grafana dashboards for our Kubernetes pods before next Tuesday, October 14th."),
    (1, "Understood. Also, we noticed that our old Docker Compose configs and dead environment variables are cluttering the repository. Someone really needs to clean up the legacy Docker files and documentation, but we haven't assigned who will do it yet."),
    (0, "Right, we will figure out who handles that cleanup later. Lastly, Alex is tasked with drafting the automated load testing plan, though we haven't fixed a deadline for that yet. Let us wrap up here and get to work.")
]

speaker = win32com.client.Dispatch("SAPI.SpVoice")
voices = speaker.GetVoices()

# Open file stream for writing
stream = win32com.client.Dispatch("SAPI.SpFileStream")
# 39 = SAFT44kHz16BitMono
stream.Open(str(output_path.resolve()), 3, False)
speaker.AudioOutputStream = stream

for voice_idx, text in dialogue:
    idx = voice_idx if voice_idx < voices.Count else 0
    speaker.Voice = voices.Item(idx)
    speaker.Rate = 0  # Normal speed
    speaker.Speak(text)

stream.Close()
print(f"Sample meeting audio generated successfully: {output_path} ({output_path.stat().st_size} bytes)")
