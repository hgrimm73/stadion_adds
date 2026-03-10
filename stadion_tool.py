import streamlit as st
import pandas as pd
import math
import random
import json
import os
import io
import requests
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from fpdf import FPDF

# ─────────────────────────────────────────────
#  KONFIGURATION & SICHERHEIT
# ─────────────────────────────────────────────
STORAGE_FILE = "data_storage.json"
PASSWORD = "SGE#2026adds"          # Besser: st.secrets["password"] verwenden
MAX_V_ITER  = 2000                 # Schutz vor Endlosschleife beim Vereinspuffer


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 Login")
        pwd = st.text_input("Passwort:", type="password")
        if st.button("Anmelden"):
            if pwd == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Falsches Passwort!")
        return False
    return True


# ─────────────────────────────────────────────
#  DATENPERSISTENZ
# ─────────────────────────────────────────────
def save_data():
    data = {
        "events": st.session_state.events,
        "grassfish_config": st.session_state.get("grassfish_config", {})
    }
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_data():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            st.session_state.events          = data.get("events", [])
            st.session_state.grassfish_config = _migrate_grassfish_config(data.get("grassfish_config", {}))
        except json.JSONDecodeError as e:
            st.warning(f"JSON-Fehler beim Laden: {e}. Starte mit leeren Daten.")
            _reset_session()
        except (KeyError, TypeError) as e:
            st.warning(f"Strukturfehler: {e}. Starte mit leeren Daten.")
            _reset_session()
        except OSError as e:
            st.error(f"Datei konnte nicht geöffnet werden: {e}")
            _reset_session()
    else:
        _reset_session()

    if not st.session_state.events:
        st.session_state.events = [make_default_event("Standard-Event")]


def _reset_session():
    st.session_state.events           = []
    st.session_state.grassfish_config = {}

def _migrate_grassfish_config(cfg: dict) -> dict:
    """Migriert alte Configs – stellt sicher dass Version nicht '1' ist."""
    if cfg.get("version") == "1":
        cfg["version"] = "1.12"
    return cfg


def make_default_event(name: str) -> dict:
    return {
        "name": name,
        "config": {
            "input_mode":     "Laufzeit (Minuten)",
            "total_event_min": 60,
            "pkg_S": 2.0,  "pkg_M": 5.0,  "pkg_L": 10.0,  "pkg_XL": 20.0,
            "dur_S": 5.0,  "dur_M": 10.0, "dur_L": 20.0,  "dur_XL": 40.0
        },
        "spots": []
    }


# ─────────────────────────────────────────────
#  HILFSFUNKTIONEN
# ─────────────────────────────────────────────
def compute_internal_pct(cfg: dict) -> dict:
    """Liefert Prozentwert pro Paket, unabhängig vom Eingabemodus."""
    mode      = cfg["input_mode"]
    total_min = cfg["total_event_min"]
    pct = {}
    for p in ["S", "M", "L", "XL"]:
        if mode == "Laufzeit (Minuten)":
            pct[p] = (cfg[f"dur_{p}"] / total_min * 100) if total_min > 0 else 0.0
        else:
            pct[p] = cfg[f"pkg_{p}"]
    return pct


# ─────────────────────────────────────────────
#  PLAYLIST-GENERIERUNG (OPTIMIERT)
# ─────────────────────────────────────────────
def generate_playlist(event: dict, play_mode: str):
    """
    Erzeugt eine Loop-Playlist mit minimaler Spotanzahl.
    Gibt (DataFrame, loop_duration_sek, error_string) zurück.
    """
    spots        = event["spots"]
    cfg          = event["config"]
    internal_pct = compute_internal_pct(cfg)

    df_all       = pd.DataFrame(spots)
    sponsoren_df = df_all[df_all["Typ"] != "Verein (Puffer)"].copy()
    vereins_df   = df_all[df_all["Typ"] == "Verein (Puffer)"].copy()

    if sponsoren_df.empty:
        return None, None, "Keine Sponsoren-Spots vorhanden."

    # ── Minimale Loop-Länge berechnen ──────────────────────────────────
    event_max_s = cfg["total_event_min"] * 60  # harte Obergrenze = Event-Dauer

    def min_loop_for_spot(row):
        pct = internal_pct.get(row["Typ"], 0)
        return (row["Dauer"] / (pct / 100)) if pct > 0 else event_max_s

    sponsoren_df["Min_Loop_Req"] = sponsoren_df.apply(min_loop_for_spot, axis=1)
    base_loop   = sponsoren_df["Min_Loop_Req"].max()

    min_v_time  = vereins_df["Dauer"].sum() if not vereins_df.empty else 0
    s_pct_sum   = sum(internal_pct.get(t, 0) for t in sponsoren_df["Typ"])
    v_pct_avail = max(0.01, 100.0 - s_pct_sum)
    loop_for_v  = (min_v_time / (v_pct_avail / 100)) if min_v_time > 0 else base_loop

    # Deckeln auf Event-Dauer
    loop_duration = min(max(base_loop, loop_for_v), event_max_s)

    # ── Sponsoren-Pool ─────────────────────────────────────────────────
    s_pool = []
    for _, row in sponsoren_df.iterrows():
        wdh = math.ceil((loop_duration * (internal_pct[row["Typ"]] / 100)) / row["Dauer"])
        for _ in range(wdh):
            s_pool.append({
                "id":    str(row["id"]),
                "Name":  row["Name"],
                "Dauer": int(row["Dauer"]),
                "Typ":   row["Typ"]
            })

    # ── Vereins-Pool ───────────────────────────────────────────────────
    # Ziel: jeder Vereins-Spot mind. 1x, insgesamt genug um die Restzeit zu füllen.
    v_list      = vereins_df.to_dict("records") if not vereins_df.empty else []
    v_instances = []
    if v_list:
        s_total_time = sum(s["Dauer"] for s in s_pool)
        remaining_s  = max(0.0, loop_duration - s_total_time)
        total_v_dur  = sum(v["Dauer"] for v in v_list)

        # Wie viele vollständige Runden werden gebraucht?
        if total_v_dur > 0 and remaining_s > 0:
            full_rounds = max(1, math.ceil(remaining_s / total_v_dur))
        else:
            full_rounds = 1

        for _ in range(min(full_rounds, 500)):
            for v in v_list:
                entry = dict(v)
                entry["id"] = str(entry["id"])
                v_instances.append(entry)

    # ── Anordnung ──────────────────────────────────────────────────────
    pkg_order = {"XL": 1, "L": 2, "M": 3, "S": 4}
    final_playlist = []

    if play_mode == "Durchmischt":
        random.shuffle(s_pool)
        v_idx = 0
        for s in s_pool:
            final_playlist.append(s)
            if v_idx < len(v_instances):
                final_playlist.append(v_instances[v_idx])
                v_idx += 1
        while v_idx < len(v_instances):
            final_playlist.append(v_instances[v_idx])
            v_idx += 1

    elif "zuerst" in play_mode:
        s_pool.sort(key=lambda x: pkg_order.get(x["Typ"], 5))
        final_playlist = s_pool + v_instances

    else:  # Sponsoren zuletzt
        s_pool.sort(key=lambda x: pkg_order.get(x["Typ"], 5))
        final_playlist = v_instances + s_pool

    # ── DataFrame aufbauen ────────────────────────────────────────────
    res_df = pd.DataFrame(final_playlist)
    t_acc, start_times = 0, []
    for d in res_df["Dauer"]:
        start_times.append(f"{int(t_acc//60):02d}:{int(t_acc%60):02d}")
        t_acc += d
    res_df.insert(0, "Start im Loop", start_times)

    return res_df, loop_duration, None


