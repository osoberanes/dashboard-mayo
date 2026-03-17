---
name: video-analyzer
description: Analyzes YouTube videos of academic conferences, policy debates, and diplomatic interviews to extract structured knowledge and save it to an Obsidian vault. Use when the user shares a YouTube URL and says "analiza este video", "extrae lo que dice", "resume esta conferencia", "guarda este panel", or pastes a youtube.com or youtu.be link. Extracts transcription via Playwright, then generates summaries, key arguments, speaker positions, keywords, and bibliography. Saves results as structured Markdown to the referencias/ folder. Do NOT use for PDF or web page analysis (use document-analyzer instead). If the video has no transcript available, guides the user through manual alternatives.
metadata:
  author: Oscar S
  version: 1.0.0
  project: lorekeeper
  vault-path: vault/
  requires: playwright, python3
---

# Video Analyzer

Extrae y estructura conocimiento de videos de YouTube — conferencias, paneles de política y entrevistas diplomáticas — guardándolo como notas permanentes en Obsidian.

---

## Configuración

Ruta del vault de Obsidian: `vault/`
Carpeta de referencias: `vault/referencias/`
Script de extracción: `scripts/get_transcript.py`

**Instalación única requerida (solo la primera vez):**
```bash
pip install playwright
playwright install chromium
```

---

## Paso 1: Recibir y validar la URL

Cuando el usuario proporcione una URL de YouTube:

1. Confirma que sea una URL válida de YouTube (`youtube.com/watch?v=` o `youtu.be/`)
2. Extrae el ID del video de la URL
3. Procede al Paso 2

Si el usuario pegó solo el ID del video (ej: `dQw4w9WgXcQ`), construye la URL completa: `https://www.youtube.com/watch?v=[ID]`

---

## Paso 2: Extraer la transcripción con Playwright

Ejecuta el script de extracción:

```bash
python scripts/get_transcript.py "URL_DEL_VIDEO" --lang es
```

Para obtener la salida en JSON (más fácil de procesar):
```bash
python scripts/get_transcript.py "URL_DEL_VIDEO" --json --output /tmp/transcript_temp.json
```

**Interpretar el resultado:**

- Si `transcript_available: true` → continúa al Paso 3
- Si `transcript_available: false` → ve al Paso 2b (manejo de fallo)

### Paso 2b: Si no hay transcripción disponible

Informa al usuario con claridad:

```
No encontré transcripción automática para este video. Esto ocurre cuando:
- El canal desactivó los subtítulos automáticos
- El video es muy reciente (YouTube tarda en generarlos)
- El audio tiene demasiado ruido o acentos que YouTube no reconoció

Opciones:
1. Abre el video en YouTube → haz clic en los tres puntos (···) → "Mostrar transcripción"
   Si aparece, copia todo el texto y pégalo aquí.
2. Si el video tiene subtítulos en otro idioma, dime cuál e intento extraerlos:
   python scripts/get_transcript.py "URL" --lang en
3. Si ninguna opción funciona, puedo analizar el video a partir de:
   - El título y descripción
   - Comentarios relevantes
   - Cualquier resumen que encuentre del evento
   (El análisis será menos completo pero puede ser útil como entrada parcial)
```

---

## Paso 3: Extraer información del video

Con la transcripción disponible, extrae y estructura:

### Metadatos del video
- Título completo del video
- Canal / organización que lo publicó
- Fecha de publicación (si está disponible en los metadatos extraídos)
- URL completa
- Duración aproximada (inferida de los timestamps de la transcripción)
- Formato: conferencia / panel / entrevista / debate / documental

### Identificación de hablantes

Para conferencias y paneles es crítico identificar quién dice qué:

- Si hay un solo ponente: identifícalo por el título del video y el canal
- Si hay múltiples participantes: 
  - Usa el título del video para identificar los nombres
  - Marca los turnos de habla con `[Hablante]` cuando cambien
  - Si no puedes identificar quién habla, usa `[Moderador]`, `[Ponente 1]`, `[Ponente 2]`, etc.

### Contenido sustantivo

Extrae de la transcripción completa:

