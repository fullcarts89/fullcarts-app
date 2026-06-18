import base64
import io

from PIL import Image

from vfx.llm import _encode_image


def test_encode_image_downscales_tall(tmp_path):
    p = tmp_path / "tall.jpg"
    Image.new("RGB", (850, 9690), "white").save(p)
    data = _encode_image(p, max_edge=2000)
    im = Image.open(io.BytesIO(base64.b64decode(data)))
    assert max(im.size) <= 2000           # long edge capped (was 9690)
    assert abs(im.size[0] / im.size[1] - 850 / 9690) < 0.01  # aspect preserved


def test_encode_image_keeps_small(tmp_path):
    p = tmp_path / "small.jpg"
    Image.new("RGB", (1200, 675), "white").save(p)
    data = _encode_image(p, max_edge=2000)
    im = Image.open(io.BytesIO(base64.b64decode(data)))
    assert im.size == (1200, 675)
