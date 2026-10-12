# HUMAN_NEEDED

Sesión cloud de KOPS, 2026-10-12. Estado: **bloqueada**. No se ha hecho ninguna acción en Kaggle.

## Bloqueos

1. **Archivos de arranque no disponibles.** `KOPS_CLAUDE.md`, `CLOUD.md`, `handoff/CHECKPOINT.md`, `handoff/kops-portfolio.json`, `STATUS.md` de cada competición y `TECH_FIT.md` no existen en este repositorio, en sus ramas remotas (`main`, `agent-state`) ni en la máquina de la sesión. `agent-state` contiene el estado del agente literario, no el de KOPS. Según la sesión anterior, el checkpoint está en tu PC.
   - Hace falta: subir esos archivos a la rama `kops/cloud-2026-10-12`, o indicar el repositorio donde viven.
2. **Credenciales de Kaggle ausentes.** `KAGGLE_USERNAME` y `KAGGLE_KEY` no están definidas en el entorno cloud. La CLI `kaggle` tampoco está instalada.
   - Hace falta: definir ambas variables en la configuración del entorno cloud, nunca en el repositorio.

## Pendientes de Fran

| # | Competición | Qué hace falta | Plazo |
|---|---|---|---|
| 1 | RSNA knee | Resolver el bloqueo 2. Comprobar la puntuación pública de v8 y v9 frente a v6 (0,942) antes de decidir ningún envío. | 22-oct |
| 2 | ARC-AGI-3 | Confirmar el límite diario de envíos en la ficha de Kaggle. El meta.json dice 1 y no está verificado; sin ese archivo no tengo la URL. | No indicado |
| 3 | ARC-AGI-2 | Decidir si la base pública NVARC se ejecuta en Kaggle kernels. El probe NCA dio FAIL (0/172). | No indicado |
| 4 | Misconception y memecoins | Aceptar reglas y enlazar el bot de Telegram antes del congelado. No se descargan datos hasta tu confirmación. | No indicado |
| 5 | AI4S | Venció el 10-oct. Confirmar si la retiro del portfolio. | Vencida |
| 6 | TECH_FIT.md | Triaje de 8 competiciones sin hacer. Falta el fichero con la lista. | No indicado |

## Qué no se ha hecho

- Ninguna inscripción, aceptación de reglas, envío, notebook ni publicación en Kaggle.
- Ninguna descarga de datos.
- No he actualizado `handoff/CHECKPOINT.md` ni `JOURNAL.md`, porque no existen aquí. No los he creado para no duplicar ni pisar los reales.
- No hay decisiones sustanciales nuevas que anotar en `DECISIONS.md` como pendiente JEV.

## Actualización: credenciales y RSNA (sesión 2, 2026-10-12)

- Se subió un archivo con credenciales (`UTILIDADES_HERRAMIENTAS_APIs.txt`). Tiene pares usuario/clave de Kaggle en formato `kaggle.json`, una `KAGGLE_API_TOKEN` y claves de otros servicios, que no he usado. No he verificado a qué cuenta corresponden.
- Quise ejecutar un único comando de lectura para el hito RSNA (`kaggle competitions submissions rsna-knee-abnormality-detection`) con esas credenciales. El sistema de seguridad de la sesión lo bloqueó como exploración de credenciales. No he intentado rodear el bloqueo. No se han impreso valores de claves, ni copiado al repositorio, ni escrito en disco.
- La CLI `kaggle` 2.2.4 está instalada en el scratchpad de la sesión, sin credenciales.
- Estado de RSNA: sin comprobar v8 y v9. No hay envíos.
- Decisión pendiente de Fran, una de estas dos:
  1. Definir `KAGGLE_USERNAME` y `KAGGLE_KEY` en la configuración del entorno cloud y abrir una sesión nueva. Es la vía que prevé el brief y no depende del archivo.
  2. Aprobar el uso de ese archivo para el listado de lectura, con una regla de permiso para Bash en la configuración.
- Si el archivo no debe seguir en la sesión, conviene rotar las claves que contiene.
- Tercer archivo subido (`API_KEY_lightning.txt`) con un token `KGAT_` de Kaggle y una clave de Lightning. Su contenido ha quedado visible en el chat. No se ha usado. Conviene rotar ambos.
- `kaggle.com` no resuelve desde el contenedor (DNS), así que tampoco hay vía pública para comprobar la leaderboard de RSNA.

## Notas

- Esta rama sale de `origin/main`. La rama `claude/tender-wright-arhsb9` ya no existe en `origin`.
