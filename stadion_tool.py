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

# Evisco-Logo (base64-kodiert)
EVISCO_LOGO_B64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/4QAiRXhpZgAATU0AKgAAAAgAAQESAAMAAAABAAEAAAAAAAD/7AARRHVja3kAAQAEAAAAZAAA/+EDkGh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8APD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4NCjx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTM4IDc5LjE1OTgyNCwgMjAxNi8wOS8xNC0wMTowOTowMSAgICAgICAgIj4NCgk8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPg0KCQk8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ4bXAuZGlkOmIwOGVmMDUzLTU4OWQtZmQ0MS04MDI0LTZjMWVmY2VlMzFmOCIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDo0NDUyQzdCRTZCQzYxMUU3QTQ5RUYwNjM1NjE3RkY5MCIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo0NDUyQzdCRDZCQzYxMUU3QTQ5RUYwNjM1NjE3RkY5MCIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxNyAoV2luZG93cykiPg0KCQkJPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6YmFmYzM1ZWQtOGI3Yy1iMDQ3LWJiZTEtZTFmOTRhYmQ5ODM0IiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOmIwOGVmMDUzLTU4OWQtZmQ0MS04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"


# ─────────────────────────────────────────────
#  KONFIGURATION & SICHERHEIT
# ─────────────────────────────────────────────
STORAGE_FILE = "data_storage.json"
PASSWORD = "EV#2026adds"           # Besser: st.secrets["password"] verwenden
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
def save_data(force: bool = False):
    """
    force=True  → sofort auf Disk schreiben (nur beim expliziten Speichern-Button).
    force=False → nur als "ungespeichert" markieren (Standard für alle UI-Aktionen).
    """
    st.session_state["_unsaved"] = True
    if force:
        _write_to_disk()

def _write_to_disk():
    # Generierte Playlisten serialisieren
    playlists = []
    for i in range(len(st.session_state.get("events", []))):
        df  = st.session_state.get(f"pl_{i}")
        dur = st.session_state.get(f"pl_dur_{i}")
        if df is not None and dur is not None:
            playlists.append({"df": df.to_dict(orient="records"), "dur": dur})
        else:
            playlists.append(None)

    data = {
        "events":           st.session_state.events,
        "grassfish_config": st.session_state.get("grassfish_config", {}),
        "playlists":        playlists,
    }
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    st.session_state["_unsaved"] = False


