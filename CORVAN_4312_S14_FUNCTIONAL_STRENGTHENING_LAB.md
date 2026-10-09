# CORVAN · primera mejora funcional contrastada · Protocolos/4312

## Pregunta madre
¿Cómo impedir que un protocolo de hilo cognitivo dé por cerrado un retorno cuando solo existe una solicitud enviada, un ACK no comprobado, un duplicado, un salto de secuencia o una escritura WAL no duradera, sin usurpar la autoridad de Contracts, WAL, del propietario de retorno ni de QA?

## Evidencia primaria leída
- **03_CORVAN_MESSAGE_EVENT_CONTRACT** (`1v3tRTw01GClNpqC-v25j_HyFED1_FWMqFMRpR-sP6N8`) posee contrato de identidad de evento, correlación, causalidad, ACK, reintento e idempotencia.
- **11_CORVAN_CONTEXT_REANCHOR_WAL_SCAR_BRIDGE** (`14PIW3KoAJP4d1_l3M_tObuIY6G2YwaB4HwLR5F7n_zM`) conserva secuencia por misión y WAL durable/continuidad.
- **S14_STRING** (`1_seNG9BrdihwsQakx0BLCs1n8h6d_mC9GUNoQRDXEvc`), sintetiza `THREAD_EVENT_RETURN_INTEGRITY`, sin convertirse en propietario.
- **4312_S** (`1k5A_fQD14UlQhSk89762UaLQX-TXJOKWgnyQQ5w-28U`) ya porta `mission_id`, `assurance_thread_id`, `correlation_id`, `causation_id`, `wal_ref`, `return_owner`, `return_contract_ref` y un `SEMANTIC_RETURN_RECEIPT`; sus campos base no incluyen `event_seq`, `mission_revision`, `idempotency_key`, `durable_high_watermark` ni `expected_return_owner`. 

## Cambio propuesto, acotado
En lugar de duplicar los mecanismos de Contracts y WAL, añadir a 4312 un **interlock de comprobantes aportados por sus propietarios**: contexto misión/revisión, identidad de evento/hilo/correlación, secuencia monotónica cotejada contra la referencia anterior, owner esperado, no duplicado, contrato/ACK leído, retorno y WAL realmente commit/readback. Ante cualquier falta el protocolo conserva `HOLD_*` y no cierra el hilo; si los comprobantes aportados cuadran, solo devuelve `READY_FOR_NATIVE_OWNER_RECONCILIATION`, **no** `ACTIVE`, `NATIVE_PASS` ni `CANONICAL`.

El archivo `src/corvan_s14_return_integrity_guard.py` es un **surrogado ejecutable de laboratorio**. Las pruebas `tests/test_s14_return_integrity_4312_lab.py` inyectan fixtures controladas, incluidas mutaciones adversariales de los comprobantes. Su verificación no autentica que los registros correspondan a un WAL real, ni prueba a 4312 original.

## Límites de autoridad
`03_CONTRACTS` valida eventos y duplicados. `WAL/Observability` certifica commit y high-watermark. El owner original certifica retorno/ACK. `4312_S` preserva y coteja referencias; `4310_AS` juzga invariantes semánticos; `4313_QA` certifica la composición. **Ninguno transfiere su función al protocolo.**

## Condición para llevar a Casa
Primero CI en GitHub sobre commit fijado. Después anexo `ADD_ONLY` en cuerpo original de 4312 como `PROPOSED_NOT_ACTIVE`, con esquema, failure modes, prueba y límites. Luego QA de readback del cuerpo original y evidencia de ejecución real de owners para certificar operación. PR permanece `draft` y sin fusionar.
