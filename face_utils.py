import cv2
import os
import time
import numpy as np
import face_recognition

FACES_DIR = os.path.join('assets', 'faces')
os.makedirs(FACES_DIR, exist_ok=True)

def capture_face_samples(student_id, num_samples=30):
    save_dir = os.path.join(FACES_DIR, str(student_id))
    os.makedirs(save_dir, exist_ok=True)

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Cannot open camera")
        return False

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    count = 0
    cv2.namedWindow("Register Face - Move head, press Q to quit")

    while count < num_samples:
        ret, frame = cam.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            count += 1
            face_img = frame[y:y+h, x:x+w]
            img_path = os.path.join(save_dir, f"{count}.jpg")
            cv2.imwrite(img_path, face_img)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
            break
        cv2.putText(frame, f"Images Captured: {count}/{num_samples}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2)
        cv2.imshow("Register Face - Move head, press Q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.1)
    cam.release()
    cv2.destroyAllWindows()
    return count >= num_samples

def load_known_faces():
    known_encodings = []
    student_ids = []
    for student_folder in os.listdir(FACES_DIR):
        folder_path = os.path.join(FACES_DIR, student_folder)
        if not os.path.isdir(folder_path):
            continue
        for img_file in os.listdir(folder_path):
            img_path = os.path.join(folder_path, img_file)
            img = face_recognition.load_image_file(img_path)
            encs = face_recognition.face_encodings(img)
            if len(encs) > 0:
                known_encodings.append(encs[0])
                student_ids.append(student_folder)
    return known_encodings, student_ids

def recognize_face_and_mark(known_encodings, student_ids, already_marked, on_recognized, stop_callback):
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Cannot open camera")
        return
    
    cv2.namedWindow("Face Attendance - Press Q to stop")
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locs = face_recognition.face_locations(rgb_small)
        face_encs = face_recognition.face_encodings(rgb_small, face_locs)
        
        for face_encoding, face_location in zip(face_encs, face_locs):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None
            name = "Unknown"
            student_id = None
            
            if best_match_index is not None and matches[best_match_index]:
                student_id = student_ids[best_match_index]
                if student_id not in already_marked:
                    on_recognized(student_id)
                    already_marked.add(student_id)
                name = f"ID: {student_id}"
            
            top, right, bottom, left = face_location
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0) if name!="Unknown" else (0,0,255), 2)
            cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0) if name!="Unknown" else (0,0,255), 2)
        
        cv2.putText(frame, f"Press Q to finish", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (150, 0, 0), 2)
        cv2.imshow("Face Attendance - Press Q to stop", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if stop_callback():
            break
    
    cam.release()
    cv2.destroyAllWindows()