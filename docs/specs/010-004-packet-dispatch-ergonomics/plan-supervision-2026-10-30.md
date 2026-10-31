# Corrección de supervisión — plan de implementación

El requisito de plan multicomponente debió detectarse antes de presentar la spec para aprobación. La omisión es de supervisión, no una nueva decisión funcional que deba resolver Pablo. Se prepara un encargo read-only a architect para un plan mínimo del contrato ya aprobado, sin nueva Discovery ni modificación de spec. Tras materialización fiel se requiere revisión independiente y aprobación separada del plan; ninguna de ellas se presume.

El marcador de aprobación añadido a la spec conserva como prefijo exacto los 48282 bytes revisados (`054d4657b5dae096114a9e41beaad3c356234fe8fd5c60236752c24c89212008`). El pin aprobado actual es `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`. El checkpoint anterior conserva legítimamente el digest anterior y resume lo rechazó por drift contractual; se registra un nuevo checkpoint vinculado por la aprobación explícita, sin reescribir historia ni reanchor legacy.

N-4/N-5/N-6 continúan opcionales abiertos/postergados; el plan no los convierte en requisitos. No se ejecutan tests, implementación, dispatch ni begin en esta preparación.
