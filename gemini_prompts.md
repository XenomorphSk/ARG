# Prompts de imagem

Um prompt por imagem, na ordem das entradas. Os prompts estão em inglês, pensados para o Gemini.

Legenda:

- **[FOTO REAL]**: dá para tirar você mesmo, com qualquer celular, num dia de neblina ou dentro de casa. Preferível à IA, porque foto real resiste melhor a quem procura falhas.
- **[IA]**: precisa de geração (a estação, as balizas, a luz no morro, o vulto).

Regras que valem para todas:

- Nada de mãos, nada de texto legível, nada de rosto em close.
- O outro observador, quando aparece, é sempre distante, desfocado, confundível com uma árvore ou um poste.
- Gere em boa resolução e deixe a degradação para `tools/degrade.py`. Salve em `assets/raw/` com o nome indicado (qualquer extensão; a saída vira `.jpg`).
- O sufixo padrão abaixo pode ser colado no fim de qualquer prompt:

> *Style suffix:* amateur phone photo, 2012, slightly blurry, tilted framing, low light noise, muted colors, no text, no people in focus, no hands.

---

## Entrada 1, "Primeiro dia lá em cima"

### `estacao-01.jpg` [IA]
Small weathered one-story masonry weather station building on a grassy mountain top, whitewashed walls with grey stains, a 10 meter steel mast with a cup anemometer and wind vane beside it, a white louvered instrument shelter on a post, two small solar panels on a frame. Thick fog, visibility about 30 meters, the far edge of the scene dissolving into white. Overcast afternoon light, wet grass. Amateur phone photo, 2012, slightly blurry, tilted framing, muted colors, no text, no people.

### `estrada-01.jpg` [FOTO REAL ou IA]
View through the dirty windshield of an old pickup truck climbing a narrow red dirt track on a steep hillside in southern Brazil, araucaria pines and wet scrub on both sides, fog ahead. Dashboard edge visible at the bottom, no hands, no steering wheel close up. Amateur phone photo, 2012, motion blur, tilted framing, reflections on the glass.

## Entrada 2, "Como se mede a neblina"

### `balizas-01.jpg` [IA]
View from a porch looking northwest over a sloping wet pasture in fog. In the foreground at about 50 meters, a slim white-painted concrete post with a small lamp on top. Further away, faint in the fog at about 200 meters, the silhouette of a single isolated araucaria tree with a cup-shaped crown. Nothing else visible beyond, just grey. Amateur phone photo, 2012, slightly blurry, tilted framing, low contrast, muted colors, no text, no people.

### `b1-poste.jpg` [FOTO REAL possível]
Close shot of a white-painted concrete post (about 3 meters) with a small old lamp fixture on top, standing in wet grass, fog behind it, paint peeling at the base. Amateur phone photo, 2012, slightly blurry, overcast flat light, no text.

## Entrada 3, "A rotina"

### `abrigo-01.jpg` [IA, ou FOTO REAL se houver um abrigo meteorológico acessível]
A white wooden louvered meteorological instrument shelter (Stevenson screen) on four legs in wet grass, early morning, dew on the slats, door closed, fog in the background. Amateur phone photo, 2012, slightly tilted, cold bluish morning light, low light noise.

### `caderno-01.jpg` [FOTO REAL]
An open hardcover logbook on a wooden desk under a yellow desk lamp at night, ruled columns filled with small blue handwriting that is too blurry to read, a blue ballpoint pen beside it, a mug with coffee stains. Shallow focus, the writing completely unreadable. Amateur phone photo, 2012, overexposed flash, warm color cast, grain.

## Entrada 4, "Sinal"

### `neblina-04.jpg` [IA] (detalhe plantado)
Dusk over a mountain pasture, a sea of fog rising from the valley and lying flat at fence height, the top of a single araucaria tree sticking out of the fog, pale pink sky above. **Far in the background, near the horizon on the right third, a single tiny faint warm-white point of light inside the fog, barely visible, not centered, easy to miss.** Amateur phone photo, 2012, slightly blurry, tilted framing, low light noise.
> O texto da entrada não comenta a luz. Não aumente o ponto. Ele precisa ser descoberto só na releitura.

## Entrada 5, "Pinhão no fogareiro"

### `pinhao-01.jpg` [FOTO REAL]
A pile of brown araucaria seeds (pinhão) on a wet wooden plank, some broken pine cone scales around them, overcast light. Amateur phone photo, 2012, slightly blurry, no hands.

### `fogareiro-01.jpg` [FOTO REAL]
A small camping gas stove on a cluttered kitchen counter with a small dented pressure cooker on top, steam, a cutting board with chopped onion beside it, a fogged-up window behind. Amateur phone photo, 2012, overexposed flash, warm cast, no hands, no readable labels.

## Entrada 6, "Dia de sol"

