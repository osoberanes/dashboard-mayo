---
name: quality-checker
description: Verifies citations, performs fact-checking, and reviews writing quality of the essay draft. Use when the user says "verifica las citas", "revisa el ensayo", "haz fact checking", "checa las referencias", "revisa el estilo general", or when the essay is ready for final review before submission. Produces two outputs: a citations report and a writing quality report with specific suggestions. Do NOT rewrite text (use style-humanizer) or generate new content (use essay-writer).
metadata:
  author: Oscar S
  version: 1.0.0
  project: lorekeeper
  vault-path: vault/
---

# Quality Checker

Revisión final del ensayo en dos dimensiones: verificación de citas y fact-checking, y revisión de calidad de escritura. Produce un reporte con observaciones específicas y accionables.

---

## Configuración

Vault: `vault/`
Ensayos: `vault/ensayos/`
Referencias: `vault/referencias/`

---

## Paso 1: Cargar el ensayo

Lee el archivo del ensayo indicado en `vault/ensayos/`. Si el usuario no especifica cuál, lista los disponibles y pregunta.

---

## Módulo A: Verificación de citas y fact-checking

### A1: Auditoría de citas

Para cada cita en el texto (formato Chicago Author-Date):

1. Busca el archivo correspondiente en `vault/referencias/[ID].md`
2. Verifica:
   - **Autor**: ¿El apellido y año coinciden con el archivo de referencia?
   - **Página**: Si se cita una página específica, ¿es razonable dado el tipo de fuente?
   - **Cita textual**: Si es cita directa, ¿coincide con lo registrado en el vault?
   - **Atribución de ideas**: ¿La idea atribuida al autor realmente corresponde a su posición registrada?

3. Para referencias no encontradas en el vault:
   - Marca como `[VERIFICAR — no está en vault]`
   - Realiza búsqueda web para confirmar que el autor, título y año existen
   - Señala si no puedes confirmar la existencia de la fuente

**Reporte de citas:**

```
## Reporte de Citas

Total de citas en el ensayo: [N]
Verificadas contra vault: [N]
No encontradas en vault: [N]
Inconsistencias detectadas: [N]

### Inconsistencias:

[Cita en el texto]: (González González 1992, 45)
Problema: En el vault, el archivo gonzalez-1992-politica.md no registra 
          esta posición en la página indicada
Recomendación: Verificar número de página

[...]

### No verificables:
[Lista de citas que no están en vault y no pudieron confirmarse]
```

### A2: Fact-checking de afirmaciones empíricas

Identifica afirmaciones de hecho que no tienen cita asignada o que son verificables:

**Tipos de afirmaciones a verificar:**
- Datos numéricos (porcentajes, cifras, estadísticas)
- Fechas de eventos, tratados, decisiones
- Nombres de cargos y funcionarios en contexto histórico
- Atribución de políticas a gobiernos o períodos específicos
- Afirmaciones sobre posiciones de organismos internacionales

Para cada una:
1. Busca en el vault si alguna referencia la respalda
2. Si no, realiza búsqueda web para verificar
3. Marca el resultado: ✓ Verificado / ⚠ Matizar / ✗ Incorrecto / ? No pude verificar

**Reporte de fact-checking:**

```
## Fact-Checking

### Verificadas ✓
- "México ingresó al GATT en 1986" — confirmado

### Requieren matiz ⚠
- "La doctrina Estrada fue adoptada universalmente en América Latina"
  Matiz: Fue influyente pero no todos los países la adoptaron formalmente

### Incorrectas ✗
- "El Grupo de Contadora se formó en 1985"
  Correcto: Se formó en enero de 1983

### No pude verificar ?
- [lista]
```

---

## Módulo B: Revisión de calidad de escritura

### B1: Revisión estructural

Evalúa:

- **Coherencia de la tesis**: ¿La tesis anunciada en la introducción se defiende efectivamente en el cuerpo?
- **Progresión del argumento**: ¿Las secciones se construyen una sobre otra o son independientes?
- **Proporcionalidad**: ¿Hay secciones desproporcionadamente largas o cortas respecto a su peso en el argumento?
- **Conclusión**: ¿Cierra el argumento o solo resume?
- **Párrafos huérfanos**: ¿Hay párrafos que no conectan con la tesis?

### B2: Revisión de estilo

Identifica:

**Problemas de claridad:**
- Oraciones de más de 50 palabras sin coma que las articule
- Pronombres ambiguos ("esto", "ello", "lo cual") sin referente claro
- Términos técnicos sin definición la primera vez que aparecen
- Cambios de terminología para el mismo concepto (confunde al lector)

**Problemas de coherencia:**
- Argumentos contradictorios entre secciones
- Afirmaciones que se hacen y luego se desmienten sin reconocerlo
- Cambios de tiempo verbal sin justificación

**Residuos de escritura genérica** (que style-humanizer no alcanzó):
- Frases formulaicas que subsistieron
- Generalizaciones sin respaldo
- Énfasis retórico sin sustancia

### B3: Consistencia formal

Verifica:
- Formato de citas consistente en todo el texto (Chicago Author-Date)
- Lista de referencias completa y en orden alfabético
- Nombres propios escritos consistentemente
- Números: ¿en letra o en cifra? Debe ser consistente
- Uso de cursivas para términos extranjeros y títulos de obras

---

## Paso 2: Presentar el reporte completo

```
# Reporte de Quality Checker
Ensayo: [nombre del archivo]
Fecha: [fecha]
Palabras revisadas: [N]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MÓDULO A: CITAS Y FACT-CHECKING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Reporte de citas]
[Reporte de fact-checking]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MÓDULO B: CALIDAD DE ESCRITURA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Revisión estructural]
[Revisión de estilo]
[Consistencia formal]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESUMEN EJECUTIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Problemas críticos (deben resolverse antes de publicar):
1. [...]

Problemas menores (recomendables pero no bloqueantes):
1. [...]

El ensayo está listo para publicar una vez resueltos los problemas críticos.
```

---

## Paso 3: Asistir en las correcciones

Para cada problema reportado, el usuario puede pedir ayuda para resolverlo:

- **Cita incorrecta**: ayuda a reformularla con los datos correctos
- **Hecho erróneo**: propone la corrección con la fuente verificada
- **Problema de estilo**: sugiere una reescritura del párrafo específico
- **Problema estructural**: propone cómo reorganizar o expandir la sección

No reescribe bloques grandes de texto — para eso el usuario usa style-humanizer. Este skill señala y propone correcciones puntuales.

---

## Paso 4: Guardar versión revisada

Si se realizaron correcciones, guarda el ensayo como nueva versión:
`[nombre]-v[N+1].md`

Actualiza el frontmatter con:
```yaml
estado: revisado
fecha-revision: [fecha]
checklist-completo: true
```
