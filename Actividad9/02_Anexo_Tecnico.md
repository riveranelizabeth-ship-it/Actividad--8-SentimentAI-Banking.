# Actividad 9 | Anexo técnico

## A. Demanda, capacidad y costos simulados

Mes de 720 h. La demanda normal es de 2 solicitudes/s durante 600 h y la demanda pico es de 12/s durante 120 h. Volumen ofrecido: (2 × 600 + 12 × 120) × 3,600 = 9,504,000 solicitudes. La capacidad útil se modela en 6/s por réplica estándar y 12/s para la instancia vertical. Se propusieron 4 vCPU y 8 GiB por réplica estándar y 8 vCPU y 16 GiB para la instancia vertical. Estos valores representan recursos asignados y capacidad supuesta.

| Concepto | Instancia única | Vertical | Horizontal |
| --- | ---: | ---: | ---: |
| Cómputo normal (USD) | 60.00 | 138.00 | 120.00 |
| Cómputo pico (USD) | 12.00 | 27.60 | 36.00 |
| Componentes compartidos (USD) | 20.00 | 20.00 | 40.00 |
| Total mensual (USD) | 92.00 | 185.60 | 196.00 |
| Solicitudes atendibles (millones) | 6.912 | 9.504 | 9.504 |
| Costo por 1,000 atendibles (USD) | 0.0133 | 0.0195 | 0.0206 |

Cómputo = instancias × horas × tarifa. Las tarifas supuestas son USD 0.10/h estándar y USD 0.23/h vertical. El componente compartido agrupa registro, almacenamiento y red interna. En horizontal incluye un presupuesto adicional para el balanceador. Solicitudes atendibles = suma de mínimo entre demanda y capacidad por intervalo × segundos. El cálculo supone estado estable y ausencia de cola persistente, reintentos y fallas. Costo unitario = costo total / solicitudes atendibles × 1,000. Las cifras modelan un techo de atención, sin acreditar latencia ni disponibilidad.

### Ahorro por ajustar las réplicas a la demanda

| Variante horizontal | Horas-réplica al mes | Cómputo (USD) | Compartidos (USD) | Total (USD) |
| --- | ---: | ---: | ---: | ---: |
| Tres réplicas fijas | 3 × 720 = 2,160 | 216 | 40 | 256 |
| Dos en horario normal y tres en pico | 2 × 600 + 3 × 120 = 1,560 | 156 | 40 | 196 |

El ajuste evita 600 horas-réplica al mes. El ahorro mensual es USD 60, equivalente a 60 / 256 = 23.4 %. Las dos variantes ofrecen 18 solicitudes/s útiles en el pico bajo los supuestos del caso. La comparación supone precalentamiento oportuno y excluye el costo adicional de arranque o de mantener réplicas extra frente a ráfagas imprevistas.

Si se requiere conservar 12/s al perder cualquier zona durante el pico, cuatro réplicas distribuidas 2 + 2 añaden USD 12 al mes bajo el mismo patrón. El costo total sería USD 208 y USD 0.0219 por 1,000 solicitudes atendibles. La cotización y el gasto real dependen del proveedor, región, tráfico, retención de logs y revisión humana.

## B. Desempeño y recursos

| Indicador | Línea base medida | Verificación del rediseño |
| --- | --- | --- |
| Latencia | p95 de 174.45 ms dentro del cuaderno, 300 solicitudes | Medición de extremo a extremo con reloj monotónico, discriminando red, cola e inferencia. |
| Servicio | 300/300 solicitudes correctas en ≤ 500 ms en Colab | SLO ≥ 95 % por escenario con demanda normal, pico y fallo inyectado. |
| Throughput | 8.23/s, proxy serial calculado como 300 / 36.46 s acumulados | Medir solicitudes completadas por segundo de reloj, concurrencia, rechazos y atraso de cola. |
| Uso de recursos | CPU en Colab, sin series de CPU ni RAM | Medir CPU, memoria residente, picos de memoria y tiempo de arranque por réplica. |
| Calidad | Recall negativo 95/100 y F1 macro 0.9767 | Comparar versiones en una muestra independiente y revisar calidad por tema. |

La carga normal representa 16.7 % de la capacidad útil horizontal y la carga pico 66.7 %. Son proporciones de demanda sobre capacidad supuesta, no porcentajes de utilización de CPU. Con una réplica perdida en pico, la relación sube al 100 % del límite útil supuesto. La prueba contempla 10 minutos de calentamiento y 30 por escenario, con una ráfaga al inicio del pico y caída de una réplica durante carga sostenida. Se reportan p50, p95, p99, éxitos, rechazos y uso de recursos. Cada respuesta fallida o tardía cuenta contra el presupuesto, incluidos los rechazos por capacidad.

## C. Fairness y sesgos por tema

Se cruzó el ID de cada solicitud de la Actividad 8 con el tema del conjunto sintético. Recall negativo = negativos detectados / negativos etiquetados. La tasa de omisión usa el mismo denominador.

| Tema | Negativos | Detectados | Omitidos | Recall |
| --- | ---: | ---: | ---: | ---: |
| Aclaraciones | 10 | 10 | 0 | 100 % |
| Aplicación móvil | 10 | 9 | 1 | 90 % |
| Atención al cliente | 10 | 10 | 0 | 100 % |
| Cajeros | 10 | 9 | 1 | 90 % |
| Comisiones | 10 | 9 | 1 | 90 % |
| Créditos | 10 | 10 | 0 | 100 % |
| Pagos de servicios | 10 | 9 | 1 | 90 % |
| Seguridad y acceso | 10 | 10 | 0 | 100 % |
| Tarjetas | 10 | 10 | 0 | 100 % |
| Transferencias | 10 | 9 | 1 | 90 % |
| Global | 100 | 95 | 5 | 95 % |

Se eligió el recall de negativos porque una omisión puede quitar prioridad a un comentario que requiere atención. Los cinco casos omitidos se identificaron para revisión de etiqueta, redacción y contexto. La causa de esas omisiones queda indeterminada con la evidencia disponible. Cualquier cambio de modelo o umbral se compara en una muestra independiente con la misma métrica.

La brecha observada entre temas fue de 10 puntos porcentuales. Con diez ejemplos por tema, un solo error cambia el recall en 10 puntos. La segmentación evalúa cobertura temática. La muestra carece de atributos y casos suficientes para inferir equidad demográfica. En el piloto se cotejan las etiquetas mediante revisión humana y se amplía el muestreo de los cinco temas con omisiones. Para decisiones por tema, se establece inicialmente un mínimo de 30 negativos por grupo y se revisa la incertidumbre junto con el tamaño de la brecha.

[Evidencia de solicitudes](../evidencias/linea_base/solicitudes.csv) · [Datos sintéticos](../data/SentimentAI_Banking_Dataset_300.csv)