# ─────────────────────────────────────────────
#  TIMELINE-VISUALISIERUNG (Plotly)
# ─────────────────────────────────────────────
TYP_COLORS = {
    "S":              "#3498db",
    "M":              "#2ecc71",
    "L":              "#f39c12",
    "XL":             "#e74c3c",
    "Verein (Puffer)":"#95a5a6"
}

def show_timeline(res_df: pd.DataFrame):
    fig = go.Figure()
    t   = 0
    for _, row in res_df.iterrows():
        color = TYP_COLORS.get(row["Typ"], "#cccccc")
        label = str(row["Name"])[:18]
        fig.add_trace(go.Bar(
            x=[row["Dauer"]],
            base=[t],
            y=[row["Typ"]],
            orientation="h",
            marker_color=color,
            marker_line=dict(color="white", width=0.8),
            text=label,
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=(
                f"<b>{row['Name']}</b><br>"
                f"Start: {row['Start im Loop']}<br>"
                f"Dauer: {row['Dauer']} s<br>"
                f"Typ: {row['Typ']}<extra></extra>"
            ),
            showlegend=False,
            name=row["Name"]
        ))
        t += row["Dauer"]

    # Legende manuell
    for typ, col in TYP_COLORS.items():
        fig.add_trace(go.Bar(
            x=[0], y=[typ], orientation="h",
            marker_color=col, showlegend=True,
            name=typ, visible="legendonly"
        ))

    fig.update_layout(
        title=dict(text="⏱️ Loop-Timeline", font=dict(size=16)),
        xaxis=dict(title="Zeit (Sekunden)", tickformat="d"),
        yaxis=dict(title="", categoryorder="array",
                   categoryarray=["S", "M", "L", "XL", "Verein (Puffer)"]),
        barmode="stack",
        height=280,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="white"),
        margin=dict(l=10, r=10, t=50, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
#  PDF-EXPORT
# ─────────────────────────────────────────────
def create_pdf(df: pd.DataFrame, fig_buffer, event_name: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Loop-Playliste: {event_name}", ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 10)
    col_w = (pdf.w - 20) / 5
    for h in ["Start", "Name", "Dauer", "Typ", "ID"]:
        pdf.cell(col_w, 9, h, border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for _, row in df.iterrows():
        name_str = str(row["Name"])
        display  = (name_str[:20] + "..") if len(name_str) > 22 else name_str
        pdf.cell(col_w, 7, str(row["Start im Loop"]), border=1)
        pdf.cell(col_w, 7, display,                   border=1)
        pdf.cell(col_w, 7, f"{row['Dauer']}s",         border=1)
        pdf.cell(col_w, 7, str(row["Typ"]),            border=1)
        pdf.cell(col_w, 7, str(row["id"]),             border=1)
        pdf.ln()

    if fig_buffer:
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 9, "Zeitverteilung", ln=True)
        img_path = "/tmp/temp_plot.png"
        with open(img_path, "wb") as f:
            f.write(fig_buffer.getvalue())
        pdf.image(img_path, x=10, y=pdf.get_y(), w=110)

    return bytes(pdf.output())


# ─────────────────────────────────────────────
#  GRASSFISH API-HELFER
#  Auth: X-ApiKey Header (empfohlen laut Grassfish-Docs)
#  Basis: {server}/gv2/webservices/API/v{version}/{resource}
# ─────────────────────────────────────────────
def _gf_headers(api_key: str) -> dict:
    return {
        "Content-Type": "application/json",
        "Accept":       "application/json",
        "X-ApiKey":     api_key
    }

def _gf_base(server: str, version: str) -> str:
    return f"{server.rstrip('/')}/gv2/webservices/API/v{version}"

def _read_gf_duration(item: dict) -> int:
    """Liest Dauer aus einem Grassfish-Item, egal welcher Feldname oder Einheit."""
    for key in ["Duration","duration","Length","length","TotalDuration",
                "totalDuration","DurationInSeconds","PlayTime","Playtime","PlayDuration"]:
        val = item.get(key)
        if val is not None:
            try:
                f = float(val)
                # Millisekunden-Erkennung: >3600 bei üblichen Clips → ms
                return max(1, int(f / 1000) if f > 3600 else int(f))
            except (TypeError, ValueError):
                continue
    return 30  # Fallback

def gf_test_connection(server: str, api_key: str, version: str) -> dict:
    """Testet die Verbindung durch Abruf der Server-Version/Lizenz."""
    url  = f"{_gf_base(server, version)}/Licenses"
    resp = requests.get(url, headers=_gf_headers(api_key), timeout=10)
    resp.raise_for_status()
    return resp.json()

def gf_discover_versions(server: str, api_key: str) -> list:
    """
    Fragt den Server nach unterstützten API-Versionen.
    Probiert verschiedene Discovery-Endpunkte.
    """
    hdrs  = _gf_headers(api_key)
    base  = server.rstrip("/")
    found = []

    # Endpunkt 1: /gv2/webservices/API/Versions (ohne vX.Y)
    for url in [
        f"{base}/gv2/webservices/API/Versions",
        f"{base}/gv2/webservices/API/versions",
        f"{base}/gv2/webservices/API/swagger/docs/v1",
        f"{base}/gv2/webservices/API",
    ]:
        try:
            resp = requests.get(url, headers=hdrs, timeout=10)
            if resp.status_code == 200:
                found.append({"url": url, "status": 200, "body": resp.text[:500]})
        except Exception as e:
            found.append({"url": url, "status": f"Err: {e}"})

    # Endpunkt 2: 400-Body von v1.12/Playlists lesen (enthält oft erlaubte Version)
    diag_url = f"{base}/gv2/webservices/API/v1.12/Playlists"
    try:
        resp = requests.get(diag_url, headers=hdrs, timeout=10)
        found.append({"url": diag_url, "status": resp.status_code, "body": resp.text[:800]})
    except Exception as e:
        found.append({"url": diag_url, "status": f"Err:{e}", "body": ""})

    # Endpunkt 3: Swagger-Spec laden
    for swagger_url in [
        f"{base}/gv2/webservices/API/swagger/docs/v1",
        f"{base}/gv2/webservices/API/Help",
    ]:
        try:
            resp = requests.get(swagger_url, headers=hdrs, timeout=10)
            if resp.status_code == 200:
                found.append({"url": swagger_url, "status": 200, "body": resp.text[:1000]})
        except Exception:
            pass

    # Endpunkt 4: v1.3 bis v1.19 auf Playlists testen
    for minor in range(3, 20):
        ver = f"1.{minor}"
        try:
            url  = f"{base}/gv2/webservices/API/v{ver}/Playlists"
            resp = requests.get(url, headers=hdrs, timeout=5)
            found.append({"url": url, "status": resp.status_code,
                           "body": resp.text[:300] if resp.status_code != 400 else ""})
            if resp.status_code == 200:
                break
        except Exception:
            pass
    return found

def gf_get_folder_spots(server: str, api_key: str, version: str, folder_id: str) -> list:
    """
    Versucht mehrere Endpunkte in dieser Reihenfolge:
    1. /SpotGroups/{id}/Spots  (Grassfish-nativer Ordner-Endpunkt)
    2. /Spots?spotGroupId={id}
    3. /Spots?superSpotGroupId={id}
    4. /Spots + client-seitiger Filter nach bekannten Gruppen-Feldern
    Gibt Tupel (spots_list, strategy_used, raw_sample) zurück.
    """
    base = _gf_base(server, version)
    hdrs = _gf_headers(api_key)

    # Strategie 1: SpotGroups/{id}/Spots
    try:
        url  = f"{base}/SpotGroups/{folder_id}/Spots"
        resp = requests.get(url, headers=hdrs, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        spots = data if isinstance(data, list) else data.get("Items", data.get("items", []))
        if spots:
            return spots, "SpotGroups/{id}/Spots", spots[:1]
    except Exception:
        pass

    # Strategie 2: ?spotGroupId=
    try:
        resp = requests.get(f"{base}/Spots", params={"spotGroupId": folder_id},
                            headers=hdrs, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        spots = data if isinstance(data, list) else data.get("Items", data.get("items", []))
        if spots:
            return spots, "Spots?spotGroupId", spots[:1]
    except Exception:
        pass

    # Strategie 3: ?superSpotGroupId=
    try:
        resp = requests.get(f"{base}/Spots", params={"superSpotGroupId": folder_id},
                            headers=hdrs, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        spots = data if isinstance(data, list) else data.get("Items", data.get("items", []))
        if spots:
            return spots, "Spots?superSpotGroupId", spots[:1]
    except Exception:
        pass

    # Strategie 4: Alle laden, client-seitig filtern
    resp  = requests.get(f"{base}/Spots", headers=hdrs, timeout=30)
    resp.raise_for_status()
    data  = resp.json()
    all_spots = data if isinstance(data, list) else data.get("Items", data.get("items", []))
    sample    = all_spots[:1]
    fid_str   = str(folder_id)
    group_keys = ["SpotGroupId","spotGroupId","SuperSpotGroupId","superSpotGroupId",
                   "FolderId","folderId","GroupId","groupId","CustomerGroupId"]
    for key in group_keys:
        filtered = [s for s in all_spots if str(s.get(key,"")) == fid_str]
        if filtered:
            return filtered, f"Alle Spots → Filter '{key}'=={fid_str}", sample
    # Kein Filter griff – alle zurückgeben damit User debuggen kann
    return all_spots, f"KEIN FILTER GEFUNDEN – alle {len(all_spots)} Spots geladen", sample

def gf_get_spotgroups(server: str, api_key: str, version: str) -> list:
    """Lädt alle SpotGroups (= Ordner) für die Ordner-Auswahl."""
    url  = f"{_gf_base(server, version)}/SpotGroups"
    resp = requests.get(url, headers=_gf_headers(api_key), timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else data.get("Items", data.get("items", []))

def gf_get_playlists(server: str, api_key: str, version: str) -> tuple:
    """
    Probiert systematisch alle bekannten Versionen × Endpunkt-Namen.
    Gibt (liste, beschreibung, probe_log) zurück.
    probe_log = [(url, status_code_oder_fehler), ...]
    """
    versions_to_try   = [version] + [v for v in ["1.19","1.18","1.17","1.16","1.15","1.12","1"] if v != version]
    endpoints_to_try  = ["Playlists","playlists","PlaylistGroups","Playlist","ChannelPlaylists"]
    probe_log = []

    for ver in versions_to_try:
        for ep in endpoints_to_try:
            url = f"{_gf_base(server, ver)}/{ep}"
            try:
                resp = requests.get(url, headers=_gf_headers(api_key), timeout=10)
                probe_log.append((url, resp.status_code))
                if resp.status_code == 200:
                    data  = resp.json()
                    items = data if isinstance(data, list) else data.get("Items", data.get("items", []))
                    return items, f"v{ver}/{ep}", probe_log
            except requests.ConnectionError as e:
                probe_log.append((url, f"ConnErr: {e}"))
            except Exception as e:
                probe_log.append((url, str(e)[:60]))

    # Probe-Log in einer globalen Variable für die UI zugänglich machen
    raise RuntimeError(f"__PROBE_LOG__{repr(probe_log)}__END__Kein funktionierender Playlists-Endpunkt gefunden.")

def _gf_playlist_spot_urls(server: str, version: str, pl_id, version_id=None) -> list:
    """
    Alle bekannten URL-Varianten für Playlist-Spot-Operationen.
    version_id = ActiveVersion.Id aus der Playlist-Antwort (oft anders als pl_id!)
    """
    vers = [version] + [v for v in ["1.19","1.18","1.12","1"] if v != version]
    ids_to_try = [pl_id]
    if version_id and str(version_id) != str(pl_id):
        ids_to_try.append(version_id)

    combos = []
    for ver in vers:
        for pid in ids_to_try:
            for path in [
                f"Playlists/{pid}/Spots",
                f"Playlists/{pid}/PlaylistSpots",
                f"Playlists/{pid}/Contents",
                f"PlaylistVersions/{pid}/Spots",
                f"PlaylistVersions/{pid}/PlaylistSpots",
            ]:
                combos.append(f"{_gf_base(server, ver)}/{path}")
    return combos

def gf_probe_push_url(server: str, api_key: str, version: str, pl_id) -> str:
    """
    Findet den funktionierenden PUT-Endpunkt für Playlist-Spots.
    Sendet einen Probe-PUT mit leerem Body und schaut welche URL nicht 404 zurückgibt.
    """
    hdrs = _gf_headers(api_key)
    for url in _gf_playlist_spot_urls(server, version, pl_id):
        try:
            # OPTIONS oder HEAD zum Prüfen ob URL existiert
            resp = requests.head(url, headers=hdrs, timeout=5)
            if resp.status_code not in (404, 405):
                return url
            # 405 = Method Not Allowed aber URL existiert → auch gut
            if resp.status_code == 405:
                return url
        except Exception:
            pass
    # Fallback: GET probieren
    for url in _gf_playlist_spot_urls(server, version, pl_id):
        try:
            resp = requests.get(url, headers=hdrs, timeout=5)
            if resp.status_code != 404:
                return url
        except Exception:
            pass
    return None

def gf_clear_playlist(server: str, api_key: str, version: str, pl_id, version_id=None) -> tuple:
    """Leert die Playlist. Gibt (success, url_used, log) zurück."""
    log = []
    for url in _gf_playlist_spot_urls(server, version, pl_id, version_id):
        try:
            resp = requests.delete(url, headers=_gf_headers(api_key), timeout=15)
            log.append((url, resp.status_code))
            if resp.status_code in (200, 204):
                return True, url, log
            if resp.status_code == 404:
                continue  # falscher Pfad
        except Exception as e:
            log.append((url, str(e)))
    return False, None, log

def gf_fetch_swagger_endpoints(server: str, api_key: str, version: str) -> list:
    """Lädt die Swagger-Spec und extrahiert alle verfügbaren Endpunkte."""
    hdrs = _gf_headers(api_key)
    base = server.rstrip("/")
    endpoints = []
    for url in [
        f"{base}/gv2/webservices/API/swagger/docs/v{version}",
        f"{base}/gv2/webservices/API/swagger/docs/v1",
        f"{base}/gv2/webservices/API/Help/index",
    ]:
        try:
            resp = requests.get(url, headers=hdrs, timeout=15)
            if resp.status_code == 200:
                try:
                    spec = resp.json()
                    paths = spec.get("paths", {})
                    for path in paths:
                        if "playlist" in path.lower():
                            for method in paths[path]:
                                endpoints.append(f"{method.upper()} {path}")
                    return endpoints
                except Exception:
                    pass
        except Exception:
            pass
    return []

def gf_push_playlist(server: str, api_key: str, version: str, pl_id, spot_ids: list, version_id=None, playlist_obj=None) -> tuple:
    """
    Überträgt Spots in die Playlist.
    Strategie 1: Sub-Ressource /Spots (verschiedene Pfade & Bodies)
    Strategie 2: PUT /Playlists/{id} mit vollständigem Playlist-Objekt
    Strategie 3: PUT /PlaylistVersions/{vid} mit Spots im Body
    """
    log  = []
    hdrs = _gf_headers(api_key)
    vers = [version] + [v for v in ["1.19","1.18","1.12","1"] if v != version]

    spot_bodies = [
        [{"SpotId": int(s), "Position": i+1} for i, s in enumerate(spot_ids)],
        [{"Id":     int(s), "SortOrder":  i+1} for i, s in enumerate(spot_ids)],
        [{"ContentId": int(s), "Position": i+1} for i, s in enumerate(spot_ids)],
        [int(s) for s in spot_ids],
    ]

    # ── Strategie 1: Sub-Ressource ─────────────────────────────────────
    for url in _gf_playlist_spot_urls(server, version, pl_id, version_id):
        for body in spot_bodies:
            for method in [requests.put, requests.post]:
                try:
                    resp = method(url, json=body, headers=hdrs, timeout=30)
                    log.append((f"{'PUT' if method==requests.put else 'POST'} {url}",
                                resp.status_code, str(body)[:60]))
                    if resp.status_code in (200, 201, 204):
                        return True, url, log
                    if resp.status_code == 404:
                        break
                except Exception as e:
                    log.append((url, str(e), ""))
                    break
            else:
                continue
            break  # 404 → nächste URL

    # ── Strategie 2: PUT /Playlists/{id} mit vollständigem Objekt ──────
    spots_in_obj = [{"SpotId": int(s), "Position": i+1} for i, s in enumerate(spot_ids)]
    for ver in vers:
        for pid in ([pl_id] + ([version_id] if version_id and version_id != pl_id else [])):
            for url, body in [
                # Playlist-Objekt mit Spots drin
                (f"{_gf_base(server, ver)}/Playlists/{pid}",
                 {"Id": int(pl_id), "Spots": spots_in_obj}),
                # PlaylistVersion mit Spots
                (f"{_gf_base(server, ver)}/PlaylistVersions/{pid}",
                 {"Id": int(pid), "Spots": spots_in_obj, "PlaylistSpots": spots_in_obj}),
                # Nur Spots-Array direkt an die Playlist
                (f"{_gf_base(server, ver)}/Playlists/{pid}",
                 {"PlaylistSpots": spots_in_obj}),
            ]:
                for method in [requests.put, requests.patch]:
                    try:
                        resp = method(url, json=body, headers=hdrs, timeout=30)
                        label = "PUT" if method == requests.put else "PATCH"
                        log.append((f"{label} {url}", resp.status_code, str(body)[:80]))
                        if resp.status_code in (200, 201, 204):
                            return True, f"{label} {url}", log
                    except Exception as e:
                        log.append((url, str(e), ""))

    return False, None, log

def render_sidebar_usage(event: dict):
    cfg          = event["config"]
    spots        = event["spots"]
    internal_pct = compute_internal_pct(cfg)

    st.sidebar.subheader("📊 Paket-Belegung")
    allocated_total = 0.0
    for p in ["S", "M", "L", "XL"]:
        has_spots = any(s["Typ"] == p for s in spots)
        pct_val   = internal_pct[p]
        allocated_total += pct_val
        label = f"Paket {p}: {pct_val:.1f}%"
        bar   = min(1.0, pct_val / 100.0)
        if has_spots:
            st.sidebar.progress(bar, text=f"✅ {label}")
        else:
            st.sidebar.progress(0.0, text=f"⬜ {label} (kein Spot)")

    remaining = max(0.0, 100.0 - allocated_total)
    bar_r     = min(1.0, remaining / 100.0)
    st.sidebar.progress(bar_r, text=f"🔵 Verein/frei: {remaining:.1f}%")


# ═══════════════════════════════════════════════════════════════════════
#  HAUPTPROGRAMM
# ═══════════════════════════════════════════════════════════════════════
if check_password():

    if "events" not in st.session_state:
        load_data()
    if "grassfish_config" not in st.session_state:
        st.session_state.grassfish_config = {}

    st.set_page_config(page_title="Stadion Ad-Manager", layout="wide", page_icon="🏟️")
    st.title("🏟️ Stadion Ad-Inventory Manager")

    # ─── TABS ──────────────────────────────────────────────────────────
    tab_events, tab_grassfish = st.tabs(["📋  Events & Playlisten", "🔌  Grassfish-Integration"])

    # ══════════════════════════════════════════════════════════════════
    #  TAB 1: EVENTS & PLAYLISTEN
    # ══════════════════════════════════════════════════════════════════
    with tab_events:

        # ── SIDEBAR ────────────────────────────────────────────────────
        st.sidebar.header("⚙️ Event-Verwaltung")

        if st.sidebar.button("💾 Alle Daten speichern"):
            save_data()
            st.sidebar.success("Gespeichert!")

        if st.sidebar.button("🚪 Abmelden"):
            st.session_state.authenticated = False
            st.rerun()

        # Event auswählen / anlegen
        event_names = [e["name"] for e in st.session_state.events]

        with st.sidebar.expander("➕ Neues Event anlegen"):
            new_ev_name = st.text_input("Name", key="new_ev_name")
            if st.button("Event erstellen", key="btn_create_ev"):
                stripped = new_ev_name.strip()
                if not stripped:
                    st.warning("Bitte einen Namen eingeben.")
                elif stripped in event_names:
                    st.warning(f"'{stripped}' existiert bereits.")
                else:
                    st.session_state.events.append(make_default_event(stripped))
                    save_data()
                    st.rerun()

        sel_ev_name = st.sidebar.selectbox("Aktives Event", event_names, key="sel_event")
        ev_idx      = event_names.index(sel_ev_name)
        event       = st.session_state.events[ev_idx]

        if len(st.session_state.events) > 1:
            if st.sidebar.button(f"🗑️ '{sel_ev_name}' löschen"):
                st.session_state.events.pop(ev_idx)
                save_data()
                st.rerun()

        st.sidebar.divider()

        # ── Konfiguration des aktiven Events ──────────────────────────
        st.sidebar.subheader("📐 Konfiguration")
        cfg = event["config"]

        input_mode = st.sidebar.radio(
            "Berechnungs-Basis", ["Prozent", "Laufzeit (Minuten)"],
            index=0 if cfg["input_mode"] == "Prozent" else 1,
            key=f"mode_{ev_idx}"
        )
        cfg["input_mode"] = input_mode

        total_min = st.sidebar.number_input(
            "Event-Dauer (Minuten)", min_value=1,
            value=int(cfg["total_event_min"]), key=f"totmin_{ev_idx}"
        )
        cfg["total_event_min"] = total_min

        st.sidebar.subheader("📦 Paket-Werte")
        for p in ["S", "M", "L", "XL"]:
            cfg_key = f"pkg_{p}" if input_mode == "Prozent" else f"dur_{p}"
            unit    = "%" if input_mode == "Prozent" else "Min"
            val     = st.sidebar.number_input(
                f"Paket {p} ({unit})", min_value=0.0,
                value=float(cfg.get(cfg_key, 0.0)),
                step=0.5, key=f"pkg_{p}_{ev_idx}"
            )
            cfg[cfg_key] = val

        # Paket-Belegung Fortschrittsbalken
        render_sidebar_usage(event)

        # ── MAIN CONTENT ───────────────────────────────────────────────
        st.header(f"📋 Event: **{sel_ev_name}**")

        col_main, col_stats = st.columns([3, 1])
        spots = event["spots"]

        with col_stats:
            st.metric("Spots gesamt",    len(spots))
            n_sponsor = sum(1 for s in spots if s["Typ"] != "Verein (Puffer)")
            n_verein  = len(spots) - n_sponsor
            st.metric("Sponsoren-Spots", n_sponsor)
            st.metric("Vereins-Spots",   n_verein)
            internal_pct = compute_internal_pct(cfg)
            used_pct = sum(internal_pct[t] for t in ["S","M","L","XL"]
                           if any(s["Typ"] == t for s in spots))
            st.metric("Gebuchte %",      f"{used_pct:.1f}%")

        with col_main:
            # ── Spot hinzufügen ────────────────────────────────────────
            with st.expander("➕ Spot manuell hinzufügen", expanded=True):
                with st.form("add_form", clear_on_submit=True):
                    c1, c2, c3 = st.columns([3, 1, 2])
                    new_name = c1.text_input("Dateiname / Bezeichnung")
                    new_dur  = c2.number_input("Dauer (Sek.)", min_value=1, value=30)
                    new_pkg  = c3.selectbox("Typ", ["S", "M", "L", "XL", "Verein (Puffer)"])
                    submitted = st.form_submit_button("➕ Hinzufügen")

                    if submitted:
                        stripped_name = new_name.strip()
                        if not stripped_name:
                            st.warning("Bitte einen Dateinamen eingeben.")
                        elif any(s["Name"] == stripped_name and s["Typ"] == new_pkg
                                 for s in spots):
                            st.warning(
                                f"⚠️ **Duplikat erkannt:** '{stripped_name}' "
                                f"mit Typ '{new_pkg}' ist bereits in der Liste."
                            )
                        else:
                            spots.append({
                                "id":    random.randint(10000, 99999),
                                "Name":  stripped_name,
                                "Dauer": new_dur,
                                "Typ":   new_pkg
                            })
                            save_data()
                            st.rerun()

            # ── Spot-Liste anzeigen ────────────────────────────────────
            if spots:
                for s_i, spot in enumerate(spots):
                    cn, cd, ct, cb = st.columns([3, 1, 2, 1])
                    cn.text(spot["Name"])
                    cd.text(f"{spot['Dauer']} s")
                    ct.text(f"Typ: {spot['Typ']}")
                    if cb.button("🗑️", key=f"del_{ev_idx}_{s_i}_{spot['id']}",
                                 help="Spot entfernen"):
                        event["spots"] = [s for j, s in enumerate(spots) if j != s_i]
                        save_data()
                        st.rerun()
            else:
                st.info("Noch keine Spots vorhanden. Füge Spots manuell hinzu oder importiere sie über die Grassfish-Integration.")

        # ── PLAYLIST GENERATOR ─────────────────────────────────────────
        if spots:
            st.divider()
            st.subheader("🚀 Playlist generieren")

            play_mode = st.radio(
                "Ausspielungs-Modus",
                ["Durchmischt", "Block: Sponsoren zuerst", "Block: Sponsoren zuletzt"],
                horizontal=True,
                key=f"pm_{ev_idx}"
            )

            if st.button("🎬 Playlist jetzt generieren", type="primary"):
                res_df, loop_dur, err = generate_playlist(event, play_mode)
                if err:
                    st.error(err)
                else:
                    st.session_state[f"pl_{ev_idx}"]       = res_df
                    st.session_state[f"pl_dur_{ev_idx}"]   = loop_dur

            # ── Ergebnis anzeigen ──────────────────────────────────────
            if f"pl_{ev_idx}" in st.session_state:
                res_df   = st.session_state[f"pl_{ev_idx}"]
                loop_dur = st.session_state[f"pl_dur_{ev_idx}"]
                total_s  = res_df["Dauer"].sum()

                c1, c2, c3 = st.columns(3)
                c1.success(f"⏱ Loop-Dauer: **{int(loop_dur//60)} m {int(loop_dur%60)} s**")
                c2.info(f"📦 Spots in Playlist: **{len(res_df)}**")
                c3.info(f"🕐 Gesamtlaufzeit: **{total_s} s**")

                # Timeline
                show_timeline(res_df)

                # Tabelle
                st.dataframe(
                    res_df[["Start im Loop", "Name", "Dauer", "Typ", "id"]],
                    use_container_width=True,
                    column_config={
                        "Dauer": st.column_config.Column("Dauer (s)", width="small"),
                        "id":    st.column_config.Column("GF-ID",     width="small")
                    }
                )

                # Export-Buttons
                col_csv, col_pdf = st.columns(2)

                with col_csv:
                    csv_bytes = res_df.to_csv(index=False, sep=";").encode("utf-8-sig")
                    st.download_button(
                        "📥 CSV exportieren",
                        data=csv_bytes,
                        file_name=f"playlist_{sel_ev_name}.csv",
                        mime="text/csv"
                    )

                with col_pdf:
                    # Tortendiagramm für PDF
                    plot_data  = res_df.groupby(["Name", "Typ"])["Dauer"].sum().reset_index()
                    fig_p, ax  = plt.subplots(figsize=(4, 4))
                    cmap       = plt.get_cmap("tab20")
                    pie_colors = [
                        cmap(i % 20) if t != "Verein (Puffer)" else "#d3d3d3"
                        for i, t in enumerate(plot_data["Typ"])
                    ]
                    ax.pie(
                        plot_data["Dauer"],
                        labels=plot_data["Name"],
                        autopct="%1.1f%%",
                        startangle=90,
                        colors=pie_colors,
                        wedgeprops={"edgecolor": "black", "linewidth": 0.5},
                        textprops={"fontsize": 7}
                    )
                    ax.axis("equal")
                    buf = io.BytesIO()
                    fig_p.savefig(buf, format="png", bbox_inches="tight", dpi=150)
                    plt.close(fig_p)

                    pdf_bytes = create_pdf(
                        res_df[["Start im Loop", "Name", "Dauer", "Typ", "id"]],
                        buf, sel_ev_name
                    )
                    st.download_button(
                        "📄 PDF exportieren",
                        data=pdf_bytes,
                        file_name=f"playlist_{sel_ev_name}.pdf",
                        mime="application/pdf"
                    )

    # ══════════════════════════════════════════════════════════════════
    #  TAB 2: GRASSFISH INTEGRATION
    # ══════════════════════════════════════════════════════════════════
    with tab_grassfish:
        st.header("🔌 Grassfish Digital Signage Integration")
        st.markdown(
            "Verbinde dich mit deinem Grassfish-Server, importiere Inhalte aus einem Ordner, "
            "klassifiziere sie und übertrage die generierte Playlist direkt ins System."
        )

        gf_cfg = st.session_state.grassfish_config

        # ── Verbindungseinstellungen ────────────────────────────────────
        with st.expander("🔑 Verbindungseinstellungen", expanded=True):
            st.info(
                "Die Grassfish-API verwendet **API-Key-Authentifizierung** (`X-ApiKey` Header). "
                "Den API-Key findest du im Grassfish Manager unter *Administration → API-Zugang*.",
                icon="ℹ️"
            )
            cg1, cg2, cg3 = st.columns([3, 2, 1])
            gf_url     = cg1.text_input("Server-URL", value=gf_cfg.get("url", "https://ds.evisco.com"),
                                         placeholder="https://ihr-server.com")
            gf_api_key = cg2.text_input("API-Key (X-ApiKey)", value=gf_cfg.get("api_key", ""),
                                         type="password", placeholder="Dein Grassfish API-Key")
            gf_version = cg3.text_input("API-Version", value=gf_cfg.get("version", "1.12"),
                                         help="Standard: 1.12  (für ältere Instanzen ggf. 1)")

            gf_cfg["url"]     = gf_url
            gf_cfg["api_key"] = gf_api_key
            gf_cfg["version"] = gf_version

            col_test, col_disc, col_swagger = st.columns(3)
            if col_swagger.button("📋 Playlist-Endpunkte aus Swagger"):
                if not gf_api_key:
                    st.error("Bitte API-Key eingeben.")
                else:
                    _ver_s = gf_cfg.get("version_playlists", gf_cfg.get("version","1.19"))
                    with st.spinner("Lade Swagger-Spec …"):
                        eps = gf_fetch_swagger_endpoints(gf_url, gf_api_key, _ver_s)
                    if eps:
                        st.success(f"✅ {len(eps)} Playlist-Endpunkte gefunden:")
                        for ep in eps:
                            st.code(ep)
                    else:
                        st.warning("Keine Playlist-Endpunkte in Swagger-Spec gefunden.")

            if col_disc.button("🔎 API-Versionen entdecken"):
                if not gf_api_key:
                    st.error("Bitte API-Key eingeben.")
                else:
                    with st.spinner("Suche verfügbare API-Versionen …"):
                        results = gf_discover_versions(gf_url, gf_api_key)
                    st.session_state["gf_discovery"] = results
                    # Playlist-Version automatisch erkennen und speichern
                    import re as _re
                    for _r in results:
                        if _r.get("status") == 200 and "/Playlists" in _r.get("url",""):
                            _m = _re.search(r"/v([\d.]+)/Playlists", _r["url"])
                            if _m:
                                gf_cfg["version_playlists"] = _m.group(1)
                                st.success(f"✅ Playlist-Version erkannt: **v{_m.group(1)}** – automatisch gespeichert!")
                                break

            if "gf_discovery" in st.session_state:
                disc = st.session_state["gf_discovery"]
                success = [r for r in disc if r["status"] == 200]
                if success:
                    st.success(f"✅ Funktionierende Endpunkte gefunden!")
                    for r in success:
                        st.code(r["url"])
                        st.caption(r.get("body","")[:300])
                else:
                    st.warning("Noch keine 200-Antwort gefunden – alle Ergebnisse:")
                with st.expander("Alle Discovery-Ergebnisse"):
                    for r in disc:
                        icon = "✅" if r["status"] == 200 else "❌"
                        st.caption(f"{icon} `{r['status']}` → {r['url']}")
                        if r.get("body"):
                            st.code(r["body"][:300], language="json")

            if col_test.button("🔗 Verbindung testen"):
                if not all([gf_url, gf_api_key]):
                    st.error("Bitte Server-URL und API-Key ausfüllen.")
                else:
                    try:
                        with st.spinner("Verbinde …"):
                            gf_test_connection(gf_url, gf_api_key, gf_version)
                            st.session_state["gf_connected"] = True
                        st.success("✅ Verbindung erfolgreich! API antwortet korrekt.")
                    except requests.HTTPError as e:
                        st.session_state["gf_connected"] = False
                        st.error(
                            f"HTTP-Fehler {e.response.status_code}: {e.response.text[:300]}\n\n"
                            f"**Geprüfte URL:** `{gf_url}/gv2/webservices/API/v{gf_version}/Licenses`\n\n"
                            "Bitte API-Version prüfen (z.B. `1` oder `1.12`)."
                        )
                    except requests.ConnectionError:
                        st.session_state["gf_connected"] = False
                        st.error(f"Verbindung zu `{gf_url}` fehlgeschlagen. Server erreichbar?")
                    except Exception as e:
                        st.session_state["gf_connected"] = False
                        st.error(f"Fehler: {e}")

        if st.session_state.get("gf_connected"):
            st.success("🟢 Verbunden mit Grassfish")
        else:
            st.warning("🔴 Noch nicht verbunden – bitte oben Verbindung testen.")

        st.divider()

        # ── Schritte nebeneinander ──────────────────────────────────────
        step1, step2, step3 = st.columns([1, 1, 1])

        # ── SCHRITT 1: Ordner importieren ───────────────────────────────
        with step1:
            st.subheader("1️⃣  Content importieren")
            _key = gf_cfg.get("api_key", "")
            _ver = gf_cfg.get("version", "1.12")

            # Ordner-Browser
            if st.button("🗂️ Verfügbare Ordner (SpotGroups) anzeigen", key="btn_browse_folders"):
                if not _key:
                    st.warning("Bitte zuerst API-Key eingeben und Verbindung testen.")
                else:
                    try:
                        with st.spinner("Lade SpotGroups …"):
                            groups = gf_get_spotgroups(gf_url, _key, _ver)
                            st.session_state["gf_spotgroups"] = groups
                    except requests.HTTPError as e:
                        st.error(f"HTTP-Fehler {e.response.status_code}: {e.response.text[:200]}")
                    except Exception as e:
                        st.error(f"Fehler beim Laden der SpotGroups: {e}")

            if "gf_spotgroups" in st.session_state:
                grps = st.session_state["gf_spotgroups"]
                if grps:
                    grp_rows = [
                        {"ID":   str(g.get("Id",   g.get("id",   "?"))),
                         "Name": str(g.get("Name", g.get("name", "?"))),
                         "SuperID": str(g.get("SuperSpotGroupId",
                                              g.get("superSpotGroupId", "–")))}
                        for g in grps
                    ]
                    st.dataframe(pd.DataFrame(grp_rows), use_container_width=True,
                                 hide_index=True, height=180)
                    st.caption("👆 Notiere die ID des gewünschten Ordners und trage sie unten ein.")
                else:
                    st.info("Keine SpotGroups gefunden – ggf. andere API-Version?")

            st.divider()

            folder_id = st.text_input("Ordner-ID eingeben", value=gf_cfg.get("folder_id", ""),
                                       placeholder="z.B. 42", key="gf_folder_id")
            gf_cfg["folder_id"] = folder_id

            if st.button("📂 Ordner laden", key="btn_load_folder"):
                if not _key:
                    st.warning("Bitte zuerst API-Key eingeben und Verbindung testen.")
                elif not folder_id:
                    st.warning("Bitte Ordner-ID eingeben.")
                else:
                    try:
                        with st.spinner("Lade Inhalte (versuche mehrere Endpunkte) …"):
                            spots, strategy, sample = gf_get_folder_spots(
                                gf_url, _key, _ver, folder_id)
                            st.session_state["gf_folder_contents"] = spots
                            st.session_state["gf_load_strategy"]   = strategy
                            st.session_state["gf_raw_sample"]      = sample
                    except requests.HTTPError as e:
                        st.error(f"HTTP-Fehler {e.response.status_code}: {e.response.text[:300]}")
                    except Exception as e:
                        st.error(f"Fehler: {e}")

            if "gf_folder_contents" in st.session_state:
                spots    = st.session_state["gf_folder_contents"]
                strategy = st.session_state.get("gf_load_strategy", "?")

                if "KEIN FILTER" in strategy:
                    st.warning(
                        f"⚠️ {strategy}\n\n"
                        "Kein passender Ordner-Filter gefunden. Bitte schau dir den "
                        "**Debug: Rohstruktur** unten an und teile mit, welches Feld "
                        "die Ordner-Zugehörigkeit speichert."
                    )
                else:
                    st.success(f"✅ **{len(spots)} Spots** geladen via `{strategy}`")

                preview = [
                    {"Name":  str(s.get("Name",     s.get("name",     "?"))),
                     "Dauer": f"{_read_gf_duration(s)} s",
                     "ID":    str(s.get("Id",       s.get("id",       "?")))}
                    for s in spots[:15]
                ]
                st.dataframe(pd.DataFrame(preview), use_container_width=True,
                             hide_index=True, height=220)

                # Debug-Panel
                with st.expander("🔍 Debug: Rohstruktur eines Spots (alle Felder)"):
                    sample = st.session_state.get("gf_raw_sample", spots[:1])
                    if sample:
                        st.json(sample[0])
                        st.caption(
                            "👆 Hier siehst du alle Felder eines Spots. Prüfe, "
                            "welches Feld die Ordner-ID enthält (z.B. SpotGroupId, "
                            "SuperSpotGroupId, CustomerId …)"
                        )

        # ── SCHRITT 2: Klassifizieren & übernehmen ─────────────────────
        with step2:
            st.subheader("2️⃣  Klassifizieren")
            if "gf_folder_contents" not in st.session_state:
                st.info("Zuerst Ordner laden (Schritt 1).")
            else:
                contents    = st.session_state["gf_folder_contents"]
                ev_names_g  = [e["name"] for e in st.session_state.events]
                target_ev   = st.selectbox("Ziel-Event", ev_names_g, key="gf_target_ev")
                target_ev_i = ev_names_g.index(target_ev)

                if "gf_cls" not in st.session_state:
                    st.session_state["gf_cls"] = {}

                with st.form("classify_form"):
                    for c_i, item in enumerate(contents):
                        iid   = str(item.get("Id",       item.get("id",       "")))
                        iname = str(item.get("Name",     item.get("name",     "?")))
                        idur  = _read_gf_duration(item)
                        cn, ct = st.columns([3, 2])
                        cn.caption(f"**{iname[:28]}**\n{idur} s | ID {iid}")
                        cls_val = ct.selectbox(
                            "", ["Ignorieren", "S", "M", "L", "XL", "Verein (Puffer)"],
                            key=f"cls_{c_i}_{iid}"
                        )
                        st.session_state["gf_cls"][iid] = {
                            "name": iname, "duration": idur,
                            "type": cls_val, "gf_id": iid
                        }

                    if st.form_submit_button("✅ In Event übernehmen"):
                        added = dupes = 0
                        tev   = st.session_state.events[target_ev_i]
                        for iid, cd in st.session_state["gf_cls"].items():
                            if cd["type"] == "Ignorieren":
                                continue
                            if any(s["Name"] == cd["name"] and s["Typ"] == cd["type"]
                                   for s in tev["spots"]):
                                dupes += 1
                                continue
                            tev["spots"].append({
                                "id":    cd["gf_id"],
                                "Name":  cd["name"],
                                "Dauer": int(cd["duration"]),
                                "Typ":   cd["type"]
                            })
                            added += 1
                        save_data()
                        st.success(f"✅ {added} Spots hinzugefügt, {dupes} Duplikate übersprungen.")

        # ── SCHRITT 3: Playlist pushen ─────────────────────────────────
        with step3:
            st.subheader("3️⃣  Playlist pushen")
            ev_names_p = [e["name"] for e in st.session_state.events]
            push_ev    = st.selectbox("Event mit Playlist", ev_names_p, key="gf_push_ev")
            push_ev_i  = ev_names_p.index(push_ev)

            if f"pl_{push_ev_i}" not in st.session_state:
                st.info("Zuerst Playlist im Tab 'Events & Playlisten' generieren.")
            else:
                res_push = st.session_state[f"pl_{push_ev_i}"]
                st.caption(f"Bereit: {len(res_push)} Spots")

                # ── Workaround: Manuelle Playlist-ID ─────────────────────
                with st.expander("🔧 Playlist-ID manuell eingeben"):
                    st.caption(
                        "Falls das automatische Laden fehlschlägt: Öffne den Grassfish Manager, "
                        "navigiere zur Playlist und kopiere die ID aus der URL oder den Einstellungen."
                    )
                    c_mid, c_mname = st.columns(2)
                    manual_pl_id   = c_mid.text_input("Playlist-ID", placeholder="z.B. 123", key="manual_pl_id")
                    manual_pl_name = c_mname.text_input("Name", placeholder="z.B. Stadion Loop", key="manual_pl_name")
                    if st.button("Übernehmen", key="btn_manual_pl"):
                        if manual_pl_id.strip():
                            mname = manual_pl_name.strip() or f"Playlist {manual_pl_id}"
                            st.session_state["gf_playlists"]  = [{"Id": manual_pl_id.strip(), "Name": mname}]
                            st.session_state["gf_pl_version"] = gf_cfg.get("version", "1.12")
                            st.success(f"Playlist gesetzt: {mname} (ID {manual_pl_id})")
                            st.rerun()
                        else:
                            st.warning("Bitte Playlist-ID eingeben.")
                st.divider()
                if st.button("🔄 GF-Playlisten laden", key="btn_load_pls"):
                    _key = gf_cfg.get("api_key", "")
                    _ver = gf_cfg.get("version_playlists", gf_cfg.get("version", "1.19"))
                    if not _key:
                        st.warning("Bitte zuerst API-Key eingeben und Verbindung testen.")
                    else:
                        try:
                            with st.spinner("Lade Playlisten (probiere Endpunkte) …"):
                                pls, used_desc, probe_log = gf_get_playlists(gf_url, _key, _ver)
                                st.session_state["gf_playlists"]  = pls
                                st.session_state["gf_pl_version"] = used_desc.split("/")[0].lstrip("v")
                                st.session_state["gf_pl_probe"]   = probe_log
                                # ActiveVersion-IDs für jede Playlist speichern
                                ver_map = {}
                                for p in pls:
                                    pid = str(p.get("Id", p.get("id","")))
                                    av  = p.get("ActiveVersion", p.get("activeVersion", {}))
                                    vid = av.get("Id", av.get("id","")) if isinstance(av, dict) else ""
                                    ver_map[pid] = str(vid) if vid else pid
                                st.session_state["gf_pl_ver_map"] = ver_map
                            st.success(f"✅ {len(pls)} Playlisten geladen via `{used_desc}`")
                        except RuntimeError as e:
                            msg = str(e)
                            probe_log = []
                            if "__PROBE_LOG__" in msg:
                                try:
                                    import ast as _ast
                                    log_str = msg.split("__PROBE_LOG__")[1].split("__END__")[0]
                                    probe_log = _ast.literal_eval(log_str)
                                    msg = msg.split("__END__")[1]
                                except Exception:
                                    pass
                            st.error(msg)
                            with st.expander("🔍 Debug: alle geprüften Endpunkte", expanded=True):
                                if probe_log:
                                    for url, status in probe_log:
                                        icon = "✅" if status == 200 else "❌"
                                        st.caption(f"{icon} `{status}` → {url}")
                                else:
                                    st.warning("Keine Endpunkte wurden erreicht – möglicherweise Netzwerk- oder TLS-Problem.")
                                    st.caption(f"Geprüfte Server-URL: `{gf_url}`")
                        except Exception as e:
                            st.error(f"Fehler: {e}")

                if "gf_playlists" in st.session_state:
                    pls = st.session_state["gf_playlists"]
                    pl_map = {}
                    for p in pls:
                        pid  = p.get("Id",   p.get("id",   "?"))
                        name = p.get("Name", p.get("name", "?"))
                        av   = p.get("ActiveVersion", p.get("activeVersion", {}))
                        vid  = av.get("Id", av.get("id","")) if isinstance(av, dict) else ""
                        label = f"{name}  (Playlist-ID {pid}, Version-ID {vid})" if vid else f"{name}  (ID {pid})"
                        pl_map[label] = pid
                    sel_pl_name = st.selectbox("Ziel-Playlist in Grassfish", list(pl_map.keys()))
                    sel_pl_id   = pl_map[sel_pl_name]

                    clear_opt = st.checkbox("Playlist vorher leeren", value=True,
                                             help="Empfohlen, um Fehler durch veraltete Einträge zu vermeiden.")

                    if st.button("🚀 Playlist übertragen", type="primary"):
                        _key = gf_cfg.get("api_key", "")
                        _ver = st.session_state.get("gf_pl_version", gf_cfg.get("version", "1.19"))
                        if not _key:
                            st.warning("Bitte zuerst API-Key eingeben und Verbindung testen.")
                        else:
                            spot_ids = res_push["id"].tolist()
                            push_log = []
                            try:
                                ver_map   = st.session_state.get("gf_pl_ver_map", {})
                                version_id = ver_map.get(str(sel_pl_id), sel_pl_id)
                                with st.spinner("Übertrage …"):
                                    if clear_opt:
                                        ok_c, url_c, log_c = gf_clear_playlist(gf_url, _key, _ver, sel_pl_id, version_id)
                                        push_log += [(f"DELETE {u}", s, "") for u, s in log_c]
                                        if not ok_c:
                                            st.warning("⚠️ Playlist konnte nicht geleert werden – fahre trotzdem fort.")
                                    ok_p, url_p, log_p = gf_push_playlist(gf_url, _key, _ver, sel_pl_id, spot_ids, version_id)
                                    push_log += log_p
                                if ok_p:
                                    st.success(f"✅ {len(spot_ids)} Spots übertragen via `{url_p}`")
                                    st.balloons()
                                else:
                                    st.error("❌ Kein funktionierender Push-Endpunkt gefunden.")
                                    with st.expander("🔍 Debug: Push-Versuche", expanded=True):
                                        for entry in push_log:
                                            url_e = entry[0]; status_e = entry[1]
                                            body_e = entry[2] if len(entry) > 2 else ""
                                            icon = "✅" if str(status_e) in ("200","201","204") else "❌"
                                            st.caption(f"{icon} `{status_e}` → {url_e}")
                                            if body_e:
                                                st.caption(f"   Body: `{body_e}`")
                            except Exception as e:
                                st.error(f"Fehler: {e}")
                                with st.expander("🔍 Debug"):
                                    for entry in push_log:
                                        st.caption(str(entry))
