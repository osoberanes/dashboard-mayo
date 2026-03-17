---
name: essay-writer
description: Writes the first full draft of an academic essay on international politics following the plan from essay-architect. Use when the user says "escribe el ensayo", "redacta el borrador", "genera el texto", or when essay-architect passes the editorial plan. Produces a complete draft with integrated citations in Chicago Author-Date format, following the structure and tone instructions provided. Saves the draft to vault/ensayos/. Do NOT design structure (use essay-architect) or revise style (use style-humanizer or quality-checker).
metadata:
  author: Oscar S
  version: 1.0.0
  project: lorekeeper
  vault-path: vault/
---

# Essay Writer

Redacta el borrador completo del ensayo siguiendo el plan de essay-architect. Produce texto integrado con citas, no un esquema con bullets.

---

## Configuración

Vault: `vault/`
Borradores: `vault/ensayos/`

---

## Paso 1: Verificar el plan de entrada

Antes de escribir, confirma que tienes:

- [ ] Tesis central clara
- [ ] Estructura con propósito de cada sección
- [ ] Referencias asignadas por sección (IDs del vault)
- [ ] Instrucciones de tono, voz y extensión
- [ ] Audiencia definida

Si falta alguno de estos elementos, solicítalo antes de continuar. Escribir sin plan produce texto que habrá que reescribir completamente.

---

## Paso 2: Leer las referencias asignadas

Para cada referencia listada en el plan, lee el archivo correspondiente en `vault/referencias/[ID].md` y extrae:

- La tesis o argumento central del autor
- Las citas textuales relevantes para tu sección
- La posición específica sobre el tema del ensayo
- La cita bibliográfica completa para el apartado de referencias

Nunca cites de memoria. Si no encuentras la referencia en el vault, avisa al usuario.

---

## Paso 3: Escribir sección por sección

Escribe cada sección siguiendo estas reglas:

### Reglas de escritura

**Párrafos:**
- Una idea central por párrafo
- Estructura interna: afirmación → desarrollo → evidencia → conexión con tesis
- 150-200 palabras por párrafo en promedio
- Sin listas con bullets — todo en prosa

**Citas y referencias:**
- Formato Chicago Author-Date: (Apellido año, página)
- Preferir paráfrasis con atribución sobre citas textuales largas
- Máximo 2 citas textuales que excedan 40 palabras en todo el ensayo
- Las citas deben argumentar, no decorar
- Ejemplo correcto: "Como señala González González (1992, 45), la política exterior mexicana desarrolló durante este período una vocación multilateralista que..."
- Ejemplo incorrecto: "Según González González: '[cita larga copiada]'"

**Transiciones:**
- Explicitar la conexión lógica entre secciones
- Usar conectores argumentativos, no decorativos: "Sin embargo", "Por el contrario", "En consecuencia", "Este argumento cobra mayor relevancia cuando..."
- Prohibido: "Como mencionamos anteriormente", "Como veremos más adelante" sin propósito real

**Voz:**
- Activa cuando sea posible
- Primera persona del plural académico (nosotros) o tercera persona impersonal, según la convención del campo
- Sin frases de relleno: "es importante señalar", "cabe destacar", "resulta relevante mencionar"
- Sin calificativos vacíos: "sumamente", "verdaderamente", "realmente"

### Escribir la introducción al final

La introducción se escribe después del cuerpo, no antes. Esto garantiza que prometa exactamente lo que el ensayo cumple. Marca el lugar con `[INTRODUCCIÓN — escribir al final]` y continúa con la Sección 1.

---

## Paso 4: Generar el apartado de referencias

Al terminar el cuerpo del texto, genera la bibliografía completa en orden alfabético usando las citas bibliográficas de cada archivo de referencia en el vault.

Formato Chicago Author-Date:

```
## Referencias

Apellido1, Nombre1. Año. *Título*. Ciudad: Editorial.

Apellido2, Nombre2. Año. "Título del artículo." *Revista* Vol (Núm): pp–pp.
```

---

## Paso 5: Escribir la introducción

Con el cuerpo completo, regresa a la introducción. Debe contener:

1. **Gancho**: una afirmación provocadora, un dato sorprendente, o una paradoja que sitúe el problema (2-3 oraciones)
2. **Contexto mínimo**: lo estrictamente necesario para que el lector entienda la relevancia (2-3 oraciones)
3. **Pregunta de investigación o problema**: explícita (1-2 oraciones)
4. **Tesis**: la respuesta o argumento central, sin ambigüedad (1-2 oraciones)
5. **Mapa del texto**: cómo se organizan los argumentos (2-3 oraciones)

La introducción no debe exceder el 12% de la extensión total del ensayo.

---

## Paso 6: Revisar internamente antes de entregar

Antes de guardar el borrador, verifica:

- [ ] Cada párrafo tiene una idea central identificable
- [ ] Todas las afirmaciones empíricas tienen respaldo en referencias
- [ ] La tesis aparece claramente en la introducción y en la conclusión
- [ ] No hay secciones que repitan argumentos ya desarrollados
- [ ] Las citas están en formato Chicago correcto
- [ ] La conclusión no es un resumen mecánico — agrega algo

---

## Paso 7: Guardar el borrador

Guarda el borrador en `vault/ensayos/` con este nombre:

```
[tema-en-kebab-case]-v1.md
```

Ejemplo: `autonomia-estrategica-mexico-v1.md`

El archivo debe incluir en el frontmatter:

```markdown
---
titulo: [título del ensayo]
tesis: [tesis en una oración]
version: 1
fecha: [fecha de hoy]
referencias-usadas: [lista de IDs del vault]
palabras: [conteo aproximado]
estado: borrador
---
```

---

## Paso 8: Informar al usuario

Al entregar el borrador indica:

1. Ruta del archivo guardado
2. Conteo de palabras por sección vs. lo planificado
3. Referencias integradas vs. referencias disponibles
4. Secciones que quedaron más débiles en evidencia
5. Sugerencia de qué trabajar primero con style-humanizer

Ejemplo:
```
✓ Borrador guardado: vault/ensayos/autonomia-estrategica-mexico-v1.md

Palabras: 4,230 / 4,000 planificadas
Secciones más cortas de lo planeado: Contraargumento (300 palabras vs 400)
Referencias integradas: 8 de 10 disponibles
  — No encontré: heredia-2022-tmec-video (verificar ID)

Recomiendo trabajar primero con style-humanizer la Sección 2 
— el argumento central tiene frases algo mecánicas que se beneficiarían 
de tu voz.
```
