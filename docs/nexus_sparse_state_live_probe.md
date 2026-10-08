# Nexus SPARSE_STATE_PROBE — prueba operativa directa

Objetivo: probar el patrón sin convertirlo en un programa Python.

Regla aplicada:
- inspeccionar estado sólo en puntos relevantes;
- no hacer readback continuo después de cada acción;
- volver a inspeccionar ante cambio de fase, error, latencia inesperada o petición explícita.

Secuencia de esta misión:
1. petición explícita -> leer baseline de main;
2. crear rama;
3. escribir este documento;
4. abrir PR draft;
5. cambio a fase de verificación -> hacer un único readback final.

Criterio de éxito:
- la rama existe;
- este documento existe;
- la PR existe;
- main conserva el baseline inicial;
- no fue necesario inspeccionar el estado entre cada operación.

No se modifica código de aplicación ni tests.
