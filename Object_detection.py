import os
import re
import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO
import datetime
import time
import torch
from multiprocessing import Pool, cpu_count

print(os.getcwd())

# Directories
video_processed_dir = 'Demo/02.video_processed/'
video_results_dir = 'Demo/03.video_results/'
traj_raw_dir = 'Demo/04.trajectory_raw/'

print('loaded directories')

# Annotators
c = sv.ColorLookup.TRACK
smoother = sv.DetectionsSmoother()
box_annotator = sv.RoundBoxAnnotator(thickness=2, color_lookup=c)
label_annotator = sv.LabelAnnotator(text_scale=0.5, color_lookup=c)
trace_annotator = sv.TraceAnnotator(thickness=2, trace_length=50, color_lookup=c)

# Callback function for frame processing
def get_callback(model, tracker, sink):
    def callback(frame: np.ndarray, index: int) -> np.ndarray:
        results = model(frame, imgsz=(736, 1280), verbose=False)[0]
        detections = sv.Detections.from_ultralytics(results)
        detections = detections[detections.class_id == 0]
        detections = detections[detections.confidence > 0.2]
        detections = tracker.update_with_detections(detections)
        sink.append(detections, {"frame_index": index})

        labels = [f"#{tracker_id}" for tracker_id in zip(detections.tracker_id)]
        annotated_frame = box_annotator.annotate(frame.copy(), detections=detections)
        annotated_frame = label_annotator.annotate(annotated_frame, detections=detections, labels=labels)
        return trace_annotator.annotate(annotated_frame, detections=detections)
    return callback

# Main video processing function
def process_video(args):
    source_path, model_name = args
    filename = os.path.basename(source_path)
    print(f"Processing {filename} with model {model_name}")

    video_info = sv.VideoInfo.from_video_path(source_path)
    target_path = os.path.join(video_results_dir, f"{filename[:-4]}_{model_name}.mp4")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)


    #Set bassed on your hardware and model availability!
    
    model = YOLO(f"{model_name}.pt")
    #device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu') 
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print('Device', device)
    model.to(device)

    tracker = sv.ByteTrack(
        track_activation_threshold=0.30,
        lost_track_buffer=125,
        minimum_matching_threshold=0.95,
        frame_rate=video_info.fps,
        minimum_consecutive_frames=3
    )
    tracker.reset()

    start_time = time.time()
    print(f"Started processing {filename}")

    csv_path = os.path.join(traj_raw_dir, f"{filename[:-4]}_{model_name}.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with sv.CSVSink(csv_path) as sink:
        sv.process_video(
            source_path,
            target_path,
            callback=get_callback(model, tracker, sink)
        )

    end_time = time.time()
    print(f"Finished {filename} in {end_time - start_time:.2f} seconds. Saved to {target_path}")

print('before entry')

# Entry point
if __name__ == "__main__":
    model = 'yolov10l_final' 
    print('model:', model)
    video_tasks = []
    print("video-processed_dir", video_processed_dir)
    for root, dirs, files in os.walk(video_processed_dir):
        print(root)
        for name in files:
            if name.endswith(".mp4"):
                full_path = os.path.join(root, name)
                video_tasks.append((full_path, model))

    num_processes = min(6, cpu_count())  # Adjust based on your GPU capacity
    print(f"Starting parallel processing with {num_processes} processes...")
    print(video_tasks)

    with Pool(processes=num_processes) as pool:
        pool.map(process_video, video_tasks)
