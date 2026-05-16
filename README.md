
# DeepStream TrafficCamNet Accident Intelligence System

Production-style real-time traffic intelligence system using:
- NVIDIA DeepStream
- TrafficCamNet
- NvDCF Tracker
- NvDsAnalytics
- pyds metadata extraction
- Rule-based accident intelligence engine

## Features
- Real vehicle detection
- Vehicle classification
- Stable tracker IDs
- Trajectory history
- Speed estimation
- Sudden stop detection
- Near collision detection
- Congestion analysis
- Accident scoring
- Annotated output video
- Structured event logging

---

# REQUIREMENTS

## System
- Ubuntu / WSL2
- NVIDIA GPU
- CUDA
- Docker
- DeepStream 6.4

---

# DeepStream Container

```bash
docker pull nvcr.io/nvidia/deepstream:6.4-triton-multiarch

docker run --gpus all -it --rm \
-v $PWD:/workspace \
nvcr.io/nvidia/deepstream:6.4-triton-multiarch
```

---

# Inside Container

```bash
cd /workspace

apt update
apt install -y python3-pip python3-opencv

pip3 install -r requirements.txt
```

---

# Verify pyds

```bash
python3 app/verify_pyds.py
```

Expected:
```text
DeepStream bindings verified successfully
```

---

# Run

```bash
python3 -m app.main \
--input sample_videos/test.mp4 \
--output outputs/result.mp4 \
--events outputs/events.json
```

---

# Pipeline

Input
→ StreamMux
→ TrafficCamNet
→ NvDCF Tracker
→ NvDsAnalytics
→ Metadata Extraction
→ Accident Intelligence Engine
→ OSD Overlay
→ Encoder
→ Output MP4

---

# Output
outputs/result.mp4
outputs/events.json

