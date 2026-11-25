# AI Pozzoni Padel Coach

An AI coaching tool for padel. Upload a court video, choose which player to track, and get a
biomechanical PDF report that flags risky or inefficient arm and leg positions, with the
timestamp and a snapshot of each one.

Built as a graduation project at the Arab Open University (AOU).

**Demo video:** [`sample_video.mp4`](sample_video.mp4) is a sample court recording you can run through the app.

## How it works

1. **Upload**: the React web app sends the video and the chosen player (left or right) to the backend.
2. **Isolate the player**: `pose_extractor.py` crops each frame to the tracked player's zone. It
   removes the left 10% of the frame, keeps the top half of the court, and keeps the chosen side,
   overlapping the middle by 10% so the player is not lost when crossing it.
3. **Pose estimation**: Google **MediaPipe Pose** (model complexity 2) finds 3D body landmarks on every frame.
4. **Joint angles**: it computes the 3D angle at the right elbow (shoulder, elbow, wrist) and the right
   knee (hip, knee, ankle), smoothed over the last 5 frames.
5. **Fault detection**: angles outside the safe range are flagged:

   | Joint | Safe range | Below range | Above range |
   |---|---|---|---|
   | Elbow | 45° to 181° | Arm jammed too close to body (loss of power) | Arm locked (joint damage risk) |
   | Knee | 90° to 181° | Over-crouched (center of gravity too low) | Stiff legs (losing power) |

6. **Report**: an `AI_Pozzoni_Report.pdf` is generated with each violation, its timestamp, and an
   annotated skeleton snapshot. The browser shows it when it is ready.

## Tech stack

- **Backend:** Python, FastAPI, Uvicorn
- **Computer vision:** MediaPipe Pose, OpenCV, NumPy
- **Report:** FPDF
- **Frontend:** React (Create React App)
- **Desktop build:** PyInstaller (a single Windows `.exe` that serves the web app at `http://127.0.0.1:8000`)

## Project structure

```
├── main.py              # FastAPI server: /upload endpoint + serves the React build
├── pose_extractor.py    # The AI part: cropping, pose estimation, angles, faults, PDF report
├── requirements.txt     # Python dependencies
├── sample_video.mp4     # Sample court video for trying the app
└── pozzoni-app/         # React frontend
    ├── public/          # Logos and background
    └── src/App.js       # Upload page, player picker, progress bar, PDF viewer
```

## Download (Windows, no setup)

Download the ready-to-run app from the [**Releases**](../../releases) page. Unzip it, run
`AI_Pozzoni_Coach.exe`, then open **http://127.0.0.1:8000** in your browser.

## Run from source

**Requirements:** Python 3.11 and Node.js 18 or newer.

```bash
# 1. Build the frontend
cd pozzoni-app
npm install
npm run build
cd ..

# 2. Copy the build next to main.py (the server serves ./build)
#    Windows PowerShell:  Copy-Item -Recurse pozzoni-app\build .\build
#    macOS / Linux:       cp -r pozzoni-app/build ./build

# 3. Install the Python dependencies and start the server
pip install -r requirements.txt
python main.py
```

Open **http://127.0.0.1:8000**, upload a court video, choose the player, and click analyze.
While it processes, a live preview window shows the tracked skeleton. Press `q` to stop early.

## Limitations

- It tracks the **top half** of the court and the player's **right** arm and leg.
- The crop zones assume a fixed camera angle like the one used during development.
- The angle thresholds are coaching heuristics, not medical advice.

## Author

**Ali Shawki**, Arab Open University (AOU)

## License

[MIT](LICENSE) © 2026 Ali Shawki
