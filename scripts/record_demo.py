"""Render a terminal GIF from captured example/test output; requires Pillow."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]


def font(size):
    for name in ['DejaVuSansMono.ttf', 'C:/Windows/Fonts/consola.ttf']:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def main():
    commands = [['examples/eval/demo.py'], ['-m', 'unittest', 'discover', '-s', 'tests']]
    recordings = []
    frames = []
    durations = []
    for arguments in commands:
        result = subprocess.run([sys.executable, *arguments], cwd=ROOT,
                                capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise RuntimeError('Demo command failed; no success GIF will be written: ' + result.stderr)
        command = 'python ' + ' '.join(arguments)
        output = result.stdout + result.stderr
        recordings.append({'command': command, 'exit_code': result.returncode, 'output': output})
        lines = [part for line in output.splitlines() for part in (textwrap.wrap(line, 91) or [''])]
        for count in range(len(lines) + 1):
            canvas = Image.new('RGB', (1040, 520), '#0c1220')
            draw = ImageDraw.Draw(canvas)
            draw.rounded_rectangle((20, 20, 1020, 500), radius=16, fill='#111d30', outline='#2b3f59', width=2)
            for x, color in [(48, '#f7768e'), (72, '#e0af68'), (96, '#9ece6a')]:
                draw.ellipse((x, 43, x + 12, 55), fill=color)
            draw.text((128, 36), 'Extraction checks', font=font(20), fill='#e7eef8')
            draw.text((729, 39), 'Actual command output', font=font(15), fill='#91a4c0')
            draw.line((40, 76, 1000, 76), fill='#2b3f59', width=1)
            draw.text((44, 96), '$ ' + command, font=font(17), fill='#7dd3fc')
            visible = lines[:count][-14:]
            for index, line in enumerate(visible):
                color = '#a7f3d0' if line == 'OK' else '#e1e9f5'
                draw.text((44, 136 + index * 23), line, font=font(17), fill=color)
            draw.text((44, 470), 'Synthetic hand-written fixtures  |  No model or API called', font=font(14), fill='#91a4c0')
            frames.append(canvas)
            durations.append(2400 if count == len(lines) else 180)
    target = ROOT / 'docs'
    target.mkdir(exist_ok=True)
    frames[0].save(target / 'extraction-eval-demo.gif', save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    sources = ['extraction_eval.py', 'examples/eval/demo.py', 'examples/eval/cases.jsonl', 'examples/eval/predictions-pass.jsonl', 'examples/eval/predictions-fail.jsonl']
    metadata = {'recorded_utc': datetime.now(timezone.utc).isoformat(),
                'kind': 'animation_rendered_from_actual_command_output',
                'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
                'commands': recordings}
    (target / 'demo-recording.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print('Recorded example and tests; wrote docs/extraction-eval-demo.gif and docs/demo-recording.json')


if __name__ == '__main__':
    main()
