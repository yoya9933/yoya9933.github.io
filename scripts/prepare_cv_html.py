from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
source = (root / "assets" / "Yoya_CV_source.html").read_text(encoding="utf-8")
qr_uri = Path("/tmp/portfolio-qr.png").as_uri()
source, count = re.subn(r'src="data:image/png;base64,[^"]+"', f'src="{qr_uri}"', source)
if count != 2:
    raise SystemExit(f"Expected to replace 2 embedded QR images, replaced {count}")
Path("/tmp/Yoya_CV_print.html").write_text(source, encoding="utf-8")
