#!/usr/bin/env python3
"""
Gerador estático do blog.

Uso:
    python build.py                      gera em docs/ só o que já pode ir ao ar hoje
    python build.py --preview            gera tudo em preview/, ignorando datas
    python build.py --date 2026-11-20    simula o site como estaria nessa data (em preview/)

As entradas têm publish_date no frontmatter. Os registros automáticos (logs.csv)
seguem as mesmas datas, deslocadas por LOG_OFFSET_DAYS.
"""
import argparse
import csv
import datetime as dt
import html
import re
import shutil
from pathlib import Path
from zoneinfo import ZoneInfo

import markdown

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"
TZ = ZoneInfo("America/Sao_Paulo")

BLOG_TITLE = "Seis meses lá em cima"
BLOG_DESC = ("Diário de um observador meteorológico numa estação no alto da serra. "
             "Escrevo pra família acompanhar e pra não falar sozinho.")
AUTOR = "Davi"

# Distância entre o calendário do diário (2025) e o calendário real de publicação.
# Um múltiplo de 7 mantém os dias da semana. Com 532, o registro de 19/05/2025 14:00
# entra no site a partir de 02/11/2026 14:00. Para mudar o lançamento use tools/remarcar.py.
LOG_OFFSET_DAYS = 532

POR_PAGINA = 5
MANTER_NA_SAIDA = {"CNAME"}

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


# ---------------------------------------------------------------- leitura

def valor(bruto):
    bruto = bruto.strip()
    if len(bruto) >= 2 and bruto[0] == '"' and bruto[-1] == '"':
        return bruto[1:-1].replace('\\"', '"')
    if " #" in bruto:
        bruto = bruto.split(" #", 1)[0].strip()
    if bruto.startswith("[") and bruto.endswith("]"):
        dentro = bruto[1:-1].strip()
        return [valor(x) for x in dentro.split(",")] if dentro else []
    return bruto


def ler_documento(path):
    """Frontmatter simples (chave: valor, listas [a, b]) seguido de markdown."""
    texto = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    meta, corpo = {}, texto
    m = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", texto, re.S)
    if m:
        for linha in m.group(1).splitlines():
            if not linha.strip() or linha.lstrip().startswith("#"):
                continue
            chave, _, resto = linha.partition(":")
            meta[chave.strip()] = valor(resto)
        corpo = m.group(2)
    return meta, corpo


def como_lista(v):
    if not v:
        return []
    return v if isinstance(v, list) else [v]


def ler_entradas():
    entradas = []
    for path in sorted((CONTENT / "entries").glob("*.md")):
        meta, corpo = ler_documento(path)
        data = dt.date.fromisoformat(meta["entry_date"])
        slug = re.sub(r"^\d+-", "", path.stem)
        exibida = meta.get("shown_date")
        entradas.append({
            "slug": slug,
            "titulo": meta.get("title", ""),
            "publica": dt.date.fromisoformat(meta["publish_date"]),
            "data": data,
            "hora": meta.get("entry_time", "12:00"),
            "data_exibida": dt.date.fromisoformat(exibida) if exibida else data,
            "imagens": como_lista(meta.get("images")),
            "oculto": meta.get("hidden_comment", ""),
            "ato": int(meta.get("act", 1)),
            "autor": meta.get("author", AUTOR),
            "defeitos": como_lista(meta.get("glitches")),
            "corpo": corpo,
            "url": f"{data.year}/{data.month:02d}/{slug}.html",
        })
    entradas.sort(key=lambda e: (e["data"], e["hora"]))
    return entradas


def ler_registros():
    with open(CONTENT / "logs.csv", newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    for l in linhas:
        l["_dt"] = dt.datetime.fromisoformat(f"{l['data']}T{l['hora']}")
    return linhas


def ler_livros():
    livros = []
    for path in CONTENT.joinpath("osmar").glob("livro-*.md"):
        meta, corpo = ler_documento(path)
        livros.append({
            "slug": path.stem,
            "num": int(path.stem.split("-")[1]),
            "titulo": meta.get("title", path.stem),
            "periodo": meta.get("periodo", ""),
            "publica": dt.date.fromisoformat(meta["publish_date"]),
            "libera": meta.get("libera", ""),
            "corpo": corpo,
        })
    livros.sort(key=lambda l: l["num"])
    return livros


# ---------------------------------------------------------------- utilidades

def template(nome):
    return (TEMPLATES / nome).read_text(encoding="utf-8")


def preencher(tpl, **ctx):
    """Troca {{chave}} numa passada só, para o conteúdo inserido não ser reprocessado."""
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(ctx.get(m.group(1), "")), tpl)


def gravar(path, texto):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(texto, encoding="utf-8")


def data_longa(d):
    return f"{DIAS[d.weekday()]}, {d.day} de {MESES[d.month - 1]} de {d.year}"


