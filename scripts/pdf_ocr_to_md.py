#!/opt/homebrew/bin/python3.12
"""
pdf_ocr_to_md.py — 通用 OCR 工具 (W30 spike)
支持：
  - PDF 文件（pdftoppm 转 PNG 后 PaddleOCR）
  - PPTX 文件（用 python-pptx 提取页 + 用 LibreOffice 转 PNG 后 OCR）
  - 直接图片（PNG/JPG/JPEG）

输出：
  - Markdown 格式
  - 每页 / 每张图独立 section
  - 自动识别的中英文混排

依赖：
  - paddleocr==3.7.0
  - paddlepaddle==3.3.1
  - python-pptx（PPTX 支持）
  - poppler-utils（pdftoppm 命令行）
  - libreoffice（PPTX 转 PNG，可选）

环境变量：
  PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
  （避免 model host 404）

用法：
  python3 pdf_ocr_to_md.py /path/to/file.pdf
  python3 pdf_ocr_to_md.py /path/to/file.pptx
  python3 pdf_ocr_to_md.py /path/to/image.png
  python3 pdf_ocr_to_md.py /path/to/dir/  # 批量

W30 spike 实战:
  - 仅在 /tmp/spike_venv 内可用 (Python 3.12 + paddleocr + paddlepaddle)
  - 装了之后用 ENV PYTHONPATH=/tmp/spike_venv/lib/python3.12/site-packages 调用
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
from pathlib import Path

# === 环境配置：PaddleOCR 模型源绕过 ===
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

# === spike venv 注入路径 ===
_SPIKE_VENV_SITE = '/tmp/spike_venv/lib/python3.12/site-packages'
if os.path.exists(_SPIKE_VENV_SITE) and _SPIKE_VENV_SITE not in sys.path:
    sys.path.insert(0, _SPIKE_VENV_SITE)


# === OCR 后端：PaddleOCR 3.x 的 predict API ===
class PaddleOCRBackend:
    _instance = None

    @classmethod
    def get_instance(cls, lang='ch'):
        if cls._instance is None:
            from paddleocr import PaddleOCR
            cls._instance = PaddleOCR(
                lang=lang,
                use_textline_orientation=False,
            )
        return cls._instance

    @classmethod
    def predict(cls, image_path):
        """返回 [[text1, text2, ...]] 列表"""
        ocr = cls.get_instance()
        result = ocr.predict(image_path)
        # 新版 API: result 是 [{'rec_text': [...], 'rec_score': [...], ...}] 列表
        all_texts = []
        for page in result:
            if isinstance(page, dict):
                texts = page.get('rec_text', [])
            elif isinstance(page, list):
                texts = [t[1][0] for t in page if isinstance(t, (list, tuple)) and len(t) > 1]
            else:
                texts = []
            all_texts.extend(texts)
        return all_texts


# === 文件类型检测 + 转 PNG ===
def file_to_pngs(path: Path, work_dir: Path):
    """
    返回 PNG 文件列表 (绝对路径)
    """
    pngs = []
    suffix = path.suffix.lower()

    if suffix == '.pdf':
        # 用 pdftoppm 转 PNG
        cmd = ['pdftoppm', '-r', '200', '-png', str(path), str(work_dir / f'{path.stem}_page')]
        subprocess.run(cmd, check=True, capture_output=True)
        pngs = sorted(work_dir.glob(f'{path.stem}_page-*.png'))

    elif suffix in ('.pptx', '.ppt'):
        # PPTX → PDF (libreoffice) → PNG
        pdf_path = work_dir / f'{path.stem}.pdf'
        subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', str(work_dir), str(path)],
            check=True, capture_output=True
        )
        # 然后 pdftoppm
        subprocess.run(
            ['pdftoppm', '-r', '200', '-png', str(pdf_path), str(work_dir / f'{path.stem}_slide')],
            check=True, capture_output=True
        )
        pngs = sorted(work_dir.glob(f'{path.stem}_slide-*.png'))

    elif suffix in ('.png', '.jpg', '.jpeg'):
        pngs = [path]

    else:
        raise ValueError(f'不支持的文件类型: {suffix}')

    return pngs


# === 单个 PNG OCR → Markdown ===
def ocr_pngs_to_md(pngs, source_name):
    """所有 PNG 跑 OCR，按顺序拼 markdown"""
    md = []
    md.append(f'# OCR 识别结果 · {source_name}\n')
    md.append(f'> 文件源: `{source_name}`')
    md.append(f'> 页数: {len(pngs)}\n')

    backend = PaddleOCRBackend()

    for i, png in enumerate(pngs):
        md.append(f'\n## 第 {i+1} 页 ({png.name})\n')
        try:
            texts = backend.predict(str(png))
            for t in texts:
                t_clean = t.strip()
                if t_clean:
                    md.append(f'- {t_clean}')
        except Exception as e:
            md.append(f'> ⚠️ 错误: {e}')

    return '\n'.join(md)


# === 主流程 ===
def process_path(input_path, output_dir='./ocr_output'):
    """处理单个文件或目录"""
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_dir():
        # 批量处理目录内文件
        targets = []
        for ext in ('*.pdf', '*.pptx', '*.ppt', '*.png', '*.jpg', '*.jpeg'):
            targets.extend(input_path.glob(ext))
        for tgt in targets:
            process_path(tgt, output_dir)
        return

    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        return

    print(f"\n[OCR] 处理: {input_path}")
    print(f"      输出至: {output_dir}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        pngs = file_to_pngs(input_path, tmp)

        if not pngs:
            print(f"❌ 无法生成 PNG (可能缺 pdftoppm / libreoffice): {input_path}")
            return

        md_text = ocr_pngs_to_md(pngs, input_path.name)

        out_file = output_dir / f"{input_path.stem}_ocr.md"
        out_file.write_text(md_text, encoding='utf-8')
        print(f"      ✅ 输出: {out_file}")
        print(f"      页数: {len(pngs)}, 文本块: {md_text.count(chr(10) + '-')}")


def main():
    ap = argparse.ArgumentParser(description='PDF/PPTX/图片 OCR → Markdown')
    ap.add_argument('paths', nargs='+', help='文件或目录路径')
    ap.add_argument('--output-dir', '-o', default='./ocr_output', help='输出目录 (default: ./ocr_output)')
    args = ap.parse_args()

    for p in args.paths:
        process_path(p, args.output_dir)


if __name__ == "__main__":
    main()
