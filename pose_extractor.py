import cv2
import numpy as np
import os
from fpdf import FPDF
from collections import deque

# Bypass the Windows loading bug
import mediapipe.python.solutions.pose as mp_pose
import mediapipe.python.solutions.drawing_utils as mp_drawing

# ==========================================
# ⚙️ SYSTEM SETTINGS
# ==========================================
TARGET_HALF = 'top'    

ELBOW_MAX_SAFE = 181   
ELBOW_MIN_SAFE = 45    
KNEE_MAX_SAFE = 181    
KNEE_MIN_SAFE = 90     

SMOOTHING_FRAMES = 5
# ==========================================

def calculate_angle_3d(a, b, c):
    a = np.array(a) 
    b = np.array(b) 
    c = np.array(c) 
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine_angle))
    return angle

def generate_pdf_report(elbow_fault, knee_fault, elbow_angle, knee_angle, elbow_time, knee_time, elbow_img_path, knee_img_path, output_path, target_half, target_side):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size=18, style="B")
    pdf.cell(200, 10, txt="AI Pozzoni - Biomechanical Report", ln=True, align='C')
    pdf.set_font("Arial", size=12, style="I")
    pdf.cell(200, 10, txt=f"Tracking: {target_half.upper()} {target_side.upper()} Player", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(200, 10, txt="Upper Body Mechanics (Right Arm)", ln=True)
    pdf.set_font("Arial", size=12)
    
    if elbow_fault:
        pdf.cell(200, 8, txt=f"VIOLATION DETECTED: Arm reached {int(elbow_angle)} degrees at {elbow_time}", ln=True)
        if elbow_angle > ELBOW_MAX_SAFE:
            pdf.cell(200, 8, txt="- FAULT: Arm completely locked. Joint damage risk.", ln=True)
        else:
            pdf.cell(200, 8, txt="- FAULT: Arm jammed too close to body. Loss of power.", ln=True)
    else:
        pdf.cell(200, 8, txt="Status: SAFE", ln=True)
        pdf.cell(200, 8, txt="- No dangerous extensions or compressions detected.", ln=True)
        
    pdf.ln(5)

    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(200, 10, txt="Lower Body Mechanics (Right Leg)", ln=True)
    pdf.set_font("Arial", size=12)
    
    if knee_fault:
        pdf.cell(200, 8, txt=f"VIOLATION DETECTED: Knee reached {int(knee_angle)} degrees at {knee_time}", ln=True)
        if knee_angle > KNEE_MAX_SAFE:
            pdf.cell(200, 8, txt="- FAULT: Stiff legs. Player is sacrificing power.", ln=True)
        else:
            pdf.cell(200, 8, txt="- FAULT: Over-crouched. Dropping center of gravity too low.", ln=True)
    else:
        pdf.cell(200, 8, txt="Status: SAFE", ln=True)
        pdf.cell(200, 8, txt="- No dangerous extensions or compressions detected.", ln=True)
        
    pdf.ln(5)
    
    if elbow_fault and os.path.exists(elbow_img_path):
        pdf.set_font("Arial", size=10, style="I")
        pdf.cell(200, 10, txt=f"Visual 1: Arm Violation (Timestamp: {elbow_time})", ln=True)
        pdf.image(elbow_img_path, x=25, y=None, w=120)
        pdf.ln(2)
        
    if knee_fault and os.path.exists(knee_img_path):
        pdf.set_font("Arial", size=10, style="I")
        pdf.cell(200, 10, txt=f"Visual 2: Leg Violation (Timestamp: {knee_time})", ln=True)
        pdf.image(knee_img_path, x=25, y=None, w=120)
        
    pdf.output(output_path)
    
    try:
        if os.path.exists(elbow_img_path): os.remove(elbow_img_path)
        if os.path.exists(knee_img_path): os.remove(knee_img_path)
    except Exception:
        pass

    return output_path

def process_video(video_path, target_half, target_side):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return {"status": "error", "message": f"Could not open video file {video_path}"}

    base_dir = os.path.dirname(video_path)
    elbow_snap = os.path.join(base_dir, "elbow_snap.jpg")
    knee_snap = os.path.join(base_dir, "knee_snap.jpg")
    pdf_filename = os.path.join(base_dir, "AI_Pozzoni_Report.pdf")

    person_detected = False
    elbow_fault_detected = False
    knee_fault_detected = False
    
    elbow_fault_angle = 0
    knee_fault_angle = 0
    elbow_time = "0:00"
    knee_time = "0:00"

    elbow_history = deque(maxlen=SMOOTHING_FRAMES)
    knee_history = deque(maxlen=SMOOTHING_FRAMES)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            current_time_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            time_formatted = f"{int(current_time_sec // 60)}:{int(current_time_sec % 60):02d}"

            # === 1. GLOBAL GARDEN BLINDFOLD ===
            # We chop off the left 10% of the raw video before doing ANY math
            orig_height, orig_width = frame.shape[:2]
            garden_crop_x = int(orig_width * 0.10)
            frame = frame[:, garden_crop_x:] # The garden is permanently deleted from the frame!

            # Now we get the new dimensions of our clean, garden-free court
            height, width = frame.shape[:2]
            
            # === 2. THE 45% NET SPLIT (Bottom blindfold) ===
            y_middle = int(height * 0.50) 
            
            if target_half == 'top':
                y1, y2 = 0, y_middle
            else:
                y1, y2 = y_middle, height

            # === 3. THE PERFECT 50/50 SPLIT (With overlap) ===
            if target_side == 'left':
                x1 = 0  
                x2 = int(width * 0.60) # Reaches 10% past the middle so it doesn't lose the player 
            else:
                x1 = int(width * 0.40) # Reaches 10% past the middle the other way
                x2 = width

            player_cam = frame[y1:y2, x1:x2]

            image_rgb = cv2.cvtColor(player_cam, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    person_detected = True
                    
                    shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z]
                    elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].z]
                    wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].z]
                    
                    hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].z]
                    knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].z]
                    ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].z]
                    
                    raw_elbow_angle = calculate_angle_3d(shoulder, elbow, wrist)
                    raw_knee_angle = calculate_angle_3d(hip, knee, ankle)

                    elbow_history.append(raw_elbow_angle)
                    knee_history.append(raw_knee_angle)

                    smoothed_elbow = sum(elbow_history) / len(elbow_history)
                    smoothed_knee = sum(knee_history) / len(knee_history)

                    mp_drawing.draw_landmarks(image_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    
                    if smoothed_elbow > ELBOW_MAX_SAFE or smoothed_elbow < ELBOW_MIN_SAFE:
                        elbow_fault_detected = True
                        elbow_fault_angle = smoothed_elbow
                        elbow_time = time_formatted 
                        cv2.imwrite(elbow_snap, image_bgr) 

                    if smoothed_knee > KNEE_MAX_SAFE or smoothed_knee < KNEE_MIN_SAFE:
                        knee_fault_detected = True
                        knee_fault_angle = smoothed_knee
                        knee_time = time_formatted 
                        cv2.imwrite(knee_snap, image_bgr) 
                            
            except AttributeError:
                pass

            cv2.imshow("AI Pozzoni - Live Analysis Preview", image_bgr)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows() 
    
    if person_detected:
        final_pdf = generate_pdf_report(elbow_fault_detected, knee_fault_detected, elbow_fault_angle, knee_fault_angle, elbow_time, knee_time, elbow_snap, knee_snap, pdf_filename, target_half, target_side)
        return {"status": "success", "report_path": final_pdf}
    else:
        return {"status": "error", "message": "No person detected in the tracking zone."}