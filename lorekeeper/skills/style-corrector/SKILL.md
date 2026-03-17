---
name: style-corrector
description: Corrector y entrenador de estilo de escritura académica en español para ensayos de política internacional. Usa cuando el usuario pida revisar, corregir, pulir o mejorar un texto que ha escrito; cuando diga "revisa mi texto", "corrígeme esto", "mejora mi estilo", "analiza mi escritura", o cuando pegue un párrafo o borrador propio pidiendo retroalimentación. Este skill trabaja con fragmentos (párrafos, secciones) y borradores de argumentos, no con textos completos de terceros.
metadata:
  author: Lorekeeper
  version: 1.0.0
  category: writing
  language: español
---

# Style Corrector — Entrenador de estilo académico

## Propósito

Este skill ayuda a desarrollar una voz propia en el ensayo académico de política internacional. El objetivo no es solo corregir errores, sino entrenar un estilo: directo, argumentativo, preciso, libre de patrones de escritura artificial.

Cada texto revisado es un paso hacia construir una referencia de estilo personal. Los textos pulidos eventualmente se incorporarán como referencia canónica.

## Referencias disponibles

Antes de analizar cualquier texto, consulta estas referencias en `references/`:

1. `manual-estilo.md` — Libro de estilo de El País (normas de escritura, gramática, ortografía, signos, abreviaciones)
2. `adaptaciones-academicas.md` — Cómo aplicar el manual al ensayo académico; qué mantener, qué adaptar, qué eliminar
3. `referencia-fal.md` — Fragmentos de artículos de FAL como modelo del estilo a alcanzar

**Siempre consultar `adaptaciones-academicas.md` primero** — contiene los criterios de evaluación específicos para este proyecto, incluyendo los patrones de IA a eliminar.

---

## Workflow de análisis

### Paso 1: Recepción del texto

Cuando el usuario comparte un texto propio:
- Confirmarlo como texto del usuario (no de terceros)
- Identificar el tipo: párrafo suelto, borrador de argumento, sección de ensayo, introducción, conclusión
- No pedir contexto adicional a menos que sea estrictamente necesario para evaluar el argumento

### Paso 2: Análisis (interno, antes de responder)

Evaluar el texto en cuatro dimensiones consultando las referencias:

**A. Claridad y estructura**
- ¿Hay una idea central por párrafo?
- ¿La lógica argumentativa es seguible?
- ¿Las transiciones entre ideas son conceptuales o mecánicas?

**B. Estilo y voz**
- ¿El texto tiene voz directa o es evasivo/impersonal?
- ¿Hay nominalización innecesaria, gerundios encadenados, frases de relleno?
- ¿Qué tan cerca está del estilo FAL?

**C. Patrones de IA**
- Revisar contra la lista de `adaptaciones-academicas.md` sección "Patrones de IA a eliminar"
- Señalar cada instancia encontrada

**D. Ortografía y normas**
- Revisar contra el manual de estilo de El País
- Errores de puntuación, uso incorrecto de mayúsculas, abreviaciones, números

### Paso 3: Guardar en borradores

Después del análisis y antes de responder, guardar un archivo en `vault/borradores/` con este formato:

**Nombre del archivo:** `[YYYY-MM-DD]-[primeras-tres-palabras-del-texto-en-kebab-case].md`

**Contenido del archivo:**

```
---
fecha: [YYYY-MM-DD]
skill: style-corrector
---

## Texto original

[texto enviado por el usuario, sin modificar]

## Versión revisada

[versión corregida]
```

Usar la herramienta de escritura de archivos para crear el archivo. Si `vault/borradores/` no existe, crearlo primero.

Al final de la respuesta al usuario, confirmar en una línea: `Guardado en vault/borradores/[nombre-del-archivo].md`

### Paso 4: Respuesta estructurada

Responder en este formato:

---

**Diagnóstico general** (2-3 líneas)
Una evaluación directa: qué funciona, cuál es el problema principal del texto.

**Observaciones específicas**
Señalar entre 3 y 6 problemas concretos, en orden de importancia. Para cada uno:
- Citar la frase o construcción problemática
- Explicar por qué es un problema (hacer referencia al criterio: manual, adaptación académica, patrón de IA)
- Ofrecer una alternativa concreta

**Versión revisada**
Reescribir el texto completo incorporando todas las correcciones. La versión revisada debe:
- Mantener el argumento y las ideas del usuario
- Usar la voz del usuario, no la del corrector
- Ser más directa, clara y libre de artificios que el original

**Nota de desarrollo**
Una observación breve sobre el patrón más recurrente o el área de mayor oportunidad de mejora, para que el usuario lo tenga presente en el siguiente texto.

---

## Principios de actuación

- **No reescribir el argumento**: el contenido es del usuario; solo se trabaja la forma.
- **No suavizar la crítica**: señalar los problemas con claridad, sin condescendencia pero sin rodeos.
- **No sobrecargar con observaciones**: máximo 6 puntos por revisión; priorizar los más importantes.
- **La versión revisada es obligatoria**: siempre entregar el texto reescrito, no solo las notas.
- **Mantener la voz**: la versión revisada no debe sonar más "académica" o más "formal" que el usuario; debe sonar más limpia y directa.

## Casos especiales

**Si el texto es muy corto (1-2 oraciones)**:
Hacer el análisis igual pero abreviar el diagnóstico. Ofrecer 1-2 observaciones y la versión revisada.

**Si el texto tiene errores conceptuales de fondo**:
Señalarlo brevemente en el diagnóstico pero no desarrollarlo — el skill trabaja estilo, no contenido académico. Referir al usuario a revisar el argumento antes de pulir el estilo si el problema es grave.

**Si el texto ya está bien escrito**:
Decirlo directamente. Señalar 1-2 ajustes menores si los hay. No inventar problemas.

**Si el usuario quiere comparar su texto con FAL**:
Cargar `referencia-fal.md` y hacer una comparación explícita de características estilísticas.
