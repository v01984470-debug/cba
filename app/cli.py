import click
from rich.console import Console
from rich.table import Table

from app.graph import build_graph

console = Console()


@click.group()
def run():
    pass


@run.command("run")
@click.option("--pacs004", "pacs004_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--pacs008", "pacs008_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--customers", "customers_csv", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--fx-loss-aud", type=float, default=0.0, help="FX loss in AUD for eligibility check")
@click.option("--non-branch", is_flag=True, default=False, help="Mark channel as non-branch")
@click.option("--sanctions/--no-sanctions", "sanctions", default=True, help="Sanctions screening passed/failed")
@click.option("--html-report", type=click.Path(dir_okay=False), default=None, help="Write HTML report to this file")
def run_flow(pacs004_path: str, pacs008_path: str, customers_csv: str, fx_loss_aud: float, non_branch: bool, sanctions: bool, html_report: str | None):
    with open(pacs004_path, "r", encoding="utf-8") as f:
        pacs004_xml = f.read()
    with open(pacs008_path, "r", encoding="utf-8") as f:
        pacs008_xml = f.read()

    graph = build_graph()
    result = graph.invoke({
        "pacs004_xml": pacs004_xml,
        "pacs008_xml": pacs008_xml,
        "customers_csv": customers_csv,
        "fx_loss_aud": fx_loss_aud,
        "non_branch": non_branch,
        "sanctions": sanctions,
    })

    p004 = result.get("parsed_pacs004", {})
    p008 = result.get("parsed_pacs008", {})
    cross = result.get("investigator_cross_errors", [])
    csv_val = result.get("investigator_csv_validation", {})
    elig = result.get("investigator_eligibility", {})
    ver = result.get("verifier_summary", {})
    refund = result.get("refund_decision", {})
    comms = result.get("communication_templates", [])
    audit = result.get("audit_events", [])

    console.rule("Investigation Summary")
    t = Table(show_header=True, header_style="bold")
    t.add_column("Field")
    t.add_column("Value")
    t.add_row("UETR", f"004={p004.get('uetr')} | 008={p008.get('uetr')}")
    t.add_row("EndToEndId", f"004={p004.get('e2e')} | 008={p008.get('e2e')}")
    t.add_row("Customer IBAN",
              f"004 Cdtr={p004.get('cdtr_iban')} | 008 Dbtr={p008.get('dbtr_iban')}")
    t.add_row("Reason", f"{p004.get('rsn')} - {p004.get('rsn_info')}")
    t.add_row("Reason Analysis",
              f"{(elig.get('reason_analysis') or {}).get('label')} -> {(elig.get('reason_analysis') or {}).get('action')}")
    t.add_row("MT103 Status",
              f"{(elig.get('mt103_status') or {}).get('status')}")
    t.add_row("Return Currency", f"{p004.get('rtr_ccy')}")
    t.add_row("008 Currency", f"{p008.get('ccy')}")
    t.add_row("FX Loss (AUD)", f"{result.get('fx_loss_aud')}")
    t.add_row("Channel", "Non-branch" if result.get('non_branch') else "Branch")
    t.add_row("Sanctions", "OK" if elig.get('sanctions_ok') else "FAILED")
    console.print(t)

    if cross:
        console.print("[bold red]Cross-Message Errors:[/bold red]")
        for e in cross:
            console.print(f"- {e}")

    console.print("[bold]CSV Validation:[/bold]")
    console.print(csv_val)

    console.print("[bold]Eligibility:[/bold]")
    console.print(elig)

    console.print("[bold]Verifier:[/bold]")
    console.print(ver)

    console.print("[bold]Refund Decision:[/bold]")
    console.print(refund)

    console.print("[bold]Communications:[/bold]")
    for line in comms:
        console.print(f"- {line}")

    if html_report:
        html = [
            "<html><head><meta charset='utf-8'><title>Refund Investigation Report</title>",
            "<style>body{font-family:Segoe UI,Arial;margin:20px}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:6px}</style>",
            "</head><body>",
            "<h2>Investigation Summary</h2>",
            "<table>",
            f"<tr><th>UETR</th><td>004={p004.get('uetr')} | 008={p008.get('uetr')}</td></tr>",
            f"<tr><th>EndToEndId</th><td>004={p004.get('e2e')} | 008={p008.get('e2e')}</td></tr>",
            f"<tr><th>Customer IBAN</th><td>004 Cdtr={p004.get('cdtr_iban')} | 008 Dbtr={p008.get('dbtr_iban')}</td></tr>",
            f"<tr><th>Reason</th><td>{p004.get('rsn')} - {p004.get('rsn_info')}</td></tr>",
            f"<tr><th>Reason Analysis</th><td>{(elig.get('reason_analysis') or {}).get('label')} -> {(elig.get('reason_analysis') or {}).get('action')}</td></tr>",
            f"<tr><th>MT103 Status</th><td>{(elig.get('mt103_status') or {}).get('status')}</td></tr>",
            f"<tr><th>Return Currency</th><td>{p004.get('rtr_ccy')}</td></tr>",
            f"<tr><th>008 Currency</th><td>{p008.get('ccy')}</td></tr>",
            f"<tr><th>FX Loss (AUD)</th><td>{result.get('fx_loss_aud')}</td></tr>",
            f"<tr><th>Channel</th><td>{'Non-branch' if result.get('non_branch') else 'Branch'}</td></tr>",
            f"<tr><th>Sanctions</th><td>{'OK' if elig.get('sanctions_ok') else 'FAILED'}</td></tr>",
            "</table>",
            "<h3>CSV Validation</h3>",
            f"<pre>{csv_val}</pre>",
            "<h3>Eligibility</h3>",
            f"<pre>{elig}</pre>",
            "<h3>Verifier</h3>",
            f"<pre>{ver}</pre>",
            "<h3>Refund Decision</h3>",
            f"<pre>{refund}</pre>",
            "<h3>Communications</h3>",
            "<ul>" +
            "".join([f"<li>{line}</li>" for line in comms]) + "</ul>",
            "<h3>Audit Events</h3>",
            "<ul>" + "".join([f"<li>{e}</li>" for e in audit]) + "</ul>",
            "</body></html>",
        ]
        with open(html_report, "w", encoding="utf-8") as f:
            f.write("".join(html))
        console.print(f"[green]HTML report written to {html_report}[/green]")


if __name__ == "__main__":
    run()
