# Actividad 9 | Reporte técnico

## 1. Análisis y rediseño de escalabilidad

SentimentAI Banking usa XLM-RoBERTa para clasificar comentarios en positivo, neutral o negativo. Su finalidad es apoyar la priorización humana de comentarios, incluidas señales de insatisfacción. El ejercicio reutiliza la línea base de la Actividad 8 y toma como referencia una arquitectura de nube simulada con una API y una sola instancia de inferencia. La instancia comparte el límite de capacidad y el riesgo de indisponibilidad con la API del escenario. A mayor concurrencia, la espera en cola puede elevar la latencia aunque la inferencia individual permanezca estable.

En Colab con CPU se invocó el modelo para 300 comentarios sintéticos. El p95 fue de 174.45 ms y el recall de negativos fue del 95 %. Esa medición se hizo dentro del cuaderno. En la nube, el tiempo observado por el cliente incluye red, validación, espera en cola e inferencia. El [anexo](02_Anexo_Tecnico.md) cuantifica la capacidad supuesta y presenta el protocolo para medir el tiempo de extremo a extremo.

| Alternativa | Capacidad útil supuesta | Disponibilidad y desempeño |
| --- | --- | --- |
| Instancia única | 6 solicitudes/s | Cubre la demanda normal de 2/s. A 12/s, sin cola persistente, se rechaza la demanda que excede la capacidad. |
| Escalamiento vertical | 12 solicitudes/s | Duplica la capacidad útil mediante una instancia mayor. Cubre el pico nominal y conserva un punto único de falla. El cambio de tamaño requiere una transición controlada. |
| Escalamiento horizontal | 12/s con dos réplicas y 18/s con tres | Distribuye carga y permite reemplazar réplicas. Con tres réplicas, perder una deja 12/s. La pérdida de una zona puede retirar dos réplicas y requiere capacidad adicional o degradación controlada. |

El [diagrama](03_Diagrama_Arquitectura.pdf) muestra el rediseño: API privada con validación y minimización, balanceador con comprobaciones de salud y réplicas sin estado en dos zonas. Cada réplica precarga la misma versión del modelo y recibe tráfico tras pasar su comprobación de disponibilidad. La telemetría agrega tiempos de espera, errores, duración total y versión del modelo mediante un identificador de traza. La revisión humana conserva un canal independiente para quejas y casos ambiguos.

El piloto mantiene dos réplicas y precalienta una tercera antes del pico programado. Ante demanda imprevista, la política inicial escala si se superan 8 solicitudes/s durante dos minutos o aumenta sostenidamente la espera en cola. Se limita a cuatro réplicas presupuestadas y reduce capacidad con diez minutos de carga estable. Los umbrales son parámetros del caso y se validan con ráfagas y pérdida de réplicas. Si la disponibilidad ante pérdida de una zona es condición de salida, se prueban cuatro réplicas en pico, dos por zona, y se incorpora su costo al presupuesto.

Para optimizar inferencia, primero se evita recargar pesos por solicitud y se mide el paralelismo efectivo por réplica. Los microlotes y la cuantización se evalúan en pruebas independientes con límites de espera y criterios de calidad. La capacidad económica del anexo mantiene el modelo de referencia y excluye ahorros por optimizaciones aún sin medir.

## 2. Optimización de costos y FinOps

El SLO propuesto mantiene el criterio de la Actividad 8 como objetivo interno de piloto: al menos 95 % de solicitudes válidas completadas correctamente en 500 ms de extremo a extremo, por escenario normal, pico y fallo de una réplica. Errores, rechazos válidos y vencimientos consumen el presupuesto del 5 %. El SLA contractual, si procede, queda sujeto a la validación operativa y comercial. La calidad se mide por separado con ejemplos etiquetados.

La instancia única cuesta USD 92 en el mes simulado, pero su límite de capacidad solo le permite atender como máximo el 72.73 % de la demanda total con el patrón definido. Una instancia mayor cuesta USD 185.60. Las réplicas cuestan USD 196 y aportan capacidad de recuperación frente a la pérdida de una réplica. El diferencial de USD 10.40 mensuales se justifica para el piloto si la prueba de fallo y los objetivos de calidad se cumplen. El anexo separa capacidad teórica y SLO observado. Las tarifas son hipotéticas y los costos excluyen revisión humana, impuestos y egreso extraordinario.

