# Lorekeeper

Sistema de investigación y escritura de ensayos de política internacional mexicana.

## Contexto del proyecto

- **Autor:** Oscar S
- **Tema central:** Política exterior mexicana y relaciones internacionales
- **Vault de Obsidian:** `vault/` (referencias, ensayos, recursos)
- **Skills activos:** ver lista abajo

## Rutas clave

```
vault/referencias/   ← donde los skills guardan las notas de análisis
vault/ensayos/       ← borradores y versiones finales
vault/recursos/      ← notas propias y perfil de voz (style-humanizer)
skills/              ← fuente de verdad de los skills (instalados en ~/.claude/skills/)
```

## Skills disponibles y cuándo usarlos

| Skill | Cuándo usarlo |
|---|---|
| `/research-harvester` | Buscar fuentes en internet sobre un tema |
| `/document-analyzer` | Analizar un PDF o página web |
| `/video-analyzer` | Analizar un video de YouTube |
| `/research-agent` | Punto de entrada al pipeline: investigar un tema y proponer enfoques |
| `/essay-architect` | Diseñar la estructura del ensayo |
| `/essay-writer` | Redactar el borrador completo |
| `/style-humanizer` | Ajustar la voz y eliminar patrones genéricos |
| `/quality-checker` | Verificar citas y calidad final antes de publicar |

## Flujo de trabajo estándar

```
[research-harvester] → [document-analyzer / video-analyzer]
                                   ↓
                           vault/referencias/
                                   ↓
                       [research-agent] → propone enfoques
                                   ↓
                       [essay-architect] → diseña estructura
                                   ↓
                       [essay-writer] → redacta borrador
                                   ↓
                       [style-humanizer] → ajusta voz
                                   ↓
                       [quality-checker] → revisión final
                                   ↓
                           vault/ensayos/
```

## Dependencias del sistema

- Python con `playwright` instalado
- Chromium instalado vía `python -m playwright install chromium`
- Requerido solo para `video-analyzer`

## Convenciones

- Formato de citas: Chicago Author-Date
- IDs de referencias: `[apellido]-[año]-[primera-palabra]`
- IDs de videos: `[apellido]-[año]-[primera-palabra]-video`
- Versiones de ensayos: `[tema-kebab-case]-v1.md`, `-v2.md`, etc.
- Marco teórico de referencia: `skills/research-agent/references/theoretical-frameworks.md`
