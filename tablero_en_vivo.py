"""Actualiza un tablero en consola al procesar cada ventana simulada."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from simular_incidentes import simulate, verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("solicitudes", type=Path)
    parser.add_argument("registro", type=Path)
    args = parser.parse_args()
    with args.solicitudes.open(newline="", encoding="utf-8-sig") as source:
        requests = list(csv.DictReader(source))

    with args.registro.open("w", encoding="utf-8") as log:
        def publish(metrics, event):
            now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            entry = {"timestamp_utc": now, **metrics, "evento": event}
            log.write(json.dumps(entry, ensure_ascii=False) + "\n")
            log.flush()
            status = event["accion"] if event else metrics["perfil"]
            print(
                f"{now} | {metrics['incidente']} {metrics['ventana']}/7 | "
                f"p95 {metrics['p95_ms']:.2f} ms | SLO {metrics['cumplimiento_slo']:.0%} | "
                f"presupuesto {metrics['consumo_presupuesto']:.0%} | "
                f"recall {metrics['recall_negativo']:.0%} | {status}", flush=True
            )
            time.sleep(0.25)

        windows, events = simulate(requests, on_window=publish)
    verify(windows, events)


if __name__ == "__main__":
    main()
