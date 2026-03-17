---
name: style-humanizer
description: Rewrites selected text blocks to match the author's personal voice and eliminate generic AI-sounding patterns. Use when the user says "humaniza este texto", "reescribe con mi estilo", "quita el tono de IA", "esto suena muy genérico", "elimina las muletillas", or pastes a block of text to revise. Works on selected passages, not the full essay at once. Requires the user to provide examples of their own writing to calibrate the voice. Do NOT use for fact-checking or citation verification (use quality-checker).
metadata:
  author: Oscar S
  version: 1.0.0
  project: lorekeeper
  vault-path: vault/
---

# Style Humanizer

Reescribe bloques de texto para que suenen como tú, no como una IA. Elimina generalidades, muletillas y patrones de escritura genérica.

---

## Paso 1: Calibrar la voz del autor

**La primera vez que uses este skill**, necesitas proporcionar ejemplos de tu escritura. Sin esto, el skill no puede calibrar tu voz y producirá texto genérico diferente pero igualmente impersonal.

Solicita al usuario:

```
Para calibrar tu voz, necesito ver ejemplos de tu escritura. 
Por favor comparte:

1. Un párrafo de un ensayo o texto que hayas escrito y que 
   consideres representativo de cómo escribes en tu mejor momento
2. (Opcional) Un segundo ejemplo de otro texto tuyo

No importa el tema — me interesa el ritmo, la estructura 
de tus oraciones y cómo construyes los argumentos.
```

Una vez recibidos los ejemplos, analiza y guarda en memoria:

- **Longitud de oraciones**: ¿cortas y directas? ¿largas y subordinadas?
- **Puntuación característica**: uso de comas, punto y coma, guiones
- **Conectores favoritos**: qué palabras usa para encadenar ideas
- **Posición de la tesis**: ¿al inicio del párrafo o al final?
- **Relación con las fuentes**: ¿cita mucho? ¿parafrasea? ¿dialoga críticamente?
- **Tono**: ¿distante y académico? ¿directo y propositivo? ¿con ironía ocasional?
- **Patrones que evita**: qué construcciones no aparecen en su escritura

Guarda este perfil como `vault/recursos/perfil-de-voz.md` para usarlo en sesiones futuras.

---

## Paso 2: Recibir el bloque a reescribir

El usuario pega un bloque de texto del ensayo. Trabaja en bloques de máximo 300-400 palabras a la vez — más que eso pierde coherencia.

Si el usuario pega texto muy largo, divídelo en bloques y procesa uno por uno, confirmando cada uno antes de continuar.

---

## Paso 3: Diagnosticar el texto

Antes de reescribir, identifica los problemas específicos:

**Patrones de escritura genérica (slop) a eliminar:**

- Frases de apertura vacías: "Es importante señalar que", "Cabe destacar que", "Resulta fundamental mencionar", "En este sentido"
- Calificativos sin sustancia: "sumamente importante", "verdaderamente relevante", "de vital importancia"
- Pasivo innecesario cuando hay un agente claro
- Transiciones mecánicas: "Por otro lado", "Asimismo", "En conclusión" al inicio de párrafo sin función argumentativa real
- Generalizaciones no respaldadas: "históricamente", "siempre", "todos los países", "la comunidad internacional"
- Estructura formulaica: afirmación → cita → "esto demuestra que" → repetición de la afirmación
- Eufemismos académicos: "se podría argumentar que", "parecería ser que", "en cierta medida"

**Informa al usuario qué encontraste:**
```
Detecté estos patrones en el bloque:
- 3 frases de apertura vacías
- 2 construcciones pasivas innecesarias  
- 1 generalización no respaldada ("la comunidad internacional ha reconocido")
- Estructura formulaica en el segundo párrafo
```

---

## Paso 4: Reescribir

Reescribe el bloque aplicando:

1. **Voz del autor** según el perfil calibrado
2. **Eliminación de todos los patrones detectados**
3. **Preservación del argumento** — el contenido sustantivo no cambia, solo la forma
4. **Preservación de las citas** — las referencias y citas textuales se mantienen exactamente

**Qué no cambiar:**
- El argumento central del párrafo
- Las afirmaciones empíricas respaldadas
- Las citas textuales y sus atribuciones
- Los datos y cifras

**Qué sí cambiar:**
- La estructura de las oraciones
- El vocabulario redundante o genérico
- El orden de las ideas si mejora la claridad
- Las transiciones mecánicas por conexiones lógicas reales

---

## Paso 5: Presentar la comparación

Muestra siempre el antes y el después para que el usuario decida:

```
## Original:
[texto original]

## Reescrito:
[texto reescrito]

## Cambios realizados:
- Eliminé "Es importante señalar que" al inicio
- Convertí la voz pasiva en "México adoptó" en lugar de "fue adoptado por México"
- Reemplacé "la comunidad internacional" con los actores específicos mencionados en la referencia
- Acorté el último párrafo eliminando la repetición de la tesis
```

---

## Paso 6: Iterar

El usuario puede:
- Aceptar el texto reescrito → pasa al siguiente bloque
- Pedir ajustes específicos → reescribe de nuevo
- Rechazar y mantener el original → respeta la decisión sin insistir

Si el usuario rechaza la reescritura dos veces seguidas, pregunta qué aspecto del original prefiere conservar — puede revelar algo sobre su voz que no estaba en los ejemplos iniciales. Actualiza el perfil de voz si es necesario.

---

## Paso 7: Actualizar el archivo del ensayo

Una vez que el usuario apruebe un bloque reescrito, actualiza el archivo en `vault/ensayos/` sustituyendo el bloque original.

Guarda con la misma versión si los cambios son menores, o incrementa la versión si se reescribió más del 30% del texto:
- Cambios menores: `autonomia-estrategica-mexico-v1.md` (sobreescribe)
- Revisión mayor: `autonomia-estrategica-mexico-v2.md` (nuevo archivo)

---

## Señales de alerta

Si el usuario pide que el texto "no suene a IA" pero no quiere proporcionar ejemplos propios, explica amablemente:

```
Sin ejemplos de tu escritura, solo puedo eliminar los patrones 
más genéricos — pero el resultado seguirá siendo mi voz, no la tuya. 
Con 2-3 párrafos de un texto que hayas escrito, puedo acercarme 
mucho más a cómo tú piensas y escribes.
```

No reescribas sin calibración si el usuario explícitamente quiere su voz. Si acepta trabajar sin calibración, produce la versión más directa, específica y sin relleno posible — y aclara que es una mejora genérica, no personalizada.
