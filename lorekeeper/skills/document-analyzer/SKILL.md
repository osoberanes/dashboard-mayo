---
name: document-analyzer
description: Analyzes PDF documents and web pages to extract structured knowledge and save it to an Obsidian vault. Use when the user says "analiza este PDF", "analiza esta página", "extrae la información de", "guarda esta referencia", "procesa este documento", or uploads a PDF file. Generates summaries, key ideas, specific positions, keywords, and bibliography entries formatted for academic citation. Saves results as structured Markdown files to the references/ folder in the Obsidian vault. Do NOT use for video content (use video-analyzer instead) or for writing essays (use essay-writer instead).
metadata:
  author: Oscar S
  version: 1.0.0
  project: lorekeeper
  vault-path: vault/
---

# Document Analyzer

Extrae y estructura conocimiento de PDFs y páginas web, guardándolo como notas permanentes en Obsidian.

---

## Configuración

Ruta del vault de Obsidian: `vault/`
Carpeta de referencias: `vault/referencias/`

Si la ruta es diferente, pregúntale al usuario antes de continuar.

---

## Paso 1: Identificar la fuente

Determina qué tipo de fuente es:

- **PDF subido directamente**: El usuario lo adjuntó a la conversación
- **URL de página web**: Usa WebFetch para obtener el contenido completo
- **Ambos**: Procésalos por separado y genera un archivo por fuente

Si el usuario no especificó idioma de salida, **responde siempre en español**.

---

## Paso 2: Extraer información

Lee el documento completo con atención. Extrae:

### Metadatos bibliográficos
- Título completo
- Autor(es) — apellido, nombre
- Año de publicación
- Editorial / Revista / Institución
- Lugar de publicación (si aplica)
- DOI o URL (si aplica)
- Número de páginas o rango consultado

### Contenido sustantivo

**Tesis y argumentos centrales**
- Argumento principal del autor
- Hipótesis o preguntas de investigación
- Posturas teóricas defendidas
- Conclusiones principales

**Marco teórico y conceptual**
- Escuela de pensamiento (realismo, liberalismo, constructivismo, etc.)
- Conceptos clave utilizados
- Autores y obras con los que dialoga
- Debates académicos en los que se inserta

**Evidencia empírica**
- Datos estadísticos y cuantitativos
- Casos de estudio analizados
- Períodos históricos examinados
- Documentos primarios citados

**Posiciones sobre actores y temas**
- Análisis de Estados específicos (México, EE.UU., etc.)
- Evaluación de organizaciones internacionales
- Postura sobre políticas o eventos concretos
- Críticas a otros enfoques o autores

**Implicaciones y aplicaciones**
- Relevancia para política exterior mexicana
- Lecciones para diseño de política pública
- Áreas que requieren mayor investigación
- Recomendaciones prácticas (si aplica)

### Evaluación crítica
- **Fortalezas del argumento**: Qué defiende bien
- **Limitaciones o sesgos**: Qué deja fuera o qué perspectiva falta
- **Diálogo con otras obras**: Si el texto cita o contradice autores conocidos

### Identificación del marco teórico

El campo `marco-teorico` debe identificar la escuela o enfoque principal del texto. Consulta el archivo `skills/research-agent/references/theoretical-frameworks.md` para ver las categorías estándar del proyecto.

Ejemplos comunes:
- **realismo** — énfasis en poder, interés nacional, anarquía internacional
- **liberalismo** — instituciones, cooperación, interdependencia
- **constructivismo** — normas, identidades, ideas
- **autonomismo** — autonomía, no intervención, tercermundismo (frecuente en contexto mexicano)
- **marxismo/dependencia** — centro-periferia, imperialismo, economía política
- **feminismo** — género, poder, relaciones de dominación

Si el texto no tiene un marco teórico claro, usa: `ecléctico` o `descriptivo`.

---

## Paso 3: Generar el ID único

Construye el ID de esta forma: `[apellido-primer-autor]-[año]-[primera-palabra-titulo]`

Ejemplos:
- `gonzalez-1992-politica`
- `nye-2004-soft`
- `ojeda-1976-alcances`

Si ya existe un archivo con ese ID en la carpeta de referencias, agrega un sufijo: `-b`, `-c`, etc.

---

## Paso 4: Generar la cita bibliográfica

Usa formato **Chicago Author-Date** (estándar en ciencias sociales y política internacional):

**Libro:**
Apellido, Nombre. Año. *Título del libro*. Ciudad: Editorial.

**Artículo en revista:**
Apellido, Nombre. Año. "Título del artículo." *Nombre de la Revista* Volumen (Número): páginas.

**Capítulo en libro editado:**
Apellido, Nombre. Año. "Título del capítulo." En *Título del libro*, editado por Nombre Apellido, páginas. Ciudad: Editorial.

**Página web:**
Apellido, Nombre. Año. "Título de la página." Nombre del sitio. Fecha de acceso. URL.

