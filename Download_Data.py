import os
import re
import shutil
import gdown
from pathlib import Path

def extract_drive_id(share_url: str) -> str:
    pattern = r'(?:/folders/|id=)([a-zA-Z0-9_-]+)'
    match = re.search(pattern, share_url)
    if not match:
        raise ValueError("공유 링크에서 ID를 추출할 수 없습니다.")
    return match.group(1)

def download_folder_from_google_drive(share_url: str, output_dir: Path):
    folder_id = extract_drive_id(share_url)
    os.makedirs(output_dir, exist_ok=True)

    gdown.download_folder(id=folder_id, output=str(output_dir), quiet=False, use_cookies=False)

    downloaded_dirs = list(output_dir.glob("*"))
    for item in downloaded_dirs:
        if item.is_dir():
            for file in item.glob("**/*"):
                if file.is_file():
                    dest = output_dir / file.relative_to(item)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file), str(dest))
            shutil.rmtree(item) 

    print("\n데이터 다운로드가 완료되었습니다.")
    print(f"저장 경로: {output_dir.resolve()}")

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    output_dir = script_dir.parent / "Download_Data"

    # 다운로드할 구글 드라이브 공유 링크
    share_url = "https://drive.google.com/drive/folders/1ryxXR_OhH1orSBd33uVKIaQ87L4mVp_s?usp=sharing" 

    download_folder_from_google_drive(share_url, output_dir)
