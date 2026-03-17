---
name: research-agent
description: The central agentic skill for essay planning on Mexican international politics. Use when the user says "quiero escribir un ensayo sobre", "ayúdame a investigar", "qué enfoque le doy a", "busca en mis referencias sobre", "propón un argumento para", or "analiza el tema de". Searches the local Obsidian vault for existing references, identifies gaps, complements with web search, and proposes 2-3 essay approaches with their central arguments and theoretical tensions. This is the entry point for the writing pipeline — it feeds into essay-architect next.
metadata:
  author: Oscar S
  version: 1.0.0
  project: lorekeeper
  vault-path: vault/
---

# Research Agent

El skill central del pipeline de escritura. Dado un tema, construye el estado del arte desde tu base de conocimiento y propone enfoques argumentativos para el ensayo.

---

## Configuración

Vault: `vault/`
Referencias: `vault/referencias/`

---

## Paso 1: Recibir y descomponer el tema

Cuando el usuario proponga un tema, identifica:

- **Tema central**: el fenómeno o pregunta principal
- **Actor(es) relevantes**: México, EE.UU., organismos internacionales, etc.
- **Período temporal**: ¿histórico, reciente, comparativo?
- **Tipo de pregunta**: descriptiva / explicativa / normativa / predictiva

Si el tema es muy amplio, propón 2-3 delimitaciones posibles y pregunta cuál prefiere antes de continuar.

---

## Paso 2: Buscar en la base de conocimiento local

Usa un sistema de dos capas para evitar cargar archivos innecesarios. **Nunca intentes leer todos los archivos de `vault/referencias/` de una vez.**

---

### Capa 1 — Búsqueda por grep (sin costo de tokens)

Antes de abrir cualquier archivo, usa grep para filtrar por frontmatter YAML. Solo trabaja con los archivos que devuelvan resultados.

**Por palabras clave del tema:**
```
Grep pattern="[término]" path="vault/referencias/" output_mode="files_with_matches"
```

**Por relevancia mexicana:**
```
Grep pattern="mexico: true" path="vault/referencias/" output_mode="files_with_matches"
```

**Por marco teórico:**
```
Grep pattern="marco-teorico:.*[escuela]" path="vault/referencias/" output_mode="files_with_matches"
```

**Por período histórico** (ej. para fuentes de los 90s):
```
Grep pattern="año: 199" path="vault/referencias/" output_mode="files_with_matches"
```

**Por texto libre en el cuerpo:**
```
Grep pattern="[nombre de actor, tratado o evento]" path="vault/referencias/" output_mode="files_with_matches"
```

Ejecuta entre 3 y 5 búsquedas grep combinando términos del tema. Consolida los archivos únicos que aparezcan en los resultados.

---

### Capa 2 — Consulta del índice maestro (si grep devuelve pocos resultados)

Si grep devuelve menos de 3 archivos o el tema es amplio, consulta `vault/INDEX.md`. El índice tiene una línea por referencia con el formato:

```
[id] | [palabras-clave] | [marco-teorico] | [año] | [tipo] | [mexico: true/false]
```

Lee el INDEX.md completo (es un archivo ligero) e identifica IDs adicionales relevantes por sus palabras clave o marco teórico.

---

### Capa 3 — Apertura de archivos completos

Solo abre los archivos identificados en las capas anteriores. Lee únicamente los que sean claramente relevantes al tema. Para cada archivo abierto, extrae:
- Tesis central y resumen
- Posiciones específicas relevantes al tema
- Palabras clave que confirmen relevancia

---

Presenta al usuario cuántas referencias encontraste y cuáles son las más relevantes. Si no hay referencias locales, informa y procede directamente al Paso 3.

---

## Paso 3: Identificar vacíos y complementar con búsqueda web

Analiza qué perspectivas faltan en las referencias locales:

- ¿Hay cobertura teórica pero no empírica?
- ¿Faltan fuentes críticas o contraargumentos?
- ¿El período histórico está cubierto?
- ¿Hay perspectivas internacionales además de la mexicana?

Para cada vacío detectado, realiza búsquedas web dirigidas. Evalúa las fuentes nuevas con los mismos criterios que research-harvester. Pregunta al usuario si quiere agregar las nuevas fuentes a la base antes de continuar.

---

## Paso 4: Construir el estado del arte

Sintetiza lo encontrado en un mapa del debate:

```
## Estado del arte: [tema]

### Lo que sabemos (consensos)
[Puntos en los que la mayoría de fuentes coinciden]

### Debates abiertos
[Tensiones entre autores o perspectivas]

### Posición de México en el debate
[Cómo aparece México — como actor, como caso, como perspectiva]

### Vacíos de investigación
[Lo que nadie ha respondido bien todavía]
```

---

## Paso 5: Proponer enfoques para el ensayo

Genera 2-3 enfoques argumentativos distintos. Cada enfoque debe tener:

- **Título tentativo** del ensayo
- **Tesis central** en una oración
- **Argumento principal** desarrollado en 3-4 oraciones
- **Marco teórico** que lo sustenta
- **Fuentes clave** de tu base que lo respaldan
- **Contraargumento principal** que tendría que enfrentar
- **Tensión central** que lo hace interesante

**Formato de presentación:**

```
## Enfoque 1: [título tentativo]

Tesis: [una oración]

Argumento: [3-4 oraciones desarrollando la posición]

Marco teórico: [escuela y conceptos clave]

Fuentes de respaldo: [IDs de referencias locales]

Contraargumento a enfrentar: [quién diría qué en contra]

Por qué es interesante: [la tensión o paradoja que resuelve]

---

## Enfoque 2: [...]

---

## Enfoque 3: [...]
```

---

## Paso 6: Recibir decisión y preparar el traspaso

Una vez que el usuario elija un enfoque:

1. Confirma la tesis central y el marco teórico
2. Lista las referencias que se usarán
3. Identifica si faltan fuentes para algún argumento específico
4. Genera un **brief de investigación** para el siguiente skill:

```
## Brief para essay-architect

Tema: [tema]
Tesis elegida: [tesis]
Marco teórico: [escuela]
Referencias disponibles: [lista de IDs]
Audiencia probable: [académica / política / divulgación — preguntar si no se sabe]
Extensión aproximada: [preguntar si no se especificó]
Tono: [preguntar si no se especificó]

Puntos que deben aparecer:
1. [punto]
2. [punto]
3. [punto]

Contraargumento principal a abordar:
[descripción]
```

Entrega este brief directamente al essay-architect.

---

## Marco teórico de referencia

Consulta `references/theoretical-frameworks.md` para identificar correctamente las escuelas teóricas y los principios históricos de la política exterior mexicana al construir los enfoques.