- **Tesis o argumento central**: La idea principal del video en 2-3 oraciones
- **Resumen**: Síntesis de 200-300 palabras (más largo que documentos porque el formato oral pierde densidad)
- **Argumentos principales**: Lista de 5-10 argumentos o puntos desarrollados, cada uno en 2-3 oraciones
- **Posiciones específicas**: Posturas concretas sobre actores, eventos o políticas internacionales
- **Intercambios relevantes**: En debates y paneles, momentos donde hubo desacuerdo o tensión argumentativa — especialmente valioso para ensayos
- **Palabras clave**: 8-15 términos técnicos o conceptuales
- **Marco teórico**: Escuela o corriente que usa(n) el/los ponente(s) — consulta `references/theoretical-frameworks.md`
- **Caso mexicano**: Referencias explícitas a México si las hay

### Evaluación del contenido

- **Credenciales del hablante**: ¿Quién es? ¿Qué institución representa? ¿Por qué su posición importa?
- **Contexto del evento**: ¿Dónde se presentó esto? ¿Para qué audiencia?
- **Fortalezas del argumento**: Qué defiende bien
- **Limitaciones**: Qué deja fuera, qué sesgos son visibles
- **Citas textuales relevantes**: 3-5 citas directas especialmente útiles, con timestamp

---

## Paso 4: Generar el ID único

Construye el ID así: `[apellido-ponente-principal]-[año]-[primera-palabra-titulo]-video`

Ejemplos:
- `castaneda-2019-soberania-video`
- `heredia-2022-tmec-video`
- `panel-cide-2021-seguridad-video` (para paneles sin ponente dominante)

Si ya existe ese ID en referencias/, agrega sufijo: `-b`, `-c`, etc.

---

## Paso 5: Generar la cita bibliográfica

Para videos de YouTube, usa el formato Chicago:

**Video de conferencia institucional:**
```
Apellido, Nombre. Año. "Título del video." Presentado en [Nombre del evento]. 
Canal de YouTube. Fecha de publicación. URL.
```

**Entrevista:**
```
Apellido, Nombre. Año. "Título de la entrevista." Entrevistado por Nombre Entrevistador. 
Canal de YouTube. Fecha de publicación. URL.
```

**Panel o debate:**
```
[Institución organizadora]. Año. "Título del panel." Panel con [Nombres de participantes]. 
Canal de YouTube. Fecha de publicación. URL.
```

**Si no hay fecha visible:**
Usa el año del canal o escribe `[año aproximado]`.

Consulta `references/chicago-citation-guide.md` para casos especiales.

---

## Paso 6: Crear el archivo Markdown

Genera el archivo y guárdalo en `vault/referencias/[ID].md`:

```markdown
---
id: [ID-generado]
tipo: video
formato: conferencia | panel | entrevista | debate | documental
fecha-analisis: [fecha de hoy]
titulo: [título completo del video]
ponente-principal: [apellido, nombre]
otros-participantes: [nombres si aplica]
canal: [nombre del canal de YouTube]
año: [año de publicación]
url: [URL completa]
duracion-aprox: [minutos estimados]
marco-teorico: [escuela teórica]
temas: [lista de temas principales]
palabras-clave: [lista de keywords]
mexico: true | false
transcripcion-disponible: true | false
---

# [Título completo del video]

**Ponente:** [Nombre completo] — [Cargo e institución]
**Formato:** [conferencia / panel / entrevista / debate]
**Canal:** [Nombre del canal]
**Año:** [año]
**URL:** [URL]

---

## Tesis central

[2-3 oraciones que capturen el argumento central]

## Resumen

[200-300 palabras]

## Argumentos principales

- [Argumento 1 — 2-3 oraciones]
- [Argumento 2 — 2-3 oraciones]
- [...]

## Posiciones específicas

- **[Tema o actor]:** [Postura del ponente]
- **[Tema o actor]:** [Postura del ponente]

## Intercambios relevantes

> [Solo para paneles y debates: momentos de tensión o desacuerdo argumentativo]

**[Ponente A]:** [postura]
**[Ponente B]:** [contrapostura]

## Marco teórico

[Escuela, conceptos centrales, autores citados]

## Credenciales del hablante

[Quién es, qué institución representa, por qué su voz importa en este debate]

## México en el video

[Solo si aplica: referencias explícitas al caso mexicano]

## Citas textuales relevantes

> "[Cita textual]" [[MM:SS]]

> "[Cita textual]" [[MM:SS]]

## Evaluación crítica

**Fortalezas:** [qué defiende bien]

**Limitaciones:** [qué deja fuera o qué sesgo tiene]

## Cita bibliográfica

[Cita completa en formato Chicago]

---

*Analizado el [fecha]. Tags: [[palabra-clave-1]] [[palabra-clave-2]]*
```