### `sol-01.jpg` [IA] (EXIF 03:12)
Bright clear midday view from a mountain top looking northwest: a grassy slope going down, a single araucaria tree, a rusty lattice steel tower about 15 meters high with empty mounts, a small iron cross at the edge of a cliff in the distance, a valley, and on the opposite ridge a thin grey transmission tower. Behind, layers of blue mountain ridges. No houses, no roads. Hard sunlight, deep blue sky. Amateur phone photo, 2012, slightly washed out, tilted framing, no text.
> O EXIF diz 03:12 da madrugada. A foto é claramente de meio-dia.

### `sol-02.jpg` [FOTO REAL possível, se houver uma araucária isolada]
A single isolated araucaria tree in a pasture, late afternoon sun, long shadow, one broken branch on the left side of the crown. Amateur phone photo, 2012, slightly blurry, warm low sun, lens flare.

## Entrada 7, "O armário"

### `armario-01.jpg` [FOTO REAL]
An old grey steel two-door office cabinet in the corner of a small room with peeling paint, a small round lock, a faded yellowed label stuck on the door (unreadable), a dusty floor. Night, single ceiling bulb. Amateur phone photo, 2012, overexposed flash, harsh shadows, grain, no readable text.

## Entrada 8, "Uma luz"

### `luz-01.jpg` [IA]
Almost entirely grey-black night photo through a window into thick fog. Faint reflection of the glass. Somewhere slightly left of center, a soft, small, warm-white smudge of light, very blurred, impossible to identify. Heavy sensor noise, the image almost unusable. Amateur phone photo, 2012, night, extreme low light noise, slightly out of focus.

## Entrada 10, "A chave"

### `livros-01.jpg` [FOTO REAL]
A stack of seven old dark green hardcover ledgers on a wooden table, worn corners, numbers painted on the spines with white correction fluid (blurred, not readable), a folded blue nylon jacket beside them, a big old flashlight. Afternoon rain light through a window. Amateur phone photo, 2012, slightly blurry, muted colors.

## Entrada 11, "Os livros do Osmar"

### `livro-pagina-01.jpg` [FOTO REAL]
Close-up of an old yellowed ledger page with ruled columns and small slanted blue handwriting, a brown coffee ring stain on the corner, shot at an angle so the handwriting is out of focus and unreadable. Warm lamp light. Amateur phone photo, 2012, shallow depth of field, grain.

## Entrada 13, "Anotando"

### `janela-01.jpg` [IA ou FOTO REAL]
A dark window at night seen from inside a room, fog outside, the glass has five small ink pen marks at different heights, each with a tiny scribble beside it (not readable), faint reflection of a room lamp in the glass. Nothing visible outside except grey. Amateur phone photo, 2012, night, low light noise, slightly tilted.

## Entrada 14, "A cruz"

### `cruz-noite-01.jpg` [IA]
Night photo into thick fog from a window. Low in the frame, a small soft warm-white light with a faint halo, very blurry. No cross visible, no shapes. Heavy noise, nearly black. Amateur phone photo, 2012, night, extreme low light noise, out of focus.

## Entrada 16, "B3"

### `b3-noite.jpg` (não gerar)
Esta imagem não existe de propósito. A entrada usa o defeito `imagem-quebrada`.

## Entrada 18, "Parei"

### `sensor-01.jpg` [IA]
A small grey forward-scatter visibility sensor mounted on a steel mast, two short angled arms (emitter and receiver) facing each other with a gap between them, a cable going down the mast, fog behind, droplets on the metal. Shot from below, afternoon flat light. Amateur phone photo, 2012, slightly blurry, tilted framing, no text, no logos.

## Entrada 20, "Sete dias"

### `araucaria-dia.jpg` [IA ou FOTO REAL] (EXIF 03:12)
A single araucaria tree in a pasture under high fog, about 200 meters away, flat white daylight, one broken branch on the left side. **At the base of the trunk, slightly to the right, a very faint thin vertical dark shape about the height of a person, so blurred it could be a fence post or a shadow.** Amateur phone photo, 2012, slightly blurry, low contrast, muted colors.
> O EXIF diz 03:12 da madrugada. O texto diz "hoje".

## Entrada 23, sem título

### `postes-01.jpg` [IA] (EXIF 1994:07:01 03:00:00)
Night photo through a window into thick fog. In the foreground at about 50 meters, a white concrete post with a small yellow lamp on top, glowing softly in the fog. **Just behind and slightly to the left of the post, a second vertical dark shape of almost the same height, very blurred, holding something faintly lit in front of it at chest height, a small pale rectangle or a weak lamp.** It could be read as a second post. No face, no details, no hands. Amateur phone photo, 2012, night, low light noise, overexposed by the lamp, slightly tilted.
> O EXIF tem data de 1994. Não existia celular com câmera.