def esc(t):
    return html.escape(t, quote=True)


def md(texto):
    return markdown.markdown(texto, extensions=["tables", "fenced_code", "md_in_html"])


# ---------------------------------------------------------------- blocos do blog

def foto_html(nome, quebrada):
    src = f"__RAIZ__img/{esc(nome)}"
    alt = esc(nome) if quebrada else ""
    return (f'<div class="foto"><a href="{src}"><img src="{src}" alt="{alt}" '
            f'loading="lazy"></a></div>')


def corpo_html(e):
    quebrada = "imagem-quebrada" in e["defeitos"]
    usadas = set()

    def troca(m):
        nome = m.group(1).strip()
        usadas.add(nome)
        return "\n\n" + foto_html(nome, quebrada) + "\n\n"

    texto = re.sub(r"\[\[foto:([^\]]+)\]\]", troca, e["corpo"])
    topo = "".join(foto_html(n, quebrada) for n in e["imagens"] if n not in usadas)
    return topo + md(texto)


def post_html(e, raiz, completo):
    titulo = esc(e["titulo"])
    link = f"{raiz}{e['url']}"
    h3 = f'<h3 class="post-title"><a href="{link}">{titulo}</a></h3>' if titulo else ""
    oculto = ""
    if completo and e["oculto"]:
        oculto = f"<!-- {e['oculto'].replace('--', '- -')} -->\n"
    corpo = corpo_html(e).replace("__RAIZ__", raiz)
    autor = esc(e["autor"])
    if e["autor"] == AUTOR:
        autor = f'<a href="{raiz}quem-sou-eu.html">{autor}</a>'
    return (
        f'<h2 class="date-header"><span>{data_longa(e["data_exibida"])}</span></h2>\n'
        f'<div class="post">\n{h3}\n<div class="post-body">\n{oculto}{corpo}\n</div>\n'
        f'<div class="post-footer">Postado por {autor} às '
        f'<a class="timestamp" href="{link}">{e["hora"]}</a>'
        f'<span class="comentarios">Comentários fechados pelo autor.</span></div>\n</div>\n'
    )


def sidebar_html(publicadas, ato, raiz, contador):
    partes = []
    partes.append(
        '<div class="widget"><h2>Quem sou eu</h2>'
        '<div class="perfil"><div class="avatar"></div>'
        f'<p><a href="{raiz}quem-sou-eu.html"><b>{AUTOR}</b></a></p>'
        '<p>34 anos. Observador de superfície temporário. Gosto de café passado e de lugar quieto.</p>'
        f'<p><a href="{raiz}quem-sou-eu.html">Visualizar meu perfil completo</a></p></div></div>'
    )

    digitos = "".join(f"<span>{c}</span>" for c in f"{contador:06d}")
    partes.append(
        '<div class="widget"><h2>Visitas</h2>'
        f'<div class="contador">{digitos}</div>'
        '<p id="ultimo-registro" class="ultimo" hidden></p></div>'
    )

    if publicadas:
        meses = {}
        for e in reversed(publicadas):
            meses.setdefault((e["data"].year, e["data"].month), []).append(e)
        itens = []
        for i, ((ano, mes), posts) in enumerate(meses.items()):
            aberto = " open" if i == 0 else ""
            lis = "".join(
                f'<li><a href="{raiz}{p["url"]}">{esc(p["titulo"]) or "(sem título)"}</a></li>'
                for p in posts)
            itens.append(f'<li><details{aberto}><summary>{MESES[mes - 1]} '
                         f'<span>({len(posts)})</span></summary><ul class="posts">{lis}</ul></details></li>')
        ano = publicadas[-1]["data"].year
        partes.append(
            '<div class="widget"><h2>Arquivo do blog</h2><ul class="arquivo">'
            f'<li><details open><summary>{ano} <span>({len(publicadas)})</span></summary>'
            f'<ul>{"".join(itens)}</ul></details></li></ul></div>'
        )

    # A partir do terceiro ato um link da lateral passa a apontar para um endereço que não existe.
    manual = "manual-do-observador.html" if ato >= 3 else "manual-observador.html"
    partes.append(
        '<div class="widget"><h2>Links</h2><ul class="links">'
        f'<li><a href="{raiz}registros.html">Registros da estação (automático)</a></li>'
        f'<li><a href="{raiz}{manual}">Manual do observador (trechos)</a></li>'
        '</ul></div>'
    )
    return "\n".join(partes)


