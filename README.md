# A Estação

Site de ficção em formato de blog pessoal (ARG / analog horror). O diário de Davi, observador temporário da estação meteorológica Pico Velado, publicado aos poucos, um dia de cada vez.

Tudo aqui é inventado. A página `aviso.html`, linkada no rodapé, diz isso ao leitor.

## Requisitos

- Python 3.9 ou mais novo
- `pip install markdown pillow` (o Pillow só é usado por `tools/degrade.py`; o build precisa apenas do `markdown`)

## Rodar o build

```
python build.py --preview              # gera tudo em preview/, ignorando datas
python build.py --date 2026-11-26      # como o site estaria nesse dia (04:00), em preview/
python build.py                        # o build real: só o que já pode ir ao ar hoje, em docs/
```

Abra `preview/index.html` direto no navegador. Os links são relativos, não precisa de servidor.

`preview/` está no `.gitignore`. Nunca copie o conteúdo de `preview/` para `docs/`.

## Datas de publicação

- Cada entrada em `content/entries/` tem `publish_date` no frontmatter. O build só gera entradas com `publish_date` menor ou igual à data de hoje (fuso de São Paulo).
- Os registros de `content/logs.csv` seguem o mesmo calendário: cada linha aparece quando `data + hora + LOG_OFFSET_DAYS` já passou. A constante fica no topo de `build.py`.
- Os livros do Osmar (`content/osmar/`) também têm `publish_date`. O `livro-7.md` tem `libera: ultimo-registro`, que faz o build gerar `/ultimo-registro.html` junto com ele.
- Para mudar a data de lançamento sem desalinhar nada, desloque tudo de uma vez:

```
python tools/remarcar.py 14     # adia duas semanas
python tools/remarcar.py -7     # antecipa uma semana
```

Use múltiplos de 7 para os dias da semana continuarem batendo com o diário (as segundas de abastecimento, o domingo de ligar para casa).

Calendário atual: primeira entrada em 03/11/2026, última (o registro automático) em 16/12/2026.

## Imagens

1. Gere ou fotografe cada imagem seguindo `gemini_prompts.md`. Ali está indicado o que vale fotografar você mesmo e o que precisa de IA.
2. Salve em `assets/raw/` com o nome indicado (a extensão pode ser qualquer uma).
3. Rode `python tools/degrade.py` (ou `python tools/degrade.py sol-01.png` para uma só).
4. A saída vai para `assets/img/`, já reduzida, com ruído, vinheta, três recompressões JPEG e EXIF de celular genérico.
5. O horário EXIF de cada imagem vem de `tools/exif_map.json`. É ali que ficam as inconsistências plantadas.

O build só copia para o site as imagens das entradas já publicadas. `b3-noite.jpg` não deve existir: é a imagem quebrada da entrada 16.

## Publicar no GitHub Pages

1. Em *Settings > Pages*, escolha *Deploy from a branch*, branch `main`, pasta `/docs`.
2. O workflow `.github/workflows/publicar.yml` roda todo dia às 04:00 de Brasília, executa `python build.py` e faz commit de `docs/` se algo mudou. Dá para rodar na mão pela aba *Actions*.

**Atenção a spoilers:** com o repositório público, qualquer pessoa lê `content/` inteiro, inclusive o final. Se isso importa, mantenha este repositório privado e publique `docs/` num segundo repositório público (por exemplo trocando o passo de commit do workflow por um push para outro repositório com uma deploy key), ou use um plano que permita Pages a partir de repositório privado.

## Camadas escondidas (spoiler, só para o autor)

- Comentários HTML em cada entrada (`hidden_comment`). Até a entrada 8 medem a luz a 310 graus; a partir da 9 passam a 130 graus, a direção oposta.
- `robots.txt` bloqueia `/livros/`, que existe e não tem link de lugar nenhum.
- A contracapa do livro 7 aponta para `/ultimo-registro.html`.
- EXIF: `sol-01.jpg` e `araucaria-dia.jpg` às 03:12; `postes-01.jpg` com data de 1994.
- `logs.csv`: um "." às 03:00 de 29/05, as observações de Davi sobre a luz, o 0200 e o 0050 parados no fim, a sequência 3000, 1000, 0500, 0200, 0050, 0000 e o "B1." às 02:00 de 02/07.
- Defeitos progressivos: imagem quebrada na entrada 16, link "Manual do observador" quebrado a partir do ato 3, data fora de ordem na entrada 21.
- `site.js`: a partir da quinta visita aparece "último registro: [visita anterior]" na lateral; entre 03:00 e 04:00 do visitante, uma névoa leve sobre as fotos. Tudo em `localStorage`/`sessionStorage`, nada sai do navegador. Sem cookies, sem analytics.

## Estrutura

```
content/entries/   entradas (.md com frontmatter)
content/logs.csv   registros horários automáticos
content/osmar/     livros do Osmar (viram /livros/)
content/paginas/   quem-sou-eu, aviso, manual do observador
assets/            estilo.css, site.js, raw/ e img/
templates/         HTML base, livros, listagem, 404, ultimo-registro
tools/             degrade.py, exif_map.json, remarcar.py
build.py           gerador
docs/              saída publicada
```
