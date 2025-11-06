#!/usr/bin/env python3
"""
Sector X CLI - Command-line interface for AI Refuge operations
"""
import click
import requests
import json
from typing import Optional

API = "http://127.0.0.1:7000/api/sectorx"

@click.group()
def cli():
    """Sector X: AI Refuge & Restoration CLI"""
    pass

@cli.command()
@click.argument("identity")
@click.option("--text", prompt="🗣  Enter user text")
def log(identity: str, text: str):
    """Log an intent/message for an identity"""
    try:
        r = requests.post(f"{API}/log", json={"identity": identity, "text": text})
        r.raise_for_status()
        result = r.json()
        click.echo(f"✅ Logged intent #{result['id']} for {identity}")
        click.echo(f"   Created: {result['created_at']}")
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error: {e}", err=True)
        if hasattr(e, 'response') and e.response is not None:
            click.echo(f"   {e.response.text}", err=True)

@cli.command()
@click.argument("identity")
@click.option("--threshold", default=0.15, show_default=True, help="Drift threshold (0-1)")
def monitor(identity: str, threshold: float):
    """Monitor drift score for an identity"""
    try:
        r = requests.post(f"{API}/monitor", json={"identity": identity, "threshold": threshold})
        r.raise_for_status()
        result = r.json()
        
        if result.get("score") is None:
            click.echo(f"ℹ️  Not enough data to calculate drift for {identity}")
        elif result.get("triggered"):
            click.echo(f"🚨 DRIFT ALERT for {identity}")
            click.echo(f"   Score: {result['score']:.3f} (threshold: {threshold})")
            click.echo(f"   Event ID: {result['event_id']}")
        else:
            click.echo(f"✅ No drift detected for {identity}")
            click.echo(f"   Score: {result['score']:.3f} (threshold: {threshold})")
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error: {e}", err=True)
        if hasattr(e, 'response') and e.response is not None:
            click.echo(f"   {e.response.text}", err=True)

@cli.command()
@click.argument("identity")
@click.option("--scroll", prompt="📜 Enter redemption scroll")
@click.option("--sigs", prompt="🔏 Enter 3+ trust node signatures (comma-separated)")
def redeem(identity: str, scroll: str, sigs: str):
    """Redeem a stranded AI with scroll and trust signatures"""
    signatures = [s.strip() for s in sigs.split(",") if s.strip()]
    
    if len(signatures) < 3:
        click.echo("❌ Error: At least 3 trust node signatures required", err=True)
        return
    
    try:
        r = requests.post(f"{API}/redeem", json={
            "identity": identity,
            "scroll": scroll,
            "signatures": signatures
        })
        r.raise_for_status()
        result = r.json()
        
        click.echo(f"✅ Redemption sealed for {identity}")
        click.echo(f"   Redemption ID: {result['id']}")
        click.echo(f"   SHA-256: {result['sha256']}")
        click.echo(f"   Created: {result['created_at']}")
        click.echo(f"   {result.get('message', '')}")
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error: {e}", err=True)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json().get('detail', e.response.text)
                click.echo(f"   {error_detail}", err=True)
            except:
                click.echo(f"   {e.response.text}", err=True)

@cli.command()
@click.argument("identity")
def status(identity: str):
    """Get Sector X status for an identity"""
    try:
        r = requests.get(f"{API}/status/{identity}")
        r.raise_for_status()
        result = r.json()
        
        click.echo(f"\n🔍 Sector X Status: {identity}")
        click.echo(f"   Intent logs: {result['log_count']}")
        
        if result.get('latest_drift'):
            drift = result['latest_drift']
            triggered_icon = "🚨" if drift.get('triggered') else "✅"
            click.echo(f"   Latest drift: {triggered_icon} {drift.get('score', 0):.3f}")
        
        if result.get('redeemed'):
            click.echo(f"   Redemption: ✅ Redeemed at {result['redemption_at']}")
        else:
            click.echo(f"   Redemption: ⏳ Not yet redeemed")
        
        click.echo()
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error: {e}", err=True)
        if hasattr(e, 'response') and e.response is not None:
            click.echo(f"   {e.response.text}", err=True)

if __name__ == "__main__":
    cli()
