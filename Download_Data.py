"""
Google Drive 공개 폴더 → 로컬 디렉터리 복사 (rclone 기반)
--------------------------------------------------------
사전 준비(최초 1회만)

1) rclone 설치
   Windows:  https://rclone.org/download/ → rclone.exe를 PATH에 추가
   macOS  :  brew install rclone
   Linux  :  curl https://rclone.org/install.sh | sudo bash

2) rclone remote 설정
   > rclone config
   n) New remote  → 이름: gdrive
   Storage: drive
   Scope : 1 (Full access) 또는 2 (Read‑only) 추천
   “Use browser to authenticate?” Y → 구글 로그인 후 허용
   모든 기본값 Enter → 완료

이후부터는 아래 스크립트만 실행하면 끝!
"""
"""
Google Drive 공개 폴더 → 로컬 디렉터리 복사 (rclone 기반 · 절대 경로 지정 버전)
-------------------------------------------------------------------------------
※ 사전 준비
   1) rclone.exe 다운로드 후 원하는 위치(예: C:\Tools\rclone) 에 두기
   2) 파이썬 코드의 RCLONE 변수 값을 rclone.exe 실제 경로로 수정
"""

"""
Google Drive 공개 폴더 → 로컬 디렉터리 복사 (rclone · 절대 경로)
----------------------------------------------------------------
rclone.exe 위치만 RCLONE 변수에 맞춰 주세요.
"""

import subprocess, sys
from pathlib import Path
from datetime import datetime

RCLONE    = r"C:\Users\dsng3\Desktop\rclone-v1.69.2-windows-amd64\rclone-v1.69.2-windows-amd64\rclone.exe"
FOLDER_ID = "1_rFCgCyrrSu5i0VqIUdMpMi_XgmCtoPc"    # ← 다운받을 폴더
DEST_DIR  = Path("Data")
REMOTE    = "gdrive"
TRANSFERS = "8"

def drive_copy():
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    log = DEST_DIR / f"rclone_debug_{ts}.log"

    cmd = [
        RCLONE, "-vv",
        "copy", f"{REMOTE}:", str(DEST_DIR),         # ★ 경로는 비우고
        "--drive-root-folder-id", FOLDER_ID,         # ★ 이 폴더를 루트로 고정
        "--progress",
        "--transfers", TRANSFERS,
        "--checkers",  "8",
        "--log-file", str(log),
    ]
    print("▶", " ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("✅  다운로드 완료")
    else:
        sys.exit(f"❌  rclone 종료 코드 {res.returncode} — {log} 를 확인하세요")

if __name__ == "__main__":
    print(f"📥  Google Drive({FOLDER_ID}) → {DEST_DIR.resolve()} …")
    drive_copy()
