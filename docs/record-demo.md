# Offline demo recording

`extraction-eval-demo.gif` renders output captured from these actual commands:

```text
python examples/eval/demo.py
python -m unittest discover -s tests
```

The walkthrough invokes `extraction_eval.py` twice and checks both exit codes:
zero for the matching fixture, one for the deliberately wrong fixture. Its compact
display is derived from the actual JSON reports. Fixtures are hand-written and
synthetic; no model, PDF, API, or user document is involved. The animation covers
the offline evaluator, not the legacy Streamlit/Ollama UI.

To rebuild, install Pillow in your development environment and run
`python scripts/record_demo.py`. The recorder fails if either command fails,
captures full output and source hashes in `demo-recording.json`, and renders the
GIF from that output. Playback pauses are adjusted for reading, not a timing
benchmark. Pillow is only needed to rebuild the animation; the evaluator and
walkthrough use the Python standard library.
