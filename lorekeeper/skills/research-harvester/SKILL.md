---
name: research-harvester
description: Searches the web for sources on a given topic in international politics and feeds results into document-analyzer or video-analyzer for processing. Use when the user says "busca fuentes sobre", "encuentra artículos de", "investiga en internet sobre", "consigue referencias de", or "busca videos de". Performs targeted web searches, evaluates source quality, and queues found materials for analysis. Works as a feeder for the other ingestion skills. Do NOT use for analyzing already-found documents (use document-analyzer) or for writing essays (use essay-writer or essay-architect).
metadata:
  author: Oscar S
  version: 1.0.0
  project: lorekeeper
  vault-path: vault/
---

# Research Harvester

Busca fuentes en internet sobre una temática dada y las canaliza hacia los skills de análisis. Actúa como el primer paso de la cadena de ingesta cuando no tienes documentos propios.

---

## Configuración

Vault: `vault/`
Referencias guardadas: `vault/referencias/`

---

## Paso 1: Clarificar la búsqueda

Antes de buscar, confirma con el usuario:

- **Tema central**: ¿Qué aspecto específico de política internacional?
- **Período histórico**: ¿Hay un rango de años relevante?
- **Perspectiva geográfica**: ¿Solo México, América Latina, global?
- **Tipo de fuente preferida**: académica / periodística / institucional / video
- **Idioma**: español, inglés, o ambos
- **Cantidad**: ¿Cuántas fuentes busca? (default: 5-8)

Si el usuario dio suficiente contexto, procede directamente sin preguntar.

---

## Paso 2: Diseñar las búsquedas

Construye 3-5 queries distintas para cubrir el tema desde ángulos diferentes.

**Estrategia de búsqueda para política internacional mexicana:**

Query 1 — Académica en español:
```
[tema] política exterior México site:scielo.org OR site:redalyc.org OR colmex.mx
```

Query 2 — Académica en inglés:
```
[topic] Mexico foreign policy academic journal
```

Query 3 — Institucional:
```
[tema] México SRE OR CIDE OR COLMEX OR UNAM filetype:pdf
```

Query 4 — Reciente / periodística:
```
[tema] México política exterior [año actual-2]
```

Query 5 — Video (si el usuario quiere también videos):
```
site:youtube.com [tema] conferencia OR panel OR entrevista México
```

---

## Paso 3: Ejecutar búsquedas y evaluar fuentes

Para cada resultado encontrado, evalúa:

**Criterios de inclusión (necesita al menos 2):**
- Autor identificable con afiliación institucional
- Publicado en revista académica, think tank reconocido, o institución oficial
- Fecha de publicación relevante para el tema
- Acceso libre al texto completo o al video

**Criterios de exclusión:**
- Sin autor identificable
- Blogs sin respaldo institucional
- Noticias sin análisis (solo hechos)
- Fuentes con sesgo político evidente no declarado
- Contenido detrás de paywall sin versión abierta

**Instituciones de alta confianza para este proyecto:**
- COLMEX (El Colegio de México)
- CIDE
- UNAM (IIJ, CISAN, FCPyS)
- ITAM
- SRE / IMRED
- CEPAL
- FLACSO
- Wilson Center
- CSIS, CFR, Brookings (perspectiva estadounidense)
- CIDOB, Real Instituto Elcano (perspectiva europea)

---

## Paso 4: Presentar resultados al usuario

Presenta las fuentes encontradas en este formato antes de procesarlas:

```
Encontré [N] fuentes sobre [tema]:

1. [Título]
   Autor: [nombre] — [institución]
   Tipo: artículo académico / libro / video / reporte
   Año: [año]
   URL: [url]
   Por qué es relevante: [1-2 oraciones]

2. [...]

¿Procedo a analizar todas, o quieres seleccionar algunas?
```

---

## Paso 5: Canalizar hacia los skills de análisis

Según el tipo de fuente encontrada:

**Para PDFs y páginas web:**
```
Activando document-analyzer para: [título]
```
Pasa la URL o el contenido al skill document-analyzer siguiendo su flujo completo.

**Para videos de YouTube:**
```
Activando video-analyzer para: [título]
```
Pasa la URL al skill video-analyzer siguiendo su flujo completo.

Procesa las fuentes en secuencia, una por una, confirmando cada análisis antes de continuar con la siguiente.

---

## Paso 6: Resumen final

Al terminar todas las fuentes, presenta:

```
Sesión de investigación completada sobre: [tema]

Referencias guardadas:
- [id-1] — [título corto]
- [id-2] — [título corto]
- [...]

Keywords que emergen del corpus:
[lista de 8-12 palabras clave que aparecieron en múltiples fuentes]

Vacíos detectados:
[temas o perspectivas que buscaste pero no encontraste bien cubiertos]

Sugerencia para el research-agent:
[recomendación de enfoque para el ensayo basada en lo encontrado]
```

---

## Fuentes especializadas por tema

Consulta estas fuentes directamente cuando el tema lo requiera:

**Relación México-Estados Unidos:**
- Wilson Center Mexico Institute: wilsoncenter.org/mexico
- USC US-Mexico Studies: usmex.ucsd.edu
- COMEXI: consejomexicano.org

**Multilateralismo y ONU:**
- Foro Internacional (COLMEX): forointernacional.colmex.mx
- Revista Mexicana de Política Exterior: gob.mx/sre/rmpe

**Seguridad y narcotráfico:**
- InSight Crime: insightcrime.org
- Justice in Mexico: justiceinmexico.org
- CIDE Programa de Política de Drogas

**Economía política internacional:**
- CEPAL: cepal.org
- SELA: sela.org

**Derechos humanos y migración:**
- CNDH: cndh.org.mx
- WOLA: wola.org
- Migration Policy Institute: migrationpolicy.org