class Site:
    def __init__(self, saida, agora, preview):
        self.saida = saida
        self.agora = agora
        self.preview = preview
        self.hoje = agora.date()
        todas = ler_entradas()
        self.entradas = [e for e in todas if preview or e["publica"] <= self.hoje]
        self.ato = max((e["ato"] for e in self.entradas), default=0)
        inicio = min(e["publica"] for e in todas)
        dias = max(0, (self.hoje - inicio).days)
        self.contador = 1187 + dias * 23 + len(self.entradas) * 11
        self.base = template("base.html")

    def pagina(self, rel, titulo, conteudo):
        raiz = "../" * rel.count("/")
        texto = preencher(
            self.base,
            page_title=esc(f"{titulo} | {BLOG_TITLE}" if titulo else BLOG_TITLE),
            raiz=raiz,
            blog_title=esc(BLOG_TITLE),
            blog_desc=esc(BLOG_DESC),
            content=conteudo.replace("__RAIZ__", raiz),
            sidebar=sidebar_html(self.entradas, self.ato, raiz, self.contador),
            ano=self.entradas[-1]["data"].year if self.entradas else 2025,
        )
        gravar(self.saida / rel, texto)

    # ------------------------------------------------------------ páginas

    def indice(self):
        recentes = list(reversed(self.entradas))
        if not recentes:
            self.pagina("index.html", "", '<p class="vazio">Nenhuma postagem.</p>')
            return
        paginas = [recentes[i:i + POR_PAGINA] for i in range(0, len(recentes), POR_PAGINA)]
        for n, grupo in enumerate(paginas, start=1):
            rel = "index.html" if n == 1 else f"pagina-{n}.html"
            posts = "\n".join(post_html(e, "__RAIZ__", completo=False) for e in grupo)
            nav = []
            if n > 1:
                ant = "index.html" if n == 2 else f"pagina-{n - 1}.html"
                nav.append(f'<a class="newer" href="__RAIZ__{ant}">Postagens mais recentes</a>')
            nav.append('<a class="home" href="__RAIZ__index.html">Página inicial</a>')
            if n < len(paginas):
                nav.append(f'<a class="older" href="__RAIZ__pagina-{n + 1}.html">Postagens mais antigas</a>')
            self.pagina(rel, "", posts + f'<div id="blog-pager">{"".join(nav)}</div>')

    def entradas_individuais(self):
        for i, e in enumerate(self.entradas):
            nav = []
            if i + 1 < len(self.entradas):
                nav.append(f'<a class="newer" href="__RAIZ__{self.entradas[i + 1]["url"]}">Postagem mais recente</a>')
            nav.append('<a class="home" href="__RAIZ__index.html">Página inicial</a>')
            if i > 0:
                nav.append(f'<a class="older" href="__RAIZ__{self.entradas[i - 1]["url"]}">Postagem mais antiga</a>')
            conteudo = (post_html(e, "__RAIZ__", completo=True)
                        + f'<div id="blog-pager">{"".join(nav)}</div>'
                        + '<div class="comments"><h4>Nenhum comentário:</h4>'
                          '<p>Comentários fechados pelo autor.</p></div>')
            self.pagina(e["url"], e["titulo"], conteudo)

    def estaticas(self):
        for path in sorted((CONTENT / "paginas").glob("*.md")):
            meta, corpo = ler_documento(path)
            titulo = meta.get("title", "")
            conteudo = (f'<div class="post"><h3 class="post-title">{esc(titulo)}</h3>'
                        f'<div class="post-body">{md(corpo)}</div></div>')
            self.pagina(f"{path.stem}.html", titulo, conteudo)

    def registros(self):
        offset = dt.timedelta(days=LOG_OFFSET_DAYS)
        linhas = [l for l in ler_registros()
                  if self.preview or l["_dt"] + offset <= self.agora]

        def tabela(ls):
            corpo = []
            for l in ls:
                temp = l["temperatura"].replace(".", ",")
                obs = esc(l["observacoes"])
                d = l["_dt"]
                corpo.append(
                    f'<tr><td>{d:%d/%m/%Y}</td><td>{l["hora"]}</td><td>{temp}</td>'
                    f'<td>{l["umidade"]}</td><td>{l["vento"]}</td>'
                    f'<td class="vis">{l["visibilidade"]}</td><td class="obs">{obs}</td></tr>')
            return ('<table class="registros"><thead><tr><th>Data</th><th>Hora</th>'
                    '<th>Temp. (°C)</th><th>UR (%)</th><th>Vento (dir/kt)</th>'
                    '<th>Visib. (m)</th><th>Observações</th></tr></thead><tbody>'
                    + "".join(corpo) + "</tbody></table>")

        intro = ('<p>Espelho dos registros horários da estação Pico Velado (PV). '
                 'Os dados saem do terminal e sobem pra cá sozinhos. Hora local. '
                 'Visibilidade em metros, 9999 quer dizer 10 km ou mais.</p>')
        if not linhas:
            conteudo = intro + '<p class="vazio">Nenhum registro disponível.</p>'
        else:
            dias = {}
            for l in linhas:
                dias.setdefault(l["data"], []).append(l)
            for dia, ls in dias.items():
                d = dt.date.fromisoformat(dia)
                c = (f'<div class="post"><h3 class="post-title">Registros de {d:%d/%m/%Y}</h3>'
                     f'<div class="post-body">{tabela(ls)}'
                     f'<p><a href="__RAIZ__registros.html">voltar</a></p></div></div>')
                self.pagina(f"registros/{dia}.html", f"Registros {d:%d/%m/%Y}", c)
            ultimas = list(reversed(linhas[-48:]))
            lista = "".join(
                f'<li><a href="__RAIZ__registros/{dia}.html">{dt.date.fromisoformat(dia):%d/%m/%Y}</a></li>'
                for dia in reversed(list(dias)))
            conteudo = (intro + "<h4>Últimas 48 horas</h4>" + tabela(ultimas)
                        + f'<h4>Dias anteriores</h4><ul class="dias">{lista}</ul>')
        self.pagina("registros.html", "Registros automáticos",
                    f'<div class="post"><h3 class="post-title">Registros automáticos</h3>'
                    f'<div class="post-body">{conteudo}</div></div>')

    def livros(self):
        """Pasta /livros/: sem link de lugar nenhum, só citada no robots.txt."""
        livros = [l for l in ler_livros() if self.preview or l["publica"] <= self.hoje]
        if not livros:
            return
        tpl = template("livro.html")
        for l in livros:
            corpo = md(l["corpo"])
            corpo = re.sub(r"\[ilegível\]", '<span class="borrao">ilegível</span>', corpo)
            corpo = re.sub(r"~~(.+?)~~", r"<s>\1</s>", corpo)
            gravar(self.saida / "livros" / f"{l['slug']}.html",
                   preencher(tpl, titulo=esc(l["titulo"]), periodo=esc(l["periodo"]), corpo=corpo))
            if l["libera"] == "ultimo-registro":
                shutil.copy(TEMPLATES / "ultimo-registro.html", self.saida / "ultimo-registro.html")
        linhas = ['<a href="../">../</a>']
        for l in livros:
            nome = f"{l['slug']}.html"
            tamanho = len((self.saida / "livros" / nome).read_bytes()) // 1024 + 1
            linhas.append(f'<a href="{nome}">{nome}</a>{" " * (24 - len(nome))}02-Jul-2025 03:00  {tamanho:>4}K')
        gravar(self.saida / "livros" / "index.html",
               preencher(template("listagem.html"), linhas="\n".join(linhas)))

    def imagens(self):
        destino = self.saida / "img"
        destino.mkdir(parents=True, exist_ok=True)
        faltando = []
        for e in self.entradas:
            for nome in e["imagens"]:
                origem = ASSETS / "img" / nome
                if origem.exists():
                    shutil.copy2(origem, destino / nome)
                elif "imagem-quebrada" not in e["defeitos"]:
                    faltando.append(nome)
        return faltando

    def fixos(self):
        shutil.copy(ASSETS / "estilo.css", self.saida / "estilo.css")
        shutil.copy(ASSETS / "site.js", self.saida / "site.js")
        shutil.copy(TEMPLATES / "404.html", self.saida / "404.html")
        gravar(self.saida / "robots.txt", "User-agent: *\nDisallow: /livros/\n")
        gravar(self.saida / ".nojekyll", "")

    def gerar(self):
        self.fixos()
        self.indice()
        self.entradas_individuais()
        self.estaticas()
        self.registros()
        self.livros()
        return self.imagens()


