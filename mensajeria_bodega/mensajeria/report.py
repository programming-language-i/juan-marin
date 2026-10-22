import argparse  # noqa: I001
import json
import re

from collections import Counter
from pathlib import Path
from typing import Any, Iterator  # noqa: UP035


STOPWORDS = {
    "para", "como", "pero", "esta", "este", "desde",
    "hasta", "donde", "cuando", "que", "con", "por",
    "una", "uno", "unos", "unas", "los", "las", "del",
    "de", "la", "el", "en", "y", "o", "a", "un", "se",
    "su", "es", "fue", "son", "han", "hay", "al",
}


def read_records(
    path: Path
) -> Iterator[dict[str, Any]]:
    """Lee mensajes válidos de la bitácora secuencialmente."""
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                item = json.loads(line)

                if (
                    isinstance(item, dict)
                    and item.get("type") == "message"
                ):
                    yield item

            except json.JSONDecodeError:
                # Una línea dañada no detiene el reporte.
                continue


def build_report(
    path: Path,
    top_words: int = 15,
) -> dict[str, Any]:
    """Calcula estadísticas sin guardar todos los mensajes."""
    by_sender: Counter[str] = Counter()
    by_hour: Counter[str] = Counter()
    words: Counter[str] = Counter()

    total = 0

    for item in read_records(path):
        total += 1

        sender = item.get("sender")
        timestamp = item.get("timestamp")
        content = item.get("text")

        if isinstance(sender, str):
            by_sender[sender] += 1

        if isinstance(timestamp, str):
            match = re.match(
                r"^\d{4}-\d{2}-\d{2}T(\d{2}):",
                timestamp,
            )

            if match:
                by_hour[match.group(1)] += 1

        if isinstance(content, str):
            tokens = re.findall(
                r"[^\W_]+",
                content.casefold(),
                flags=re.UNICODE,
            )

            for word in tokens:
                if (
                    len(word) > 2
                    and word not in STOPWORDS
                    and not word.isdigit()
                ):
                    words[word] += 1

    hourly_counts = [
        (f"{hour:02d}:00", by_hour[f"{hour:02d}"])
        for hour in range(24)
    ]

    return {
        "total_mensajes": total,
        "mensajes_por_usuario": by_sender.most_common(),
        "mensajes_por_hora": hourly_counts,
        "palabras_frecuentes": words.most_common(
            max(0, top_words)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reporte de operación de la bitácora"
    )

    parser.add_argument(
        "bitacora",
        nargs="?",
        default="bitacora.jsonl",
        help="Ruta del archivo JSONL",
    )

    parser.add_argument(
        "--top",
        type=int,
        default=15,
        help="Cantidad de palabras frecuentes",
    )

    args = parser.parse_args()

    try:
        report = build_report(
            Path(args.bitacora),
            args.top,
        )

        print(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
            )
        )

    except OSError as error:
        print(f"No se pudo leer la bitácora: {error}")


if __name__ == "__main__":
    main()