"""Command-line entry point.

    python -m polarmed.cli run --source <pasta> --out <pasta>

Every threshold lives in ``config/default.yaml``; the flags here override
individual leaves of it and nothing else. The resolved cut is printed on every
run and recorded in ``run_manifest.json``, so a report can always be traced back
to the parameters that produced it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from polarmed import __version__
from polarmed.config import Config, load_config
from polarmed.logging_setup import get_logger, setup_logging
from polarmed.manifest import RunManifest

# Config keys whose absence deserves an explanation rather than a bare
# "field required" from the validator.
_KEY_EXPLANATIONS = {
    "primary_endpoint": (
        "O resultado principal tem de ser declarado ANTES de olhar para os "
        "dados (PLAN.md 4.7). Sem ele, qualquer achado e indistinguivel de "
        "uma pesca. Acrescente ao YAML:\n"
        "    primary_endpoint:\n"
        "      metric: RMSSD\n"
        "      contrast: rest_vs_mantra\n"
        "      direction: increase\n"
        '      declared_on: "AAAA-MM-DD"'
    ),
}


class ConfigurationError(RuntimeError):
    """Raised when the run cannot proceed as configured."""


def _format_validation_error(exc: ValidationError) -> str:
    """Turn a Pydantic traceback into something a tired operator can act on."""
    lines = ["ERRO DE CONFIGURACAO: o ficheiro YAML nao e valido.", ""]
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"]) or "(raiz)"
        lines.append(f"  - {location}: {error['msg']}")
        top_level = str(error["loc"][0]) if error["loc"] else ""
        explanation = _KEY_EXPLANATIONS.get(top_level)
        if explanation:
            lines.extend(f"    {line}" for line in explanation.splitlines())
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m polarmed.cli",
        description=(
            "Pipeline ECG/HRV para sessoes de meditacao em grupo com mantra."
        ),
    )
    parser.add_argument("--version", action="version", version=f"polarmed {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Corre o pipeline completo sobre uma pasta.")
    _add_common_arguments(run)
    _add_phase_arguments(run)
    run.add_argument(
        "--no-site", action="store_true", help="Nao gerar o site em docs/."
    )
    run.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolver e imprimir a configuracao, escrever o manifesto, e parar.",
    )

    inventory = sub.add_parser(
        "inventory", help="So descoberta e inventario, sem processamento."
    )
    _add_common_arguments(inventory)

    synth = sub.add_parser("synth", help="Gerar dados sinteticos de teste.")
    synth.add_argument("--out", required=True, type=Path)
    synth.add_argument("--bands", type=int, default=6)
    synth.add_argument("--sessions", type=int, default=3)
    synth.add_argument("--edge-cases", action="store_true")
    synth.add_argument("--seed", type=int, default=20260911)
    synth.add_argument("--verbose", action="store_true")

    return parser


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", required=True, type=Path, help="Pasta raiz dos dados.")
    parser.add_argument("--out", required=True, type=Path, help="Pasta de saida da corrida.")
    parser.add_argument("--config", type=Path, default=None, help="YAML alternativo.")
    parser.add_argument(
        "--session-grouping", choices=["folder", "time"], default=None
    )
    parser.add_argument(
        "--measurement-filter",
        default=None,
        help='Token no nome da pasta de medicao. "" desativa.',
    )
    parser.add_argument(
        "--session-types",
        default=None,
        help='Lista separada por virgulas do session_type aceite. "" desativa.',
    )
    parser.add_argument("--participants", type=Path, default=None)
    parser.add_argument("--session-map", type=Path, default=None)
    parser.add_argument(
        "--publish-mode", choices=["full", "aggregate", "anonymous"], default=None
    )
    parser.add_argument(
        "--i-know-what-im-doing",
        action="store_true",
        help="Permite --publish-mode full mesmo com um remote git publico.",
    )
    parser.add_argument("--verbose", action="store_true")


def _add_phase_arguments(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group(
        "recorte de fases",
        "Minutos desde o inicio de cada gravacao. A janela guard e o intervalo "
        "entre --rest-end e --mantra-start, e e sempre excluida das metricas.",
    )
    group.add_argument("--rest-start", type=float, default=None)
    group.add_argument("--rest-end", type=float, default=None)
    group.add_argument("--mantra-start", type=float, default=None)
    group.add_argument("--epoch-min", type=float, default=None)
    group.add_argument(
        "--align", choices=["recording_start", "group_start"], default=None
    )
    group.add_argument("--hrv-window", type=float, default=None)
    group.add_argument(
        "--exclude-threshold",
        type=float,
        default=None,
        help="pct_corrected acima do qual a gravacao sai dos agregados.",
    )


def collect_overrides(args: argparse.Namespace) -> dict[str, Any]:
    """Translate CLI flags into dotted config paths.

    ``--rest-end`` and ``--mantra-start`` also move the guard boundaries. The
    guard is *defined* as the interval between the two, so moving one edge
    without the other would leave a gap or an overlap in the timeline - which
    the config validator rejects outright.
    """
    overrides: dict[str, Any] = {}

    def put(path: str, value: Any) -> None:
        if value is not None:
            overrides[path] = value

    put("phases.rest.start_min", getattr(args, "rest_start", None))
    rest_end = getattr(args, "rest_end", None)
    if rest_end is not None:
        overrides["phases.rest.end_min"] = rest_end
        overrides["phases.guard.start_min"] = rest_end
    mantra_start = getattr(args, "mantra_start", None)
    if mantra_start is not None:
        overrides["phases.guard.end_min"] = mantra_start
        overrides["phases.mantra.start_min"] = mantra_start

    put("epochs.duration_min", getattr(args, "epoch_min", None))
    put("alignment.mode", getattr(args, "align", None))
    put("sliding.window_s", getattr(args, "hrv_window", None))
    put("rr.quality_warn_max_pct", getattr(args, "exclude_threshold", None))
    put("ingest.session_grouping", getattr(args, "session_grouping", None))
    put("report.publish_mode", getattr(args, "publish_mode", None))

    measurement_filter = getattr(args, "measurement_filter", None)
    if measurement_filter is not None:
        overrides["ingest.measurement_filter"] = measurement_filter

    session_types = getattr(args, "session_types", None)
    if session_types is not None:
        parsed = [s.strip() for s in session_types.split(",") if s.strip()]
        overrides["ingest.session_types_included"] = parsed

    return overrides


def check_primary_endpoint(config: Config) -> None:
    """Refuse to run without a declared primary endpoint (PLAN.md section 4.7).

    With this many metrics and this few participants, an undeclared result is
    indistinguishable from a fishing expedition. Pydantic already rejects a
    missing block; this adds the explicit, actionable message.
    """
    endpoint = config.primary_endpoint
    if not endpoint.metric or not endpoint.contrast:
        raise ConfigurationError(
            "primary_endpoint incompleto em config: 'metric' e 'contrast' sao "
            "obrigatorios. O resultado principal tem de ser declarado antes de "
            "olhar para os dados (PLAN.md 4.7)."
        )


def describe_config(config: Config, source: Path, out_dir: Path) -> str:
    """The resolved-config block printed at the top of every run."""
    endpoint = config.primary_endpoint
    lines = [
        "",
        "=" * 72,
        f"  polarmed {__version__}",
        "=" * 72,
        f"  fonte              : {source}",
        f"  saida              : {out_dir}",
        "",
        f"  RECORTE DE FASES   : {config.phase_summary()}",
        f"  epocas             : {config.epochs.duration_min:g} min "
        f"({', '.join(config.epochs.names)})",
        f"  alinhamento        : {config.alignment.mode}",
        "",
        f"  filtro session_type: {config.ingest.session_types_included or '(desativado)'}",
        f"  filtro pasta       : "
        f"{config.ingest.measurement_filter or '(desativado)'}",
        f"  agrupamento        : {config.ingest.session_grouping}",
        "",
        f"  ENDPOINT PRIMARIO  : {endpoint.metric} / {endpoint.contrast} / "
        f"{endpoint.direction} (declarado em {endpoint.declared_on})",
        "",
        f"  janela de Welch    : {config.spectral.window_s:g} s, "
        f"overlap {config.spectral.overlap:g}, nfft {config.spectral.nfft}"
        f"{'  [VLF desativada]' if not config.spectral.vlf_enabled else ''}",
        f"  HRV deslizante     : janela {config.sliding.window_s:g} s, "
        f"passo {config.sliding.step_s:g} s",
        f"  exclusao           : pct_corrected > "
        f"{config.rr.quality_warn_max_pct:g} %",
        "",
        f"  publish_mode       : {config.report.publish_mode}",
        f"  config sha256      : {config.content_hash()}",
        "=" * 72,
        "",
    ]
    return "\n".join(lines)


def command_run(args: argparse.Namespace) -> int:
    out_dir: Path = args.out
    logger = setup_logging(out_dir, verbose=args.verbose)

    config = load_config(args.config, collect_overrides(args))
    check_primary_endpoint(config)

    print(describe_config(config, args.source, out_dir))
    logger.info("recorte: %s", config.phase_summary())
    logger.info("config sha256: %s", config.content_hash())

    manifest = RunManifest(
        config=config,
        source=args.source,
        out_dir=out_dir,
        command=" ".join(sys.argv),
    )

    if not args.source.exists():
        # Not fatal during --dry-run: the point of a dry run is to check the cut.
        message = f"a pasta de origem nao existe: {args.source}"
        if args.dry_run:
            logger.warning("%s (ignorado em --dry-run)", message)
            manifest.add_warning(message)
        else:
            logger.error(message)
            manifest.add_warning(message)
            manifest.write()
            return 2

    if args.dry_run:
        path = manifest.write()
        logger.info("dry-run: manifesto escrito em %s", path)
        return 0

    manifest.write()
    logger.error(
        "A ingestao ainda nao esta implementada (Fase 2). "
        "Use --dry-run para validar o recorte."
    )
    return 3


def command_inventory(args: argparse.Namespace) -> int:
    setup_logging(args.out, verbose=args.verbose)
    get_logger().error("O inventario chega na Fase 2.")
    return 3


def command_synth(args: argparse.Namespace) -> int:
    setup_logging(None, verbose=args.verbose)
    get_logger().error("O gerador sintetico chega na Fase 2.")
    return 3


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handlers = {
        "run": command_run,
        "inventory": command_inventory,
        "synth": command_synth,
    }
    try:
        return handlers[args.command](args)
    except ConfigurationError as exc:
        print(f"ERRO DE CONFIGURACAO: {exc}", file=sys.stderr)
        return 2
    except ValidationError as exc:
        print(_format_validation_error(exc), file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"ERRO: ficheiro de configuracao nao encontrado: {exc}", file=sys.stderr)
        return 2
    except KeyError as exc:
        print(f"ERRO: flag desconhecida para a configuracao: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
