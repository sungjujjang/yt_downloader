from pystray import MenuItem, Icon
from PIL import Image
import pyautogui, threading, clipboard, os, pytubefix
from pytubefix import Playlist, YouTube
from moviepy.editor import VideoFileClip, AudioFileClip

DOWNLOAD_DIR = "C:\\yt_downloads"

downloading = []

if not os.path.exists(DOWNLOAD_DIR):
    os.mkdir(DOWNLOAD_DIR)

def s_to_hms(s: int):
    h, m, s = s//3600, s%3600//60, s%3600%60
    return f"{str(h) + ':' if h > 0 else ''}{str(m) + ':' if m > 0 else ''}{str(s) if s > 0 else ''}"

def video_add_audio(video_path, audio_path, output_file_path):
    video = VideoFileClip(video_path)
    new_audio = AudioFileClip(audio_path)

    video = video.set_audio(new_audio)
    video.write_videofile(output_file_path, codec='libx264', audio_codec='aac')

def convert_to_filename(name):
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        name = name.replace(char, '')
    return name

def download_video():
    global downloading
    try:
        # init
        url = clipboard.paste()
        yt = YouTube(url)

        if yt.title in downloading:
            pyautogui.alert(text=f"{yt.title}은 이미 다운로드 중 입니다.", title='유튜브 영상 다운로더', button='OK')
            return
        
        # 같은이름 파일 중복해서 다운하면 파일깨짐 (중복방지)
        downloading.append(yt.title)
        
        # 비디오 다운하는거
        resolution_list = []
        for idx, i in enumerate(yt.streams):
            resolution_list.append(
                int(str(i.resolution).replace("p", "")) if i.resolution else 0
            )
        idx = resolution_list.index(max(resolution_list))
        pyautogui.alert(text=f'{yt.title} ({s_to_hms(int(yt.length))})\n영상 다운로드를 시작합니다.\n다운로드가 완료되면 자동으로 알림이 표시됩니다.', title='유튜브 영상 다운로더', button='OK')
        yt.streams[idx].download(output_path=DOWNLOAD_DIR) # 임마는 mp4

        # 오디오 다운하는거
        ys = yt.streams.get_audio_only()
        ys.download(output_path=DOWNLOAD_DIR)  # 무조건 .ma4

        # 합치기
        video_add_audio(
            video_path=os.path.join(DOWNLOAD_DIR, f"{convert_to_filename(yt.title)}.mp4"),
            audio_path=os.path.join(DOWNLOAD_DIR, f"{convert_to_filename(yt.title)}.m4a"),
            output_file_path=os.path.join(DOWNLOAD_DIR, f"{convert_to_filename(yt.title)}.mp4")
        )

        # 비디오는 덮어써졌으니까 오디오만 삭제 + 다운로딩 리스트에서 삭제
        try:
            os.remove(os.path.join(DOWNLOAD_DIR, f"{convert_to_filename(yt.title)}.m4a"))
            downloading.remove(yt.title)
        except:
            pass

        # nofi
        pyautogui.alert(text=f"{yt.title} 영상 다운로드가 완료되었습니다.", title='유튜브 영상 다운로더', button='OK')
    except:
        pyautogui.alert(text=f'영상 다운로드에 오류가 생겼습니다. 다시 시도해 주세요.', title='유튜브 영상 다운로더', button='OK')

def on_clicked():
    work = threading.Thread(target=download_video)
    work.start()

def open_folder():
    os.startfile(os.path.realpath(DOWNLOAD_DIR))

def exit_program():
    icon.stop()
    exit()

image = Image.open("./assets/icon.ico")

menu = (
    MenuItem('복사한 영상 다운로드', on_clicked),
    MenuItem('영상 다운로드 폴더 열기', open_folder),
    MenuItem('프로그램 종료', exit_program),
)

icon = Icon("복사한 영상 다운로드", image, "유튜브 다운로더", menu)
icon.run()