def limpar(saida):
    saida.mkdir(exist_ok=True)
    for item in saida.iterdir():
        if item.name in MANTER_NA_SAIDA:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def main():
    ap = argparse.ArgumentParser(description="Gera o blog estático.")
    ap.add_argument("--preview", action="store_true", help="gera tudo em preview/, ignorando datas")
    ap.add_argument("--date", help="simula a data (AAAA-MM-DD ou AAAA-MM-DDTHH:MM), gera em preview/")
    args = ap.parse_args()

    if args.date:
        agora = dt.datetime.fromisoformat(args.date if "T" in args.date else args.date + "T04:00")
    else:
        agora = dt.datetime.now(TZ).replace(tzinfo=None, second=0, microsecond=0)
    preview = args.preview
    saida = ROOT / ("preview" if (preview or args.date) else "docs")

    limpar(saida)
    site = Site(saida, agora, preview)
    faltando = site.gerar()

    modo = "preview (tudo)" if preview else f"data {agora:%Y-%m-%d %H:%M}"
    print(f"{modo}: {len(site.entradas)} entradas, ato {site.ato}, saída em {saida.relative_to(ROOT)}/")
    if faltando:
        print(f"aviso: {len(faltando)} imagem(ns) ainda não existem em assets/img/: {', '.join(faltando)}")


if __name__ == "__main__":
    main()
