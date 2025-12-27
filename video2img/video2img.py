import cv2
import os

def extract_frames(video_path, output_folder, fps=None, start_time=0, end_time=None):
    """
    將影片分解成多個 frame 圖片
    
    參數:
    - video_path: 影片檔案路徑 (str)
    - output_folder: 儲存 frame 的資料夾路徑 (str)
    - fps: 每秒儲存幾張 (None = 使用影片原始 fps)
    - start_time: 開始時間（秒），預設 0
    - end_time: 結束時間（秒），None = 到影片結尾
    """
    # 建立輸出資料夾
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 開啟影片
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("錯誤：無法開啟影片檔案")
        return

    # 取得影片資訊
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / original_fps if original_fps > 0 else 0
    
    print(f"影片長度: {duration:.2f} 秒")
    print(f"原始 FPS: {original_fps:.2f}")
    print(f"總幀數: {total_frames}")

    # 決定儲存間隔
    target_fps = fps if fps is not None else original_fps
    frame_interval = int(original_fps / target_fps) if fps else 1  # 每幾幀存一張

    # 設定開始與結束 frame
    start_frame = int(start_time * original_fps)
    end_frame = int(end_time * original_fps) if end_time else total_frames

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)  # 跳到開始位置

    saved_count = 0
    current_frame = start_frame

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or current_frame > end_frame:
            break

        # 只在指定間隔儲存
        if (current_frame - start_frame) % frame_interval == 0:
            filename = f"frame_{saved_count}.jpg"
            filepath = os.path.join(output_folder, filename)
            cv2.imwrite(filepath, frame)
            saved_count += 1
            print(f"儲存: {filepath}")

        current_frame += 1

    cap.release()
    print(f"\n完成！共儲存 {saved_count} 張圖片到 {output_folder}")


# ==================== 使用範例 ====================
if __name__ == "__main__":
<<<<<<< HEAD
    video_file = "/home/waynelee0124/aoop_2025_group7_TBC/video2img/Screencast from 12-26-2025 04_45_38 PM.mp4"          # 你的影片檔名
    output_dir = "/home/waynelee0124/aoop_2025_group7_TBC/video2img/output_frames"            # 輸出的資料夾
=======
    video_file = "./rotate_egg.mp4"          # 你的影片檔名
    output_dir = "./gacha_rotate"            # 輸出的資料夾
>>>>>>> c320692cd362048ea28643e5fc113de066343ec1

    # 範例1：完整影片，使用原始 FPS 存所有 frame
    # extract_frames(video_file, output_dir)

    # 範例2：每秒存 1 張（適合做縮圖或分析）
    extract_frames(video_file, output_dir, fps=2)

    # 範例3：只取前 10 秒，每秒 2 張
    # extract_frames(video_file, output_dir, fps=2, start_time=0, end_time=10)

    # 範例4：從 30 秒到 60 秒，每秒 5 張
    # extract_frames(video_file, output_dir, fps=5, start_time=30, end_time=60)