Con enfoque FinOps, el responsable técnico etiqueta costos por entorno y versión. Producto y FinOps revisan semanalmente costo por 1,000 solicitudes completas, tráfico, utilización, rechazos y gasto de telemetría. El costo unitario se acompaña de la tasa de cumplimiento para que un aparente ahorro por rechazar solicitudes sea visible. Un aumento de 20 % sobre el costo unitario presupuestado abre revisión de demanda, recursos y retención de logs antes de modificar capacidad. La referencia metodológica es [FinOps Foundation, Unit Economics](https://www.finops.org/framework/capabilities/unit-economics/).

## 3. Auditoría de gobernanza, ética y cumplimiento

| Dimensión | Hallazgo y riesgo | Control y evidencia |
| --- | --- | --- |
| Ética y sesgos | Se omitieron cinco comentarios negativos en cinco temas. Si el resultado ordena la revisión, una queja puede perder prioridad. | Mantener el canal formal de quejas, habilitar revisión humana, muestrear negativos y falsos negativos por tema. Registrar discrepancias y correcciones. |
| Técnica | La línea base usa 300 textos sintéticos. Cambios de entrada o de versión pueden degradar el recall con latencia normal. | Evaluar por tema, formar un conjunto independiente, comparar versiones y registrar hash, versión, despliegue e intervención. Aplicar rollback tras una degradación confirmada. |
| Privacidad y legal | Un comentario real puede identificar a una persona o incluir datos de una operación. Un proveedor de nube y sus subprocesadores amplían el perímetro. | Inventariar tratamientos, validar finalidad y aviso, limitar texto y retención, cifrar y restringir accesos. Revisar con Jurídico la relación con proveedor, subprocesadores, ubicación y transferencias cuando apliquen. Documentar el encuadre sectorial antes de recibir datos reales. |
| Trazabilidad | La predicción pierde valor para auditoría si se desconoce la versión o si se registra texto innecesario. | Registrar ID de traza, modelo, fecha, tiempos, resultado y decisión humana vinculada cuando exista. Mantener el texto fuera de logs operativos y conservar bitácoras con acceso limitado. |

La revisión se organiza conforme a [NIST AI RMF 1.0](https://nvlpubs.nist.gov/nistpubs/AI/NIST.AI.100-1.pdf): Gobernar asigna responsables, Mapear delimita el caso de uso, Medir incorpora rendimiento y disparidades, y Gestionar define mitigación y reversión. La revisión jurídica toma como referencia la [LFPDPPP](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf), en particular los principios de su artículo 5. Los controles se proponen para un despliegue futuro con datos reales. El ejercicio con datos sintéticos permite revisar el diseño y deja la validación jurídica y técnica del servicio real como condición de autorización.

## 4. Plan de escalamiento responsable

| Fase | Responsable | Criterio para avanzar |
| --- | --- | --- |
| Pruebas en entorno aislado | Plataforma y MLOps | Medir latencia, recursos y SLO en carga normal, pico y pérdida de una réplica. Comprobar recuperación y trazabilidad. |
| Evaluación en sombra | Producto, Calidad y Privacidad | Validar controles de datos, etiquetar una muestra independiente y comprobar recall negativo global ≥ 90 %. Las predicciones se comparan con la revisión humana. |
| Piloto con 5 % y después 25 % del tráfico elegible | Producto y Operaciones | Cumplir el SLO, mantener recall global ≥ 90 %, revisar cualquier brecha por tema mayor a 10 puntos con muestra suficiente y comprobar costo unitario dentro de 120 % del plan. |
| Ampliación y seguimiento | Producto, MLOps, FinOps y Jurídico | Documentar aceptación de riesgos, prueba de fallo y capacidad de revisión. Revisar calidad semanalmente y costo por versión. |

Ante dos ventanas consecutivas fuera del SLO, Operaciones detiene el aumento de tráfico y aplica el runbook correspondiente. Si el recall cae por debajo del umbral sobre muestra suficiente, MLOps restaura la última versión aprobada y verifica la recuperación. Ante un incidente de privacidad, se corta el ingreso afectado y se activa el protocolo correspondiente. La detección de drift abre una revisión de calidad antes de decidir un reentrenamiento.

## Conclusión

El escalamiento horizontal se justifica por el margen de capacidad y la tolerancia a la pérdida de una réplica. El costo incremental se evalúa junto con las solicitudes atendidas y el control de calidad. En la Actividad 8, la degradación simulada mantuvo la latencia dentro del objetivo mientras el recall negativo cayó del 95 % al 50 %. Por eso, el plan exige comprobar calidad y nivel de servicio antes de aumentar tráfico.
