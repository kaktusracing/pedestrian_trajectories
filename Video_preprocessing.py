import cv2
import os
import datetime


# === CONFIGURATION ===
input_path = 'Demo/01.video_raw/'
output_path = 'Demo/02.video_processed/'

start_time_sec = 0  # Start time in seconds
end_time = 10   # End time in seconds
duration_min = (end_time-start_time_sec)/60
duration_sec = end_time-start_time_sec
new_width, new_height = 1280, 720  # New resolution (width, height)
new_fps = 15    # New frame rate

# === LOAD VIDEO ===


def process_video(cap, output_path, start_time_sec, new_width, new_height, new_fps):
    # === SEEK TO START TIME ===
    cap.set(cv2.CAP_PROP_POS_MSEC, start_time_sec * 1000)

    # === SETUP VIDEO WRITER ===
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, new_fps, (new_width, new_height))

    # === TIMING SETUP ===
    target_frame_interval_ms = 1000 / new_fps
    end_time_ms = (start_time_sec + duration_sec) * 1000
    next_frame_time = start_time_sec * 1000

    while cap.get(cv2.CAP_PROP_POS_MSEC) < end_time_ms:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = cap.get(cv2.CAP_PROP_POS_MSEC)
        if current_time >= next_frame_time:
            # === GPU ACCELERATION (optional) ===
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                gpu_frame = cv2.cuda_GpuMat()
                gpu_frame.upload(frame)
                gpu_resized = cv2.cuda.resize(gpu_frame, (new_width, new_height))
                resized = gpu_resized.download()
            else:
                resized = cv2.resize(frame, (new_width, new_height))

            out.write(resized)
            next_frame_time += target_frame_interval_ms

    cap.release()
    out.release()
    print("Video processing complete.")
    now = datetime.datetime.now()
    print('End time:', now.strftime("%Y-%m-%d %H:%M:%S"))


print('Input_path:', input_path)

for root, dirs, files in os.walk(input_path):
    for name in files:
        print('filename: ', name)
        if name.endswith((".mp4")):
            # Get the current date and time
            now = datetime.datetime.now()
            print('starttime: ', now.strftime("%Y-%m-%d %H:%M:%S"))
            filename = os.fsdecode(name)
            print("filename:", filename)
            file_dir = os.path.join(root+ '/' + filename)
            print('directories:',file_dir)

            cap = cv2.VideoCapture(file_dir)
            if not cap.isOpened():
                raise IOError("Cannot open video file")

            original_fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            
            try:
                print(original_fps)
                current_length = frame_count/original_fps   
                print(current_length)
            except:
                print('No video_ERROR')
                break
            print('curent_length:', current_length)  
            
            
            output_file = os.path.join(output_path + '/' + filename[:-4]+ '_' + str(new_fps) + '_' + str(int(duration_sec)) +'sec_HD.mp4')
            print('out:', output_file)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            print('output: ', output_file)
            process_video(cap, output_file, start_time_sec, new_width, new_height, new_fps)
            # Get the current date and time
            now = datetime.datetime.now()
            print('endtime: ', now.strftime("%Y-%m-%d %H:%M:%S"))