---

## Paso 7: Actualizar el índice maestro

Después de guardar el archivo de referencia, añade una línea al archivo `vault/INDEX.md`.

**Formato de la línea:**
```
[id] | [palabras-clave separadas por coma] | [marco-teorico] | [año] | [tipo] | [mexico: true/false]
```

**Procedimiento:**
1. Verifica si `vault/INDEX.md` existe.
   - Si **no existe**: créalo con el encabezado estándar (ver abajo) y luego añade la línea.
   - Si **existe**: añade la línea al final del bloque de entradas, antes de cualquier línea en blanco final.

**Encabezado estándar si INDEX.md no existe:**
```markdown
# Índice maestro de referencias

Formato: `id | palabras-clave | marco-teorico | año | tipo | mexico`
Actualizado automáticamente por document-analyzer y video-analyzer.
No editar manualmente — usar los skills para mantener consistencia.

---

```

**Ejemplo de línea a añadir:**
```
castaneda-2019-soberania-video | soberanía, política exterior, AMLO, no intervención | autonomismo | 2019 | video | true
```

Usa las palabras clave del frontmatter del archivo recién guardado. Si hay más de 6 palabras clave, selecciona las 6 más representativas.

---

## Paso 8: Confirmar al usuario

Una vez guardado el archivo y actualizado el índice, informa:

1. El ID asignado
2. La ruta del archivo creado
3. La cita bibliográfica generada
4. Las 3-5 palabras clave más relevantes
5. Si hay intercambios de debate particularmente útiles para ensayos argumentativos
6. Si el video tiene relevancia directa para el caso mexicano

Ejemplo:
```
✓ Referencia guardada: castaneda-2019-soberania-video
📁 vault/referencias/castaneda-2019-soberania-video.md
📋 vault/INDEX.md actualizado

Cita: Castañeda, Jorge. 2019. "Soberanía y política exterior en el siglo XXI."
      Conferencia magistral CIDE. YouTube. URL.

Keywords principales: soberanía, política exterior mexicana, AMLO, relación México-EE.UU.

Nota: El video contiene un intercambio relevante con el moderador sobre el concepto
de no intervención — útil para argumentar posiciones encontradas en tu ensayo.

Relevancia México: Alta — análisis directo de la política exterior del gobierno actual.
```

---

## Diferencias clave con document-analyzer

| Aspecto | document-analyzer | video-analyzer |
|---|---|---|
| Fuente | PDF / página web | Video de YouTube |
| Densidad | Alta (texto académico) | Media (formato oral) |
| Resumen | 150-250 palabras | 200-300 palabras |
| Hablantes | Generalmente uno | Puede ser múltiple |
| Citas | Con número de página | Con timestamp [MM:SS] |
| Valor especial | Argumentos elaborados | Intercambios y debate en vivo |
| Script requerido | No | Sí (get_transcript.py) |

---

## Manejo de casos especiales

**Video en inglés con subtítulos en español:**
```bash
python scripts/get_transcript.py "URL" --lang es
```
Si no hay en español, extrae en inglés y avisa al usuario. Puedes traducir los fragmentos clave al analizar.

**Video muy largo (+2 horas):**
Pregunta al usuario si quiere el análisis completo o de una sección específica (ej: "solo el panel de las 3pm"). Si es completo, procesa toda la transcripción pero enfoca el análisis en los argumentos sustantivos, no en saludos, logística o preguntas del público sin respuesta elaborada.

**Canal institucional sin subtítulos automáticos:**
Algunos canales de la SRE, UNAM o cancillerías extranjeras tienen sus propios subtítulos como archivos separados. En ese caso, sugiere al usuario descargarlos manualmente desde la configuración del video en YouTube Studio.

**Video eliminado o privado:**
Informa al usuario e intenta buscar una versión alternativa en otros canales con el título del video.
