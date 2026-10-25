#!/usr/bin/env python3
"""
Envelhece as imagens de assets/raw/ e grava em assets/img/ com cara de foto de celular velho.

Uso:
    python tools/degrade.py                    processa todas as imagens de assets/raw/
    python tools/degrade.py sol-01.jpg luz-01.png   processa só essas

Opções:
    --src DIR      pasta de origem (padrão: assets/raw)
    --dst DIR      pasta de destino (padrão: assets/img)
    --mapa ARQ     JSON com o horário EXIF de cada imagem (padrão: tools/exif_map.json)

A saída é sempre .jpg com o mesmo nome base. O resultado é determinístico:
a mesma imagem com o mesmo nome sai sempre igual.
"""
import argparse
import io
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp"}

# Celular genérico, sem marca real.
FABRICANTE = "Generic"
MODELO = "A1 Dual Chip"
SOFTWARE = "A1_V2.3.6_20120415"
HORARIO_PADRAO = "2025:05:19 12:00:00"

TAG_FABRICANTE = 0x010F
TAG_MODELO = 0x0110
TAG_SOFTWARE = 0x0131
TAG_DATAHORA = 0x0132
IFD_EXIF = 0x8769
TAG_ORIGINAL = 0x9003
TAG_DIGITALIZADA = 0x9004


def reduzir(img, lado=1600):
    img.thumbnail((lado, lado), Image.LANCZOS)
    return img


def perder_nitidez(img, rng):
    """Lente barata: reduz, amplia de volta e desfoca de leve."""
    w, h = img.size
    fator = rng.uniform(0.62, 0.75)
    pequena = img.resize((max(1, int(w * fator)), max(1, int(h * fator))), Image.BILINEAR)
    img = pequena.resize((w, h), Image.BILINEAR)
    return img.filter(ImageFilter.GaussianBlur(rng.uniform(0.5, 0.9)))


def ruido(img, rng):
    """Ruído de crominância mais forte nas sombras, mais uma granulação fina por cima."""
    w, h = img.size
    sigma = rng.uniform(16, 24)
    canais = [Image.effect_noise((w, h), sigma) for _ in range(3)]
    ruidosa = ImageChops.add(img, Image.merge("RGB", canais), 1.0, -128)
    sombras = ImageOps.invert(img.convert("L")).point(lambda v: int(v * 0.6))
    img = Image.composite(ruidosa, img, sombras)

    grao = Image.effect_noise((w, h), rng.uniform(7, 11))
    granulada = ImageChops.add(img, Image.merge("RGB", (grao, grao, grao)), 1.0, -128)
    return Image.blend(img, granulada, 0.45)


def vinheta(img, rng):
    w, h = img.size
    forca = rng.uniform(0.45, 0.65)
    mascara = Image.radial_gradient("L").resize((w, h), Image.BILINEAR)
    mascara = mascara.point(lambda v: int(max(0, v - 95) * forca))
    return Image.composite(Image.new("RGB", (w, h), (8, 8, 10)), img, mascara)


def cor_de_celular(img, rng):
    img = ImageEnhance.Color(img).enhance(rng.uniform(0.78, 0.9))
    img = ImageEnhance.Contrast(img).enhance(rng.uniform(0.88, 0.95))
    return ImageEnhance.Brightness(img).enhance(rng.uniform(0.97, 1.05))


def recomprimir(img, rng, passes=3):
    for _ in range(passes):
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=rng.randint(60, 75), subsampling=2)
        buf.seek(0)
        img = Image.open(buf)
        img.load()
    return img.convert("RGB")


def exif_para(horario):
    exif = Image.Exif()
    exif[TAG_FABRICANTE] = FABRICANTE
    exif[TAG_MODELO] = MODELO
    exif[TAG_SOFTWARE] = SOFTWARE
    exif[TAG_DATAHORA] = horario
    sub = exif.get_ifd(IFD_EXIF)
    sub[TAG_ORIGINAL] = horario
    sub[TAG_DIGITALIZADA] = horario
    return exif


def processar(origem, destino, horario):
    rng = random.Random(origem.stem)
    with Image.open(origem) as bruta:
        img = ImageOps.exif_transpose(bruta).convert("RGB")
    img = reduzir(img)
    img = perder_nitidez(img, rng)
    img = cor_de_celular(img, rng)
    img = ruido(img, rng)
    img = vinheta(img, rng)
    img = recomprimir(img, rng)
    destino.parent.mkdir(parents=True, exist_ok=True)
    # O quarto passe de compressão é o arquivo final, já com o EXIF.
    img.save(destino, "JPEG", quality=rng.randint(60, 75), subsampling=2,
             exif=exif_para(horario).tobytes())


def main():
    ap = argparse.ArgumentParser(description="Degrada imagens para parecerem foto de celular antigo.")
    ap.add_argument("arquivos", nargs="*", help="nomes de arquivo dentro de --src (padrão: todos)")
    ap.add_argument("--src", default=str(ROOT / "assets" / "raw"))
    ap.add_argument("--dst", default=str(ROOT / "assets" / "img"))
    ap.add_argument("--mapa", default=str(ROOT / "tools" / "exif_map.json"))
    args = ap.parse_args()

    src, dst = Path(args.src), Path(args.dst)
    mapa = {}
    if Path(args.mapa).exists():
        mapa = json.loads(Path(args.mapa).read_text(encoding="utf-8"))

    if args.arquivos:
        origens = [src / a for a in args.arquivos]
    else:
        origens = sorted(p for p in src.iterdir() if p.suffix.lower() in EXTENSOES)
    if not origens:
        print(f"nenhuma imagem em {src}")
        return 1

    for origem in origens:
        if not origem.exists():
            print(f"não encontrada: {origem}")
            continue
        nome = origem.stem + ".jpg"
        horario = mapa.get(nome)
        if horario is None:
            horario = HORARIO_PADRAO
            print(f"aviso: {nome} sem horário em {Path(args.mapa).name}, usando {horario}")
        processar(origem, dst / nome, horario)
        print(f"{origem.name} -> {dst.name}/{nome}  [{horario}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
