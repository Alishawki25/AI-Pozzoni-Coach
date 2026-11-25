import os
import sys
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import multiprocessing

# --- IMPORT YOUR AI BRAIN HERE ---
from pose_extractor import process_video

# --- 1. INITIALIZE APP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. THE UPLOAD & ANALYSIS ENDPOINT ---
@app.post("/upload")
async def upload_video(file: UploadFile = File(...), target_side: str = Form(...)):
    try:
        base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
        video_path = os.path.join(base_path, "temp_video.mp4")

        with open(video_path, "wb") as buffer:
            buffer.write(await file.read())

        print(f"Analyzing {video_path} for side: {target_side}...")
        
        # --- TRIGGER THE IMPORTED AI BRAIN ---
        result = process_video(video_path, 'top', target_side.lower())

        if result["status"] == "success":
            report_path = result["report_path"]
            if os.path.exists(report_path) and os.path.getsize(report_path) > 0:
                return FileResponse(
                    path=report_path,
                    filename="AI_Pozzoni_Report.pdf",
                    media_type='application/pdf'
                )
            else:
                raise HTTPException(status_code=500, detail="PDF generation failed or file is empty.")
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        print(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- 3. SERVE THE REACT WEBSITE ---
if os.path.exists("build"):
    app.mount("/static", StaticFiles(directory="build/static"), name="static")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        file_path = os.path.join("build", full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse("build/index.html")

# --- 4. START THE SERVER ---
if __name__ == "__main__":
    multiprocessing.freeze_support() 
    
    try:
        print("\n" + "="*50)
        print("🚀 AI POZZONI SERVER STARTING...")
        print("URL: http://127.0.0.1:8000")
        print("="*50 + "\n")
        
        uvicorn.run(app, host="127.0.0.1", port=8000)
        
    except Exception as e:
        print("\n" + "!"*50)
        print("🚨 CRITICAL ERROR PREVENTED CRASH")
        print(f"Error: {e}")
        print("!"*50 + "\n")
        input("Press Enter to close this window...")