"""
Hagleitner Bohrtechnik GmbH
PDF Generator API Server

Dieser Server empfängt JSON-Daten von Google Apps Script
und gibt ein fertiges Bohrprotokoll-PDF zurück.

Deployment: Railway.app, Render.com oder Google Cloud Run
"""

from flask import Flask, request, send_file, jsonify
import tempfile
import os
import sys

# Importiere den PDF-Generator (liegt im gleichen Verzeichnis)
from bohrprotokoll_generator import generate_bohrprotokoll

app = Flask(__name__)

# ── Sicherheit: Einfacher API-Key ────────────────────────────────────────────
# Diesen Key trägst du auch in Google Apps Script ein
API_KEY = os.environ.get("BOHRPROTOKOLL_API_KEY", "hagleitner-secret-key-2026")


@app.route("/health", methods=["GET"])
def health():
    """Einfacher Health-Check — zum Testen ob der Server läuft."""
    return jsonify({"status": "ok", "service": "Hagleitner Bohrprotokoll Generator"})


@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    """
    Hauptendpunkt: Empfängt Bohrprotokoll-Daten als JSON, gibt PDF zurück.

    Erwarteter JSON-Body (alle Felder optional außer bericht_nr):
    {
        "api_key": "hagleitner-secret-key-2026",
        "bauvorhaben": "Naumanngasse 38a, 5020 Salzburg",
        "auftraggeber": "Frodinger",
        "bericht_nr": "5431",
        "datum": "30.03.2026",
        "bohrgeraet": "Rotomax XL 1",
        "bohrmeister": "Müller",
        "schichten": [
            {"von": "0,00", "bis": "0,30", "beschreibung": "Humus"},
            {"von": "0,30", "bis": "10,00", "beschreibung": "mG, gG, gS"}
        ],
        ... weitere Felder
    }
    """

    # ── API-Key prüfen ────────────────────────────────────────────────────────
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Kein gültiger JSON-Body"}), 400

    # if data.get("api_key") != API_KEY:
    #     return jsonify({"error": "Ungültiger API-Key"}), 401

    # ── Pflichtfeld prüfen ────────────────────────────────────────────────────
    if not data.get("bericht_nr"):
        return jsonify({"error": "Pflichtfeld 'bericht_nr' fehlt"}), 400

    # ── PDF generieren ────────────────────────────────────────────────────────
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        generate_bohrprotokoll(data, tmp_path)

        filename = f"Bohrprotokoll_{data.get('bericht_nr', 'unbekannt')}.pdf"

        return send_file(
            tmp_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": f"PDF-Generierung fehlgeschlagen: {str(e)}"}), 500

    finally:
        # Temporäre Datei aufräumen
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"✓ Bohrprotokoll API Server läuft auf Port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
