# Pipeline de Instagram de Eddy IA (100% gratis)

Genera y publica solo los reels, carruseles y posts de Eddy IA con el **Profe Eddy**, el personaje de la
marca, y la voz en español de Perú. Tú solo grabas las demos y apruebas las piezas una vez por semana.

```
Miércoles 9:17          Tú (5-10 min)            Cada hora                  Lunes 8:23
┌──────────────┐      ┌───────────────┐      ┌─────────────────┐      ┌──────────────┐
│ 1 · Generar  │ ───▶ │ Revisas el PR │ ───▶ │ 2 · Publicar en │ ───▶ │ 3 · Métricas │
│  guion, voz, │      │ y haces merge │      │ Instagram a la  │      │  reporte.md  │
│ video, fotos │      │  = aprobado   │      │  hora indicada  │      │              │
└──────────────┘      └───────────────┘      └─────────────────┘      └──────────────┘
```

## Qué usa y cuánto cuesta

| Parte | Herramienta | Costo |
| --- | --- | --- |
| Automatización y horarios | GitHub Actions (repositorio público) | Gratis |
| Alojar videos e imágenes para Instagram | GitHub Pages | Gratis |
| Voz del Profe Eddy | edge-tts, voces neuronales `es-PE-AlexNeural` / `es-PE-CamilaNeural` | Gratis |
| Personaje, montaje de video, carruseles | Código propio (Pillow + ffmpeg) | Gratis |
| Guiones de meses siguientes (opcional) | API de Gemini, nivel gratuito de Google AI Studio | Gratis |
| Publicar y leer métricas | API oficial de Instagram (Graph API), app de Meta en modo desarrollo | Gratis |
| Tipografías Poppins e Inter | Google Fonts (licencia OFL) | Gratis |

Los guiones y copies de las 16 piezas del primer mes (23 de noviembre al 19 de diciembre de 2026) ya
están escritos en `contenido/`. Gemini solo hace falta cuando agregues meses nuevos.

## Instalación (una sola vez, unos 40 minutos)

### 1. Sube el proyecto a GitHub

