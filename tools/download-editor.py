"""Download the official Unity editor in verified HTTP byte ranges; no installer is run."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://download.unity3d.com/download_unity/cc83ebd631f8/Windows64EditorInstaller/UnitySetup64-6000.4.5f1.exe'
TOTAL = 3772758632
PARTS = 16
WORK = ROOT / '.local/tools/unity-parts'
OUTPUT = ROOT / '.local/tools/UnitySetup64-6000.4.5f1.exe'
WORK.mkdir(parents=True, exist_ok=True)

def get_part(index):
    start = TOTAL * index // PARTS
    end = TOTAL * (index + 1) // PARTS - 1
    path = WORK / f'{index:02d}.part'
    if path.exists() and path.stat().st_size == end - start + 1:
        return index
    result = subprocess.run(['curl.exe', '-sS', '-4', '--http1.1', '-L', '--fail', '--retry', '2', '--retry-all-errors', '--connect-timeout', '20', '--max-time', '1200', '-r', f'{start}-{end}', '-o', str(path), URL], capture_output=True, text=True)
    if result.returncode or not path.exists() or path.stat().st_size != end - start + 1:
        raise RuntimeError(f'part {index} failed: {result.stderr[-500:]}')
    return index

started = time.time()
with ThreadPoolExecutor(max_workers=4) as pool:
    for future in as_completed([pool.submit(get_part, index) for index in range(PARTS)]):
        print(f'part {future.result()+1}/{PARTS} complete after {time.time()-started:.0f}s', flush=True)
with OUTPUT.open('wb') as target:
    for index in range(PARTS):
        with (WORK / f'{index:02d}.part').open('rb') as source:
            while data := source.read(8*1024*1024):
                target.write(data)
assert OUTPUT.stat().st_size == TOTAL
print(f'Official installer complete: {OUTPUT} ({TOTAL} bytes)', flush=True)