def load_data():
    # Alte Playlist-Keys aus Session löschen vor dem Laden
    keys_to_del = [k for k in st.session_state if k.startswith("pl_")]
    for k in keys_to_del:
        del st.session_state[k]
    st.session_state.pop("gf_cls", None)
    st.session_state.pop("gf_folder_contents", None)
    st.session_state.pop("gf_playlists", None)

    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            st.session_state.events           = data.get("events", [])
            st.session_state.grassfish_config = _migrate_grassfish_config(data.get("grassfish_config", {}))
            # Gespeicherte Playlisten wiederherstellen
            for i, pl_data in enumerate(data.get("playlists", [])):
                if pl_data:
                    st.session_state[f"pl_{i}"]     = pd.DataFrame(pl_data["df"])
                    st.session_state[f"pl_dur_{i}"] = pl_data["dur"]
            st.session_state["_unsaved"] = False
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
    Unterstützt Sponsor-Gruppen (mehrere Files pro Sponsor).
    Gibt (DataFrame, loop_duration_sek, error_string|warning_string) zurück.
    Das dritte Element ist None (OK), ein str mit "⚠️" (Warnung) oder ein str ohne (Fehler).
    """
    spots        = event["spots"]
    cfg          = event["config"]
    internal_pct = compute_internal_pct(cfg)

    df_all       = pd.DataFrame(spots)
    # Sponsor-Feld mit Fallback auf Typ (Abwärtskompatibilität)
    if "Sponsor" not in df_all.columns:
        df_all["Sponsor"] = df_all["Typ"]

    sponsoren_df = df_all[df_all["Typ"] != "Verein (Puffer)"].copy()
    vereins_df   = df_all[df_all["Typ"] == "Verein (Puffer)"].copy()

    if sponsoren_df.empty:
        return None, None, "Keine Sponsoren-Spots vorhanden."

    event_max_s = cfg["total_event_min"] * 60

    # ── Gruppen-basierte Loop-Berechnung ──────────────────────────────
    # Gruppe = eindeutiger (Sponsor, Typ). Alle Files einer Gruppe teilen sich den %-Anteil.
    # Mindest-Loop: die Gruppe muss so lang sein, dass alle Spots mind. 1x passen.
    group_min_loops = []
    for (sponsor, typ), grp in sponsoren_df.groupby(["Sponsor", "Typ"], sort=False):
        pct = internal_pct.get(typ, 0)
        if pct <= 0:
            continue
        group_total_dur = grp["Dauer"].sum()  # eine Runde durch alle Gruppe-Spots
        min_loop = group_total_dur / (pct / 100)
        group_min_loops.append(min_loop)

    base_loop = max(group_min_loops) if group_min_loops else event_max_s

    min_v_time  = vereins_df["Dauer"].sum() if not vereins_df.empty else 0
    s_pct_sum   = sum(internal_pct.get(t, 0) for t in sponsoren_df["Typ"].unique())
    v_pct_avail = max(0.01, 100.0 - s_pct_sum)
    loop_for_v  = (min_v_time / (v_pct_avail / 100)) if min_v_time > 0 else base_loop

    loop_duration = min(max(base_loop, loop_for_v), event_max_s)

    # ── Warnung wenn Playlist durch Mindest-1x-Bedingung sehr groß wird ──
    warning_msg = None
    min_possible_spots = len(sponsoren_df) + (len(vereins_df) if not vereins_df.empty else 0)
    min_possible_dur   = sponsoren_df["Dauer"].sum() + vereins_df["Dauer"].sum() if not vereins_df.empty else sponsoren_df["Dauer"].sum()
    if min_possible_dur > loop_duration * 0.8:
        warning_msg = (
            f"⚠️ Die Mindestanzahl der Spots ({min_possible_spots}) erfordert "
            f"bereits {int(min_possible_dur//60)}:{int(min_possible_dur%60):02d} min – "
            f"die Playlist wird dadurch groß. Trotzdem fortfahren?"
        )

    # ── Sponsoren-Pool: gruppen-weise, gleichmäßig verteilt ───────────
    # Jede Gruppe bekommt `rounds` Durchläufe, jeder Spot erscheint mind. 1x.
    # Innerhalb einer Gruppe werden Spots reihum eingetragen (round-robin).
    group_pools = {}  # key=(sponsor,typ) → list of spot-dicts (mit Wiederholungen)
    for (sponsor, typ), grp in sponsoren_df.groupby(["Sponsor", "Typ"], sort=False):
        pct = internal_pct.get(typ, 0)
        if pct <= 0:
            continue
        group_total_dur = grp["Dauer"].sum()
        rounds = max(1, math.ceil((loop_duration * (pct / 100)) / group_total_dur))
        grp_spots = grp.to_dict("records")
        pool = []
        for r in range(rounds):
            for spot in grp_spots:
                pool.append({
                    "id":      str(spot["id"]),
                    "Name":    spot["Name"],
                    "Dauer":   int(spot["Dauer"]),
                    "Typ":     spot["Typ"],
                    "Sponsor": spot["Sponsor"],
                })
        group_pools[(sponsor, typ)] = pool

    # Alle Sponsor-Pools zusammenführen
    s_pool = [item for pool in group_pools.values() for item in pool]

    # ── Vereins-Pool ──────────────────────────────────────────────────
    v_list      = vereins_df.to_dict("records") if not vereins_df.empty else []
    v_instances = []
    if v_list:
        s_total_time = sum(s["Dauer"] for s in s_pool)
        remaining_s  = max(0.0, loop_duration - s_total_time)
        total_v_dur  = sum(v["Dauer"] for v in v_list)
        full_rounds  = max(1, math.ceil(remaining_s / total_v_dur)) if total_v_dur > 0 and remaining_s > 0 else 1
        for _ in range(min(full_rounds, 500)):
            for v in v_list:
                entry = dict(v)
                entry["id"]      = str(entry["id"])
                entry["Sponsor"] = entry.get("Sponsor", "Verein (Puffer)")
                v_instances.append(entry)

    # ── Anordnung: Sponsor-Gruppen gleichmäßig verteilen ─────────────
    pkg_order = {"XL": 1, "L": 2, "M": 3, "S": 4}

    def distribute_evenly(s_pool, v_instances, loop_duration):
        """
        Verteilt Sponsor-Spots gleichmäßig über die gesamte Loop-Zeitachse.
        Jeder Sponsor bekommt N Slots, die gleichmäßig über den Loop verteilt sind.
        Verein-Spots füllen die Lücken zwischen den Sponsor-Slots.

        Idee:
        - Berechne für jeden Sponsor den "Abstand" zwischen seinen Auftritten
          (loop_duration / anzahl_auftritte).
        - Weise jedem Sponsor-Spot einen Ziel-Zeitpunkt zu.
        - Sortiere alle Sponsor-Spots nach Ziel-Zeitpunkt.
        - Baue die finale Liste auf: Sponsor-Spot → fülle Lücke mit Verein-Spots.
        """
        from collections import deque

        # Ziel-Zeitpunkte pro Sponsor berechnen
        # Jeder Sponsor-Spot bekommt einen gleichmäßig verteilten Slot
        sponsor_groups = {}
        for spot in s_pool:
            key = spot["Sponsor"]
            sponsor_groups.setdefault(key, []).append(spot)

        timed_spots = []  # (ziel_zeitpunkt, spot)
        for sponsor, spots_of_sponsor in sponsor_groups.items():
            n = len(spots_of_sponsor)
            interval = loop_duration / n
            # Erster Auftritt leicht versetzt je nach Sponsor (verhindert Überlappung)
            offset = list(sponsor_groups.keys()).index(sponsor) * (interval / max(len(sponsor_groups), 1))
            offset = offset % interval
            for i, spot in enumerate(spots_of_sponsor):
                target_t = offset + i * interval
                timed_spots.append((target_t, sponsor, spot))

        # Nach Ziel-Zeitpunkt sortieren; bei Gleichstand nach Sponsor-Name
        timed_spots.sort(key=lambda x: (x[0], x[1]))

        # Verein-Pool als Deque für einfaches Entnehmen
        v_queue = deque(v_instances)
        total_v = len(v_instances)
        # Wie viele Verein-Spots zwischen je zwei Sponsor-Spots?
        n_sponsor = len(timed_spots)
        v_per_gap = total_v / max(n_sponsor, 1)  # float, wird gerundet

        result = []
        v_budget = 0.0
        for _, _, spot in timed_spots:
            result.append(spot)
            v_budget += v_per_gap
            # Ganze Verein-Spots aus dem Budget entnehmen
            while v_budget >= 1.0 and v_queue:
                result.append(v_queue.popleft())
                v_budget -= 1.0

        # Verbleibende Verein-Spots anhängen
        while v_queue:
            result.append(v_queue.popleft())

        return result

    final_playlist = []
    if play_mode == "Durchmischt":
        final_playlist = distribute_evenly(s_pool, v_instances, loop_duration)
    elif "zuerst" in play_mode:
        s_pool.sort(key=lambda x: pkg_order.get(x["Typ"], 5))
        final_playlist = s_pool + v_instances
    else:
        s_pool.sort(key=lambda x: pkg_order.get(x["Typ"], 5))
        final_playlist = v_instances + s_pool

    # ── DataFrame aufbauen ───────────────────────────────────────────
    res_df = pd.DataFrame(final_playlist)
    t_acc, start_times = 0, []
    for d in res_df["Dauer"]:
        start_times.append(f"{int(t_acc//60):02d}:{int(t_acc%60):02d}")
        t_acc += d
    res_df.insert(0, "Start im Loop", start_times)

    return res_df, loop_duration, warning_msg


# ─────────────────────────────────────────────
#  TIMELINE-VISUALISIERUNG (Plotly)
# ─────────────────────────────────────────────
# Feste Farb-Palette für Sponsor-Gruppen
_SPONSOR_COLORS = [
    "#e63946","#f4a261","#2a9d8f","#457b9d","#e9c46a",
    "#264653","#6a994e","#ff595e","#8ac926","#6a4c93",
    "#1982c4","#ffca3a","#bc4749","#a8dadc","#3d405b",
]
TYP_COLORS = {
    "S": "#457b9d", "M": "#2a9d8f", "L": "#f4a261",
    "XL": "#e63946", "Verein (Puffer)": "#adb5bd"
}

def _sponsor_color_map(res_df: pd.DataFrame) -> dict:
    cmap = {}
    ci   = 0
    col  = res_df["Sponsor"] if "Sponsor" in res_df.columns else res_df["Typ"]
    for sponsor in col.unique():
        if sponsor == "Verein (Puffer)":
            cmap[sponsor] = "#adb5bd"
        else:
            cmap[sponsor] = _SPONSOR_COLORS[ci % len(_SPONSOR_COLORS)]
            ci += 1
    return cmap

def show_timeline(res_df: pd.DataFrame):
    fig      = go.Figure()
    t        = 0
    cmap     = _sponsor_color_map(res_df)
    seen     = set()

    for _, row in res_df.iterrows():
        sponsor = row.get("Sponsor", row["Typ"]) if "Sponsor" in row.index else row["Typ"]
        color   = cmap.get(sponsor, "#cccccc")
        label   = str(row["Name"])[:18]
        y_label = sponsor  # Zeile im Chart = Sponsor-Gruppe

        fig.add_trace(go.Bar(
            x=[row["Dauer"]],
            base=[t],
            y=[y_label],
            orientation="h",
            marker_color=color,
            marker_line=dict(color="white", width=0.8),
            text=label,
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=(
                f"<b>{row['Name']}</b><br>"
                f"Sponsor: {sponsor}<br>"
                f"Start: {row['Start im Loop']}<br>"
                f"Dauer: {row['Dauer']} s<br>"
                f"Typ: {row['Typ']}<extra></extra>"
            ),
            showlegend=sponsor not in seen,
            legendgroup=sponsor,
            name=sponsor,
        ))
        seen.add(sponsor)
        t += row["Dauer"]

    fig.update_layout(
        title=dict(text="⏱️ Loop-Timeline", font=dict(size=16)),
        xaxis=dict(title="Zeit (Sekunden)", tickformat="d"),
        yaxis=dict(title=""),
        barmode="stack",
        height=max(280, 60 * len(cmap) + 80),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="white"),
        margin=dict(l=10, r=10, t=60, b=40)
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

# Bekannte Feldnamen für Dauer – wird automatisch erweitert wenn neuer Name entdeckt wird
_DURATION_KEYS = [
    "Duration", "duration", "Length", "length",
    "TotalDuration", "totalDuration", "DurationInSeconds", "durationInSeconds",
    "PlayTime", "Playtime", "playtime", "PlayDuration", "playDuration",
    "FileDuration", "fileDuration", "ContentDuration", "SpotDuration",
    "RuntimeSeconds", "RuntimeMs", "DurationMs", "DurationSec",
]

def _extract_val(item: dict, dotted_key: str):
    """Liest einen Wert aus einem Dict, auch verschachtelt (z.B. 'ActiveVersion.Duration')."""
    parts = dotted_key.split(".")
    cur = item
    for part in parts:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur

def _detect_duration_key(item: dict) -> str | None:
    """
    Findet automatisch den richtigen Feldnamen für die Dauer.
    Sucht auch in verschachtelten Objekten (z.B. ActiveVersion.Duration).
    Gibt gepunkteten Pfad zurück (z.B. 'ActiveVersion.Duration').
    """
    # 1) Bekannte Top-Level-Namen
    for key in _DURATION_KEYS:
        if key in item and item[key] is not None:
            try:
                float(item[key])
                return key
            except (TypeError, ValueError):
                pass

    # 2) Verschachtelte Suche in dict-Werten (eine Ebene tief)
    for parent_key, parent_val in item.items():
        if isinstance(parent_val, dict):
            for key in _DURATION_KEYS:
                if key in parent_val and parent_val[key] is not None:
                    try:
                        float(parent_val[key])
                        return f"{parent_key}.{key}"
                    except (TypeError, ValueError):
                        pass
            # Heuristik in verschachtelten Dicts
            for key, val in parent_val.items():
                if any(h in key.lower() for h in ["dur","length","runtime"]):
                    try:
                        f = float(val)
                        if 0 < f < 100_000:
                            return f"{parent_key}.{key}"
                    except (TypeError, ValueError):
                        pass

    # 3) Heuristik Top-Level
    for key, val in item.items():
        if any(h in key.lower() for h in ["dur","length","runtime","playtime"]):
            try:
                f = float(val)
                if 0 < f < 100_000:
                    return key
            except (TypeError, ValueError):
                pass
    return None

def _read_gf_duration(item: dict, override_key: str = None) -> int:
    """Liest Dauer aus einem Grassfish-Item, auch aus verschachtelten Feldern."""
    key = override_key or _detect_duration_key(item)
    if key:
        val = _extract_val(item, key)
        if val is not None:
            try:
                f = float(val)
                return max(1, int(f / 1000) if f > 3600 else int(f))
            except (TypeError, ValueError):
                pass
    return 30

def _get_numeric_fields(item: dict) -> list:
    """Gibt alle Felder mit numerischen Werten zurück – auch verschachtelt."""
    result = []
    for key, val in item.items():
        if isinstance(val, dict):
            for sub_key, sub_val in val.items():
                try:
                    f = float(sub_val)
                    result.append({"Feldname": f"{key}.{sub_key}", "Wert": f,
                                   "Als Sekunden": int(f/1000) if f > 3600 else int(f)})
                except (TypeError, ValueError):
                    pass
        else:
            try:
                f = float(val)
                result.append({"Feldname": key, "Wert": f,
                               "Als Sekunden": int(f/1000) if f > 3600 else int(f)})
            except (TypeError, ValueError):
                pass
    return result

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
    vid  = version_id if version_id else pl_id
    vers = [version] + [v for v in ["1.19","1.18","1.12","1"] if v != version]

    # Primär: DELETE /PlaylistVersions/{vid}/Items
    for ver in vers:
        for pid in list(dict.fromkeys([vid, pl_id])):
            for path in [f"PlaylistVersions/{pid}/Items",
                         f"Playlists/{pid}/Spots",
                         f"Playlists/{pid}/Items"]:
                url = f"{_gf_base(server, ver)}/{path}"
                try:
                    resp = requests.delete(url, headers=_gf_headers(api_key), timeout=15)
                    log.append((f"DELETE {url}", resp.status_code))
                    if resp.status_code in (200, 204):
                        return True, url, log
                except Exception as e:
                    log.append((f"DELETE {url}", str(e)))
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

def gf_create_playlist_version(server: str, api_key: str, version: str,
                               pl_id, valid_from_iso: str) -> tuple:
    """
    Erstellt eine neue Version einer bestehenden Playlist.
    Probiert alle bekannten Endpunkt-Varianten durch.
    Gibt (neue_version_id, url_verwendet, log) zurück, oder (None, None, log) bei Fehler.
    """
    hdrs = _gf_headers(api_key)
    log  = []
    vers = [version] + [v for v in ["1.19", "1.18", "1.12"] if v != version]

    # Mögliche Body-Varianten (ValidFrom als ISO-8601-String)
    bodies = [
        {"PlaylistId": int(pl_id), "ValidFrom": valid_from_iso},
        {"PlaylistId": int(pl_id), "ValidFrom": valid_from_iso, "Status": "Draft"},
        {"PlaylistId": int(pl_id), "ValidFrom": valid_from_iso, "Status": "Released"},
        {"PlaylistId": str(pl_id), "ValidFrom": valid_from_iso},
    ]
    # Mögliche Endpunkte
    paths = [
        f"PlaylistVersions",
        f"Playlists/{pl_id}/Versions",
        f"Playlists/{pl_id}/PlaylistVersions",
    ]

    for ver in vers:
        for path in paths:
            url = f"{_gf_base(server, ver)}/{path}"
            for body in bodies:
                try:
                    resp = requests.post(url, json=body, headers=hdrs, timeout=15)
                    log.append((f"POST {url}", resp.status_code, str(body)[:120]))
                    if resp.status_code in (200, 201):
                        # Neue Version-ID aus Antwort lesen
                        try:
                            data   = resp.json()
                            new_id = (data.get("Id") or data.get("id") or
                                      data.get("VersionId") or data.get("versionId") or
                                      (data.get("ActiveVersion") or {}).get("Id"))
                            if new_id:
                                log.append((f"→ Neue Version-ID: {new_id}", 0, ""))
                                return str(new_id), url, log
                        except Exception:
                            pass
                        # Kein JSON / kein ID-Feld → trotzdem als Erfolg werten
                        log.append(("→ Keine Version-ID in Antwort – nutze pl_id als Fallback", 0, ""))
                        return str(pl_id), url, log
                    elif resp.status_code == 404:
                        break  # Endpunkt existiert nicht → nächsten probieren
                except Exception as e:
                    log.append((f"POST {url}", str(e), str(body)[:80]))
    return None, None, log


def gf_push_playlist(server: str, api_key: str, version: str, pl_id, spot_ids: list, version_id=None, playlist_obj=None, spot_durations: dict = None) -> tuple:
    """
    Überträgt Spots in die Playlist.
    Primär: POST /v1.19/PlaylistVersions/{versionId}/Items  (ein Item pro Request)
    Fallback: diverse ältere Pfad-/Body-Varianten
    """
    log  = []
    hdrs = _gf_headers(api_key)
    vers = [version] + [v for v in ["1.19","1.18","1.12","1"] if v != version]
    vid  = version_id if version_id else pl_id  # ActiveVersion.Id bevorzugen

    # ── Primär-Strategie: POST /PlaylistVersions/{vid}/Items einzeln ───
    # Korrekte Body-Struktur laut Grassfish API-Doku:
    # SpotId + SequenceNumber (Position) + DurationSeconds
    def make_item(spot_id, position):
        dur = (spot_durations or {}).get(str(spot_id), 30)
        return {
            "SpotId":          int(spot_id),
            "SequenceNumber":  position,
            "DurationSeconds": int(dur),
        }
        return body

    for ver in vers:
        url = f"{_gf_base(server, ver)}/PlaylistVersions/{vid}/Items"
        # Teste mit erstem Spot
        test_body = make_item(spot_ids[0], 1)
        try:
            resp = requests.post(url, json=test_body, headers=hdrs, timeout=15)
            log.append((f"POST {url}", resp.status_code, str(test_body)))
        except Exception as e:
            log.append((f"POST {url}", str(e), str(test_body)))
            continue

        if resp.status_code == 404:
            continue  # falsche Version → nächste versuchen

        if resp.status_code in (200, 201, 204):
            # Restliche Spots übertragen
            failed = 0
            for i, spot_id in enumerate(spot_ids[1:], start=2):
                body = make_item(spot_id, i)
                try:
                    r = requests.post(url, json=body, headers=hdrs, timeout=15)
                    log.append((f"POST {url}", r.status_code, str(body)))
                    if r.status_code not in (200, 201, 204):
                        failed += 1
                except Exception as e:
                    log.append((f"POST {url}", str(e), str(body)))
                    failed += 1
            result_url = f"POST {url} ({len(spot_ids)-failed}/{len(spot_ids)} OK)"
            return failed == 0, result_url, log

        # Anderer Fehler (z.B. 400/422) → Body-Problem, nicht URL-Problem → loggen & weiter
        log.append((f"POST {url}", resp.status_code, f"Response: {resp.text[:200]}"))

    # ── Fallback: Array-basierte Endpunkte ──────────────────────────────
    array_bodies = [
        [{"SpotId": int(s), "Position": i+1} for i, s in enumerate(spot_ids)],
        [{"Id":     int(s), "SortOrder":  i+1} for i, s in enumerate(spot_ids)],
        [{"ContentId": int(s), "Position": i+1} for i, s in enumerate(spot_ids)],
    ]
    for ver in vers:
        for pid in list(dict.fromkeys([vid, pl_id])):
            for path in [f"PlaylistVersions/{pid}/Items",
                         f"Playlists/{pid}/Spots",
                         f"Playlists/{pid}/Items"]:
                url = f"{_gf_base(server, ver)}/{path}"
                for body in array_bodies:
                    for method in [requests.post, requests.put]:
                        try:
                            resp = method(url, json=body, headers=hdrs, timeout=30)
                            label = "POST" if method == requests.post else "PUT"
                            log.append((f"{label} {url}", resp.status_code, str(body)[:80]))
                            if resp.status_code in (200, 201, 204):
                                return True, f"{label} {url}", log
                            if resp.status_code == 404:
                                break
                        except Exception as e:
                            log.append((url, str(e), ""))
                    if log and log[-1][1] == 404:
                        break

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
    if "_unsaved" not in st.session_state:
        st.session_state["_unsaved"] = False

    st.set_page_config(page_title="Stadion Ad-Manager", layout="wide", page_icon="🏟️")
    st.title("🏟️ Stadion Ad-Manager")

    # ─── TABS ──────────────────────────────────────────────────────────
    tab_events, tab_grassfish = st.tabs(["📋  Events & Playlisten", "🔌  Grassfish-Integration"])

    # ══════════════════════════════════════════════════════════════════
    #  TAB 1: EVENTS & PLAYLISTEN
    # ══════════════════════════════════════════════════════════════════
    with tab_events:

        # ── SIDEBAR ────────────────────────────────────────────────────
        st.sidebar.markdown(
            f'<img src="data:image/jpeg;base64,{EVISCO_LOGO_B64}" '
            'style="width:150px;display:block;margin-bottom:10px;">',
            unsafe_allow_html=True
        )
        st.sidebar.header("⚙️ Event-Verwaltung")

        # ── Speichern / Laden / Export / Import ───────────────────────
        unsaved = st.session_state.get("_unsaved", False)
        if unsaved:
            st.sidebar.warning("⚠️ Ungespeicherte Änderungen")

        c_save, c_load = st.sidebar.columns(2)
        if c_save.button("💾 Speichern", type="primary", use_container_width=True,
                         help="Alle Daten auf dem Server zwischenspeichern"):
            _write_to_disk()
            st.sidebar.success("✅ Gespeichert!")
            # kein rerun → Spots bleiben sichtbar

        if c_load.button("📂 Laden", type="secondary", use_container_width=True,
                         help="Gespeicherten Stand vom Server laden"):
            if st.session_state.get("_unsaved"):
                st.session_state["_confirm_load"] = True
            else:
                load_data()
                st.rerun()

        # Bestätigung für Laden bei ungespeicherten Änderungen
        if st.session_state.get("_confirm_load"):
            st.sidebar.error("⚠️ Ungespeicherte Änderungen gehen verloren!")
            cc1, cc2 = st.sidebar.columns(2)
            if cc1.button("Ja, laden", key="btn_confirm_load"):
                st.session_state.pop("_confirm_load", None)
                load_data()
                st.rerun()
            if cc2.button("Abbrechen", key="btn_cancel_load"):
                st.session_state.pop("_confirm_load", None)
                st.rerun()

        st.sidebar.divider()

        # ── Daten exportieren / importieren ────────────────────────────
        # Wichtig: Streamlit Cloud setzt das Filesystem bei Neustarts zurück.
        # Daher: Daten als JSON herunterladen (lokal sichern) und wieder hochladen.
        with st.sidebar.expander("💿 Daten exportieren / importieren"):
            # Export
            export_data = {
                "events":           st.session_state.get("events", []),
                "grassfish_config": st.session_state.get("grassfish_config", {}),
                "playlists":        [
                    {"df": st.session_state[f"pl_{i}"].to_dict(orient="records"),
                     "dur": st.session_state[f"pl_dur_{i}"]}
                    if f"pl_{i}" in st.session_state else None
                    for i in range(len(st.session_state.get("events", [])))
                ],
            }
            export_bytes = json.dumps(export_data, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button(
                label="⬇️ Alle Daten herunterladen",
                data=export_bytes,
                file_name="stadion_admanager_backup.json",
                mime="application/json",
                use_container_width=True,
                help="Speichert alle Events, Spots, GF-Konfiguration und Playlisten als JSON-Datei auf deinem Gerät."
            )

            st.caption("Gespeicherte JSON-Datei wieder hochladen:")
            uploaded = st.file_uploader(
                "JSON-Datei hochladen",
                type=["json"],
                key="import_json",
                label_visibility="collapsed"
            )
            if uploaded is not None:
                if st.button("✅ Importieren & laden", key="btn_do_import",
                             use_container_width=True):
                    try:
                        data = json.loads(uploaded.read().decode("utf-8"))
                        # Alte Playlist-Keys löschen
                        for k in [k for k in st.session_state if k.startswith("pl_")]:
                            del st.session_state[k]
                        st.session_state.events           = data.get("events", [])
                        st.session_state.grassfish_config = _migrate_grassfish_config(
                            data.get("grassfish_config", {}))
                        for i, pl_data in enumerate(data.get("playlists", [])):
                            if pl_data:
                                st.session_state[f"pl_{i}"]     = pd.DataFrame(pl_data["df"])
                                st.session_state[f"pl_dur_{i}"] = pl_data["dur"]
                        st.session_state["_unsaved"] = False
                        _write_to_disk()   # sofort auf Server sichern
                        st.rerun()
                    except Exception as e:
                        st.error(f"Import fehlgeschlagen: {e}")

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

        # Aktiven Event-Namen persistent halten → kein Index-Sprung nach rerun
        _saved_ev = st.session_state.get("_active_event")
        _default_idx = event_names.index(_saved_ev) if _saved_ev in event_names else 0
        sel_ev_name = st.sidebar.selectbox(
            "Aktives Event", event_names,
            index=_default_idx,
            key="sel_event"
        )
        st.session_state["_active_event"] = sel_ev_name
        ev_idx = event_names.index(sel_ev_name)
        event  = st.session_state.events[ev_idx]

        if len(st.session_state.events) > 1:
            if st.sidebar.button(f"🗑️ '{sel_ev_name}' löschen"):
                st.session_state.events.pop(ev_idx)
                save_data()
                st.rerun()

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
                    new_name    = c1.text_input("Dateiname / Bezeichnung")
                    new_dur     = c2.number_input("Dauer (Sek.)", min_value=1, value=30)
                    new_pkg     = c3.selectbox("Typ", ["S", "M", "L", "XL", "Verein (Puffer)"])
                    # Sponsor-Bezeichnung (leer = kein Gruppen-Label)
                    sponsor_existing = sorted(set(
                        s.get("Sponsor", s["Typ"]) for s in spots
                        if s["Typ"] != "Verein (Puffer)"
                    ))
                    new_sponsor = st.text_input(
                        "Sponsor-Label (optional – für Gruppierung mehrerer Files)",
                        placeholder="z.B. Allianz, Sponsor AG …"
                    )
                    submitted = st.form_submit_button("➕ Hinzufügen")

                    if submitted:
                        stripped_name = new_name.strip()
                        sponsor_val   = new_sponsor.strip() or new_pkg
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
                                "id":      random.randint(10000, 99999),
                                "Name":    stripped_name,
                                "Dauer":   new_dur,
                                "Typ":     new_pkg,
                                "Sponsor": sponsor_val,
                            })
                            save_data()
                            st.rerun()

            # ── Spot-Liste anzeigen ────────────────────────────────────
            if spots:
                col_del_all, _ = st.columns([1, 4])
                if col_del_all.button("🗑️ Alle Spots löschen", key=f"del_all_{ev_idx}",
                                       type="secondary",
                                       help="Alle Spots dieses Events löschen"):
                    event["spots"] = []
                    st.session_state.pop(f"pl_{ev_idx}", None)
                    st.session_state.pop(f"pl_dur_{ev_idx}", None)
                    save_data()
                    st.rerun()
                for s_i, spot in enumerate(spots):
                    cn, cd, ct, cs, cb = st.columns([3, 1, 1, 2, 1])
                    cn.text(spot["Name"])
                    cd.text(f"{spot['Dauer']} s")
                    sponsor_lbl = spot.get("Sponsor", spot["Typ"])
                    cs.caption(f"🏷 {sponsor_lbl}" if sponsor_lbl != spot["Typ"] else "")
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
                res_df, loop_dur, _gen_msg = generate_playlist(event, play_mode)
                if _gen_msg and not _gen_msg.startswith("⚠️"):
                    st.error(_gen_msg)
                else:
                    if _gen_msg and _gen_msg.startswith("⚠️"):
                        st.warning(_gen_msg)
                    st.session_state[f"pl_{ev_idx}"]     = res_df
                    st.session_state[f"pl_dur_{ev_idx}"] = loop_dur
                    if loop_dur > 600:  # > 10 Minuten
                        st.session_state[f"pl_longwarn_{ev_idx}"] = True
                    else:
                        st.session_state.pop(f"pl_longwarn_{ev_idx}", None)

            # ── Ergebnis anzeigen ──────────────────────────────────────
            if f"pl_{ev_idx}" in st.session_state:
                res_df   = st.session_state[f"pl_{ev_idx}"]
                loop_dur = st.session_state[f"pl_dur_{ev_idx}"]
                total_s  = res_df["Dauer"].sum()

                if st.session_state.get(f"pl_longwarn_{ev_idx}"):
                    st.warning(f"⚠️ Achtung! Die Playliste ist bereits länger als 10 Minuten! (Loop-Dauer: {int(loop_dur//60)} m {int(loop_dur%60)} s)")

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
                     "Dauer": f"{_read_gf_duration(s, gf_cfg.get('dur_field_override') or None)} s",
                     "ID":    str(s.get("Id",       s.get("id",       "?")))}
                    for s in spots[:15]
                ]
                st.dataframe(pd.DataFrame(preview), use_container_width=True,
                             hide_index=True, height=220)

                # Debug-Panel
                with st.expander("🔍 Debug: Rohstruktur & Feld-Erkennung"):
                    sample = st.session_state.get("gf_raw_sample", spots[:1])
                    if sample:
                        first = sample[0]
                        # Automatisch erkanntes Dauer-Feld anzeigen
                        dur_key = _detect_duration_key(first)
                        if dur_key:
                            raw_val = first.get(dur_key)
                            dur_sec = _read_gf_duration(first)
                            st.success(f"✅ Erkanntes Dauer-Feld: **`{dur_key}`** = {raw_val} → **{dur_sec} s**")
                        else:
                            st.error("❌ Kein Dauer-Feld erkannt! Bitte unten numerische Felder prüfen.")

                        # Alle numerischen Felder anzeigen
                        num_fields = _get_numeric_fields(first)
                        if num_fields:
                            st.caption("**Alle numerischen Felder dieses Spots:**")
                            st.dataframe(pd.DataFrame(num_fields), use_container_width=True, hide_index=True)

                        # Override-Möglichkeit
                        st.caption("---")
                        st.caption("**Manueller Override** (falls die Erkennung falsch ist):")
                        override = st.text_input("Feldname für Dauer erzwingen",
                                                  value=gf_cfg.get("dur_field_override",""),
                                                  placeholder=f"z.B. {dur_key or 'Duration'}",
                                                  key="dur_override_input")
                        if st.button("Override speichern", key="btn_dur_override"):
                            gf_cfg["dur_field_override"] = override.strip()
                            save_data()
                            st.success(f"Gespeichert: Dauer-Feld = '{override.strip() or 'auto'}'")
                            st.rerun()

                        st.caption("---")
                        st.caption("**Vollständige Rohstruktur:**")
                        st.json(first)

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
                        idur  = _read_gf_duration(item, gf_cfg.get("dur_field_override") or None)
                        cn, ct, cs = st.columns([3, 2, 2])
                        cn.caption(f"**{iname[:28]}**\n{idur} s | ID {iid}")
                        cls_val = ct.selectbox(
                            "Typ", ["Ignorieren", "S", "M", "L", "XL", "Verein (Puffer)"],
                            key=f"cls_{c_i}_{iid}"
                        )
                        spon_val = cs.text_input(
                            "Sponsor-Label",
                            placeholder="z.B. Allianz",
                            key=f"spon_{c_i}_{iid}"
                        )
                        st.session_state["gf_cls"][iid] = {
                            "name": iname, "duration": idur,
                            "type": cls_val, "gf_id": iid,
                            "sponsor": spon_val.strip()
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
                            sponsor_val = cd.get("sponsor") or cd["type"]
                            tev["spots"].append({
                                "id":      cd["gf_id"],
                                "Name":    cd["name"],
                                "Dauer":   int(cd["duration"]),
                                "Typ":     cd["type"],
                                "Sponsor": sponsor_val,
                            })
                            added += 1
                        save_data()
                        st.session_state.pop("gf_cls", None)  # Formular zurücksetzen
                        st.rerun()

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

                    st.divider()
                    st.markdown("#### 📅 Neue Playlist-Version")
                    st.caption(
                        "In Grassfish wird eine **neue Version** der Playlist erstellt – "
                        "die bisherige bleibt erhalten und ist jederzeit nachvollziehbar."
                    )

                    import datetime as _dt
                    col_d, col_t = st.columns(2)
                    valid_date = col_d.date_input(
                        "Gültig ab – Datum",
                        value=_dt.date.today(),
                        key="push_valid_date"
                    )
                    valid_time = col_t.time_input(
                        "Gültig ab – Uhrzeit",
                        value=_dt.time(0, 0),
                        key="push_valid_time",
                        step=300,   # 5-Min-Schritte
                    )
                    valid_from_iso = _dt.datetime.combine(valid_date, valid_time).strftime("%Y-%m-%dT%H:%M:%S")
                    st.caption(f"ValidFrom: `{valid_from_iso}`")

                    if st.button("🚀 Neue Version erstellen & übertragen", type="primary"):
                        _key = gf_cfg.get("api_key", "")
                        _ver = st.session_state.get("gf_pl_version", gf_cfg.get("version", "1.19"))
                        if not _key:
                            st.warning("Bitte zuerst API-Key eingeben und Verbindung testen.")
                        else:
                            spot_ids = res_push["id"].tolist()
                            push_log = []
                            try:
                                ver_map    = st.session_state.get("gf_pl_ver_map", {})
                                version_id = ver_map.get(str(sel_pl_id), sel_pl_id)

                                with st.spinner("Schritt 1/2 – Neue Playlist-Version erstellen …"):
                                    new_vid, create_url, create_log = gf_create_playlist_version(
                                        gf_url, _key, _ver, sel_pl_id, valid_from_iso
                                    )
                                    push_log += create_log

                                if new_vid:
                                    st.info(f"✅ Neue Version erstellt (ID: `{new_vid}`) via `{create_url}`")
                                    use_vid = new_vid
                                else:
                                    st.warning(
                                        "⚠️ Neue Version konnte nicht automatisch erstellt werden. "
                                        "Versuche, direkt in die aktive Version zu schreiben …"
                                    )
                                    use_vid = version_id

                                # Dauer je Spot (id→sekunden) mitgeben
                                spot_dur_map = {}
                                if "id" in res_push.columns and "Dauer" in res_push.columns:
                                    for _, row in res_push.iterrows():
                                        spot_dur_map[str(row["id"])] = int(row["Dauer"])

                                with st.spinner(f"Schritt 2/2 – {len(spot_ids)} Spots übertragen …"):
                                    ok_p, url_p, log_p = gf_push_playlist(
                                        gf_url, _key, _ver, sel_pl_id, spot_ids,
                                        version_id=use_vid, spot_durations=spot_dur_map
                                    )
                                    push_log += log_p

                                if ok_p:
                                    st.success(f"✅ {len(spot_ids)} Spots übertragen via `{url_p}`")
                                    st.balloons()
                                else:
                                    st.error("❌ Kein funktionierender Push-Endpunkt gefunden.")

                                with st.expander("🔍 Debug: alle API-Aufrufe"):
                                    for entry in push_log:
                                        url_e    = entry[0]
                                        status_e = entry[1]
                                        body_e   = entry[2] if len(entry) > 2 else ""
                                        icon = "✅" if str(status_e) in ("200","201","204") else (
                                               "ℹ️" if str(status_e) == "0" else "❌")
                                        st.caption(f"{icon} `{status_e}` → {url_e}")
                                        if body_e:
                                            st.caption(f"   Body: `{body_e}`")
                            except Exception as e:
                                st.error(f"Fehler: {e}")
                                with st.expander("🔍 Debug"):
                                    for entry in push_log:
                                        st.caption(str(entry))
