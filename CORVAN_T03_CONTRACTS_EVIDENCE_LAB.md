# T03 Contracts → COG02 — fuente real, preadmisión, bloqueo

Leídos y cotejados en Drive los cuerpos originales: 03 Message/Event Contract, 08 Failure/Retry Policy, registro funcional 701, L0 4200 y COG02. 03 y 08 viven en L_SHARED_CONTRACTS.

Las firmas de función descritas dentro de 03 incluyen ValidateMessageEvent y BuildEventPacket. Las de 08 incluyen Signature_ClassifyFailure y Signature_SelectRetryRoute. Son funciones originales candidatas para una ficha 701; no equivalen a firmas Q_OP/A_OP individualmente admitidas por 701.

Resultado de fuentes: 701 presenta una ficha general de Protocols, pero no fichas individuales 03 y 08 con revisión sellada. L0 no acredita interfaces invocables reales para estos contratos. La revisión actual de 03 difiere de la usada por el QA histórico.

Ensayo seguro: src/corvan_t03_source_admission.py aplica los bloqueos 701→L0 antes del COG02 v0.3. Su prueba test_t03_cog02_source_admission.py demuestra que una interfaz ficticia bien formada puede producir ROUTE_REQUEST_ONLY con el modelo base, mientras que el precontrol debe emitir HOLD_701_QOP_AOP_SIGNATURE. La prueba no invoca a 705 ni a órganos originales.

Para avanzar: que 701 valide las preguntas/respuestas operativas propias de 03/08 y que L0 certifique propiedad, revisión e interfaz. Luego repetir el experimento y registrar en Drive solo el resultado observado. No mover o reescribir opcodes por suposición.

ESTADO: T03 SOLO · PR DRAFT · LABORATORIO · SIN RUTA NATIVA · SIN NUEVO OPCODE.