1. Crea una cuenta en [github.com](https://github.com) si no tienes.
2. Crea un repositorio **público** llamado `eddy-instagram`. Tiene que ser público para que Pages y
   Actions sean gratis. Los secretos (tokens) nunca se ven.
3. Sube todo el contenido de esta carpeta (botón *Add file → Upload files* o con `git push`).
   Asegúrate de que se suba la carpeta oculta `.github`.

### 2. Activa GitHub Pages

*Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs` → Save.*
En unos minutos aparece tu dirección, por ejemplo `https://tu-usuario.github.io/eddy-instagram`.

Guárdala como variable: *Settings → Secrets and variables → Actions → pestaña Variables → New variable*
con el nombre `PUBLIC_BASE_URL` y esa dirección como valor (sin `/` al final).

### 3. Deja que GitHub Actions abra los PR

*Settings → Actions → General → Workflow permissions* → marca **Read and write permissions** y
**Allow GitHub Actions to create and approve pull requests** → Save.

### 4. Conecta Instagram (gratis, sin revisión de Meta)

Ya está configurado para la cuenta **@eddyai1995**:

- App de Meta **Eddy IA Publicador** (modo desarrollo) con los permisos `instagram_basic`,
  `instagram_content_publish`, `instagram_manage_insights`, `pages_show_list`, `pages_read_engagement`
  y `business_management`.
- Portfolio comercial **Eddy IA**, con la cuenta de Instagram y el usuario del sistema **Eddy Bot**.
- El token de Eddy Bot **no vence**. Si algún día hay que cambiarlo: business.facebook.com →
  Configuración → Usuarios del sistema → Eddy Bot → **Generar token** (app Eddy IA Publicador,
  caducidad *Nunca*, los 6 permisos de arriba).

Secretos en GitHub (*Settings → Secrets and variables → Actions*):

- `IG_USER_ID` → `17841475316920941` (ID de @eddyai1995)
- `IG_ACCESS_TOKEN` → el token de Eddy Bot

Para comprobar que todo funciona: *Actions → 4 · Probar conexión con Instagram → Run workflow*.

### 5. Opcionales

- **Gemini (guiones de meses nuevos):** crea una clave gratis en [aistudio.google.com](https://aistudio.google.com)
  → secreto `GEMINI_API_KEY`. Ojo: en el nivel gratuito Google puede usar lo que envías para mejorar sus
  modelos; solo se envían datos de marketing, nunca datos de alumnos.
- **Voz femenina:** variable `EDDY_VOZ` = `es-PE-CamilaNeural`.
- **Música de fondo:** coloca un archivo libre de derechos en `marca/musica.mp3`; se mezcla bajito.

### 6. Graba las demos

Sigue la lista de [`demos/LEEME.md`](demos/LEEME.md) y sube los MP4 a la carpeta `demos/`.
Son la prueba de cada bondad: sin ellas, los reels salen con una tarjeta de texto.

### 7. Prueba

1. *Actions → 1 · Generar piezas → Run workflow*, con `desde` = `2026-11-23` y `dias` = `7`.
2. Se abre un **Pull Request** con las portadas, los enlaces a los videos y los textos. Revísalos.
3. *Actions → 2 · Publicar en Instagram → Run workflow* con **Solo simular** marcado: muestra qué publicaría.

## El ciclo de cada semana

1. **Miércoles:** llega un PR "Piezas para aprobar" con todo lo de la semana siguiente.
2. **Tú revisas** cada pieza: mira el reel, lee el texto y marca la lista *Revisar*.
   - Para **frenar** una pieza: en el PR edita `calendario/calendario.csv` y cambia su estado a `pausado`.
   - Para **corregir** un guion o un copy: edita `contenido/<id>.json` en `main`, cierra el PR y vuelve a
     correr *1 · Generar piezas* con ese id y **forzar** marcado.
3. **Haces merge** del PR. Desde ese momento, las piezas quedan **aprobadas**.
4. **Publicación:** cada hora el flujo *2 · Publicar* revisa el calendario y publica lo que toca.
   El calendario se actualiza solo con el enlace de cada publicación.
5. **Lunes:** `metricas/reporte.md` muestra alcance, guardados y compartidos de cada pieza y por pilar.

## Agregar el mes siguiente

Agrega filas a `calendario/calendario.csv` con estado `pendiente`:

| Columna | Ejemplo | Valores |
| --- | --- | --- |
| `id` | `s5-21dic-reel` | único, sin espacios |
| `fecha`, `hora` | `2026-12-21`, `19:00` | hora de Lima |
| `formato` | `reel_avatar` | `reel_avatar`, `reel_demo`, `reel_faq`, `reel_antes_despues`, `carrusel`, `post`, `story` |
| `pilar`, `bondad`, `titulo` | texto libre | orientan el guion |
| `modulo` | `correccion` | `correccion`, `contenido`, `plan`, `gestion` (color del carrusel) |
| `demo` | `demos/ahorro-lote.mp4` | solo para reels |

Si existe `contenido/<id>.json`, se usa ese guion. Si no, lo escribe Gemini (si configuraste la clave) y
queda guardado para que lo revises en el PR. Copia cualquiera de los JSON del primer mes como modelo.
Para resaltar una palabra en pantalla, enciérrala entre asteriscos: `Ahorra *hasta 90%*`.

## Probar en tu computadora (opcional)

```bash
pip install -r requirements.txt          # y ffmpeg instalado
python -m pipeline.generar --ids s1-23nov-reel --forzar
python -m pipeline.publicar --simular
```

Los archivos quedan en `docs/media/<id>/`. Las tipografías se descargan solas de Google Fonts y los
dibujos del Profe Eddy se generan solos desde `avatar/profe_eddy.py` la primera vez. Para cambiar el
personaje, edita ese archivo y borra la carpeta `avatar/sprites`.

## Límites y cuidados

- **Voz:** edge-tts usa el servicio de voz de Microsoft Edge sin cuenta; es gratis pero no oficial y
  podría cambiar. Si falla, el reel sale con una voz simulada y el PR lo avisa en rojo: no lo apruebes así.
- **Instagram:** la API permite hasta 100 publicaciones cada 24 horas; carruseles de 2 a 10 láminas.
  Las encuestas y stickers de las stories se agregan a mano en la app.
- **Repositorio público:** las piezas aprobadas se pueden ver en GitHub un par de días antes de
  publicarse. No subas nada confidencial.
- **Revisión humana:** el pipeline revisa reglas de marca (el "hasta" del 90%, frases prohibidas, largo
  del copy), pero la exactitud del producto la confirma una persona antes del merge.
- GitHub pausa los flujos programados de repos sin actividad en 60 días; como este repo hace commits
  cada semana, no debería pasar.

## Estructura

```
calendario/calendario.csv   qué se publica y cuándo (y su estado)
contenido/<id>.json         guion, textos de pantalla, copy y hashtags de cada pieza
demos/                      grabaciones reales de Eddy
avatar/                     el Profe Eddy (SVG editable + sprites)
marca/                      tipografías y música opcional
pipeline/                   el código (voz, lip-sync, montaje, carruseles, Instagram, métricas)
docs/media/                 piezas generadas, servidas por GitHub Pages
.github/workflows/          los 4 flujos automáticos
```
