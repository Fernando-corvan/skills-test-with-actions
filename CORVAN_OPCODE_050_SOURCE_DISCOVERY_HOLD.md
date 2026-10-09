# CORVAN · selección aleatoria del opcode 50 · hallazgo forense

**Tipo:** `LAB_SOURCE_DISCOVERY_HOLD` / **NO es el cuerpo del opcode 50**.

**Pregunta madre:** ¿Puede un opcode elegido arbitrariamente extraerse de su Casa original y demostrar en GitHub las conductas de su propio contrato, sin inventar identidad, función ni autoridad cuando no aparece su fuente primaria?

## Lectura de Casa CORVAN

Se consultaron directamente en Google Drive la raíz física de Casa, el Master Index v1.2, el ledger 000–1000, el mapa de familia histórica 000–099, el mapa temprano 000–699 y el expediente de arqueología del tramo 000–099.

Búsquedas dirigidas: `50_C`, `50`, `0050`, `050_C`, `OPCODE_50`, `50_S`, `50_CORVAN`, `50_C_CORVAN`, `CORVAN_50`; además búsquedas en registros y carpetas históricas.

**Observado:** no se recuperó ningún documento cuyo ID/título y cuerpo primario identifiquen sin ambigüedad un **opcode autónomo 50**. En el tramo cercano sí aparecen cuerpos 40, 56 y 58, y referencias internas a módulos `M50` de otros opcodes. **Esas piezas no son el opcode 50**.

El registro histórico 000–099 advierte expresamente que las numeraciones bajas se reutilizaron por familias y que un resultado de búsqueda vacío **no demuestra un número libre ni inexistencia histórica**.

## Qué probamos y qué NO

El adaptador `src/corvan_opcode_source_discovery_gate.py` implementa **únicamente el preflight de identidad y evidencia**. La política es:

- No inferir función por número, banda, texto, `M50` ni por similitud con 40/56/58.
- Si no hay cuerpo exacto: `HOLD_SOURCE_NOT_LOCATED`.
- Si hay varias piezas tituladas 50: `HOLD_NUMERIC_COLLISION` y reconciliación L0/4103.
- Si hay título pero no lectura íntegra de cuerpo: `HOLD_PRIMARY_BODY`.
- Sin dueño, revisión y contrato: `HOLD_SOURCE_IDENTITY` o `HOLD_OWNER_OR_CONTRACT`.
- Incluso con un cuerpo validado: `READY_TO_DESIGN_FUNCTIONAL_TESTS`, **no** `RUNTIME_PASS`.

La batería `tests/test_opcode_050_source_discovery_gate.py` incluye números colindantes y `M50` falsos, fallos de esquema, colisión, título sin cuerpo y un caso sintético que alcanza solo preparación de pruebas.

**No inventar** `function_signature`, `expected_output`, `real_owner` ni adaptador funcional para el opcode 50. La prueba de comportamiento contractual real **no se ejecutó porque falta el cuerpo fuente**.

## Alcance de GitHub y protocolo

Repo de laboratorio: `Fernando-corvan/skills-test-with-actions`. Esta rama no sobrescribe `main`, no traslada ficheros privados de Drive, no instala opcodes y no edita órganos originales.

Validación prevista: Python package y Python Coverage de GitHub Actions; un CI verde demostraría que **el preflight** funciona como fue programado, **no** que el opcode 50 funciona.

El protocolo de integración sigue `corvan-agent-memory/protocols/lab_to_casa.md`; sin fuente primaria, el estado debe ser `HOLD` y no `ADMITTED`.

## Siguiente acción válida

Solicitar a L0 / 4103 la identidad y hogar exactos del cuerpo primario 50, incluyendo `document_id`, `revision`, nombre completo, dueño, contratos de entrada/salida, fallos esperados y evidencia de actualizaciones. Solo entonces extraer el ADN funcional **de ese cuerpo** y construir las pruebas de comportamiento y falsación. Ningún número se asigna ni se marca libre.

**RESULTADO DEL CASO:** `HOLD_SOURCE_NOT_LOCATED` / `FUNCTIONAL_TEST_NOT_RUN` / `NATIVE_RUNTIME_NOT_PROVEN`.