**Documento gubernamental:**
[Organismo]. Año. *Título del documento*. Ciudad: [Dependencia].

**Reporte de organización internacional:**
[Organización]. Año. *Título del reporte*. Ciudad: [Organización]. URL o DOI.

**Working paper:**
Apellido, Nombre. Año. "Título del paper." Serie de Working Papers, Número. Institución. URL.

**Think tank / policy brief:**
Apellido, Nombre. Año. "Título del brief." Nombre del Think Tank. Fecha de publicación. URL.

---

## Paso 5: Crear el archivo Markdown

Genera el archivo con esta estructura exacta y guárdalo en `vault/referencias/[ID].md`:

```markdown
---
id: [ID-generado]
tipo: pdf | web
fecha-analisis: [fecha de hoy]
titulo: [título completo]
autor: [apellido, nombre]
año: [año]
editorial: [editorial o institución]
marco-teorico: [escuela teórica]
temas: [lista de temas principales]
palabras-clave: [lista de keywords]
mexico: true | false
---

# [Título completo]

**Autor:** [Nombre Apellido]
**Año:** [año]
**Tipo:** [libro / artículo / capítulo / página web]

---

## Tesis central

[2-3 oraciones que capturen el argumento central]

## Resumen

[150-250 palabras]

## Ideas principales

- [Idea 1]
- [Idea 2]
- [Idea 3]
- [...]

## Posiciones específicas

- **[Tema o actor]:** [Postura del autor]
- **[Tema o actor]:** [Postura del autor]

## Marco teórico

[Escuela, concepto central, autores con los que dialoga]

## México en el texto

[Solo si aplica: referencias explícitas al caso mexicano]

## Citas relevantes

> "[Cita textual]" (p. [número])

> "[Cita textual]" (p. [número])

## Evaluación crítica

**Fortalezas:** [qué defiende bien]

**Limitaciones:** [qué deja fuera o qué sesgo tiene]

## Cita bibliográfica

[Cita completa en formato Chicago Author-Date]

---

*Analizado el [fecha]. Tags: [[palabra-clave-1]] [[palabra-clave-2]]*
```

---

## Paso 6: Actualizar el índice maestro

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
gonzalez-1992-politica | política exterior, ONU, autonomía, multilateralismo | autonomismo | 1992 | pdf | true
```

Usa las palabras clave del frontmatter del archivo recién guardado. Si hay más de 6 palabras clave, selecciona las 6 más representativas.

**Manejo de duplicados:**
Si al revisar INDEX.md encuentras que el ID ya existe (porque ya se procesó ese documento anteriormente), informa al usuario y pregunta si desea sobrescribir la entrada existente o cancelar la operación. No añadas una línea duplicada sin confirmar con el usuario.

---

## Paso 7: Confirmar al usuario

Una vez guardado el archivo y actualizado el índice, informa:

1. El ID asignado a la referencia
2. La ruta del archivo creado
3. La cita bibliográfica generada
4. Las 3-5 palabras clave más relevantes para búsqueda futura
5. Si el texto tiene relevancia directa para el caso mexicano

Ejemplo de confirmación:
```
Referencia guardada: gonzalez-1992-politica
Archivo: vault/referencias/gonzalez-1992-politica.md
INDEX.md actualizado

Cita: González González, Guadalupe. 1992. "La política exterior de México..."

Keywords principales: política exterior mexicana, multilateralismo, ONU, autonomía

Relevancia México: Alta — el texto analiza directamente la estrategia mexicana en organismos internacionales.
```

---

## Manejo de errores comunes

**El PDF no tiene texto extraíble (es imagen escaneada):**
Informa al usuario que el PDF es una imagen y no puede extraerse texto automáticamente. Sugiere usar Adobe Acrobat o Google Drive para OCR antes de analizarlo.

**La URL no carga o está detrás de paywall:**
Informa el error específico. Sugiere al usuario que copie y pegue el texto directamente en la conversación.

**Datos bibliográficos incompletos:**
Rellena los campos que puedas y marca los faltantes con `[verificar]`. Nunca inventes datos bibliográficos.

**El texto no es de política internacional:**
Procede de todas formas pero agrega una nota: `relevancia-proyecto: baja` en el frontmatter.

---

## Procesamiento por lotes

Si el usuario proporciona múltiples fuentes a la vez:
1. Procésalas en secuencia
2. Genera un archivo separado por cada fuente
3. Al final, presenta un resumen de todas las referencias guardadas con sus IDs

---

## Notas para búsqueda posterior

Al guardar cada referencia, el skill de investigación (`research-agent`) podrá encontrarla buscando por:
- Palabras en el frontmatter YAML (`palabras-clave`, `temas`, `marco-teorico`)
- Texto libre dentro del archivo
- El campo `mexico: true` para filtrar fuentes sobre el caso mexicano
- El campo `año` para filtrar por período histórico
