import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import requests

API_BASE = "https://2gi0kne1gd.execute-api.us-east-1.amazonaws.com/prod"

app = dash.Dash(__name__, title="The Valorant Gazette")

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link href="https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=IM+Fell+English:ital@0;1&family=Courier+Prime:wght@400;700&family=Caveat:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --ink:       #1a1008;
            --parchment: #f2ead5;
            --aged:      #e8dfc4;
            --aged2:     #dfd5b8;
            --rule:      #8a7a5a;
            --faded:     #b0a080;
            --accent:    #c0351a;
            --win:       #2a6e3f;
            --loss:      #c0351a;
            --stain:     rgba(139, 109, 56, 0.07);
        }

        html { scroll-behavior: smooth; }

        /* ── Deep parchment background ── */
        body {
            background-color: var(--parchment);
            color: var(--ink);
            font-family: 'IM Fell English', serif;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }

        /* Paper grain overlay */
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            background-image:
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.08'/%3E%3C/svg%3E"),
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='6' height='6'%3E%3Crect width='6' height='6' fill='%23f2ead5'/%3E%3Crect x='0' y='0' width='1' height='1' fill='%23c8b888' opacity='0.18'/%3E%3Crect x='3' y='3' width='1' height='1' fill='%23a89868' opacity='0.1'/%3E%3Crect x='2' y='5' width='2' height='1' fill='%23d4c090' opacity='0.12'/%3E%3C/svg%3E");
        }

        /* Coffee stain rings */
        body::after {
            content: '';
            position: fixed;
            top: 120px;
            right: 60px;
            width: 160px;
            height: 160px;
            border-radius: 50%;
            border: 18px solid rgba(139, 100, 40, 0.06);
            box-shadow:
                0 0 0 4px rgba(139, 100, 40, 0.04),
                0 0 0 8px rgba(139, 100, 40, 0.02);
            pointer-events: none;
            z-index: 0;
        }

        /* ── Decorative weapon SVGs ── */
        .weapon-deco {
            position: absolute;
            opacity: 0.12;
            pointer-events: none;
            z-index: 1;
        }
        .weapon-deco svg { display: block; }

        /* ── Masthead ── */
        .masthead {
            position: sticky;
            top: 0;
            z-index: 100;
            background: var(--aged);
            border-bottom: 4px double var(--ink);
            padding: 14px 40px 10px;
            text-align: center;
            box-shadow: 0 3px 12px rgba(26,16,8,0.15);
        }
        .masthead::before {
            content: '';
            position: absolute;
            inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='4' height='4'%3E%3Crect width='4' height='4' fill='%23e8dfc4'/%3E%3Crect x='0' y='0' width='1' height='1' fill='%23c0aa80' opacity='0.2'/%3E%3C/svg%3E");
            pointer-events: none;
        }
        .masthead-rule-top {
            position: relative;
            border-top: 1px solid var(--ink);
            border-bottom: 1px solid var(--ink);
            padding: 3px 0;
            margin-bottom: 6px;
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            letter-spacing: 2px;
            color: var(--rule);
            display: flex;
            justify-content: space-between;
        }
        .masthead-title {
            position: relative;
            font-family: 'UnifrakturMaguntia', cursive;
            font-size: 58px;
            line-height: 1;
            color: var(--ink);
            letter-spacing: 1px;
            margin: 4px 0 2px;
            text-shadow: 2px 2px 0 rgba(26,16,8,0.08);
        }
        .masthead-sub {
            position: relative;
            font-family: 'IM Fell English', serif;
            font-style: italic;
            font-size: 12px;
            color: var(--rule);
            letter-spacing: 0.5px;
        }
        .masthead-rule-bot {
            position: relative;
            border-top: 2px solid var(--ink);
            margin-top: 8px;
        }

        /* ── Ticker ── */
        .ticker-wrap {
            background: var(--ink);
            overflow: hidden;
            padding: 6px 0;
            position: relative;
            z-index: 2;
        }
        .ticker-inner {
            display: flex;
            gap: 60px;
            white-space: nowrap;
            animation: ticker 28s linear infinite;
        }
        .ticker-item {
            font-family: 'Playfair Display', serif;
            font-size: 13px;
            font-weight: 700;
            color: var(--parchment);
            flex-shrink: 0;
        }
        .ticker-item em {
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            color: var(--accent);
            letter-spacing: 2px;
            font-style: normal;
            margin-right: 8px;
        }
        @keyframes ticker {
            0%   { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        /* ── Page wrapper ── */
        .page-wrap {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 40px 120px;
            position: relative;
            z-index: 2;
        }

        /* ── Dateline ── */
        .dateline {
            display: flex;
            justify-content: space-between;
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            letter-spacing: 1.5px;
            color: var(--rule);
            padding-bottom: 8px;
            border-bottom: 1px solid var(--rule);
            margin-bottom: 50px;
        }

        /* ── Sections: messy, rotated ── */
        .section {
            position: relative;
            padding: 24px 0 48px;
            opacity: 0;
            transform: translateY(28px);
            transition: opacity 0.7s ease, transform 0.7s ease;
        }
        .section.visible { opacity: 1; transform: translateY(0); }
        .section.faded   { opacity: 0.06; transform: translateY(-20px); }

        /* Tilted ink-stamp look for section labels */
        .section-label {
            font-family: 'Courier Prime', monospace;
            font-size: 8px;
            letter-spacing: 3px;
            color: var(--accent);
            text-transform: uppercase;
            margin-bottom: 6px;
            transform: rotate(-0.8deg);
            display: inline-block;
            border: 1px solid var(--accent);
            padding: 2px 8px;
            opacity: 0.75;
        }

        /* Torn-edge divider effect */
        .torn {
            width: 100%;
            height: 24px;
            margin: 20px 0;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 24' preserveAspectRatio='none'%3E%3Cpath d='M0,12 Q20,4 40,14 Q60,22 80,10 Q100,2 120,15 Q140,24 160,8 Q180,0 200,12 Q220,20 240,7 Q260,0 280,13 Q300,22 320,9 Q340,2 360,14 Q380,22 400,8 Q420,0 440,13 Q460,21 480,9 Q500,3 520,15 Q540,23 560,10 Q580,2 600,14 Q620,22 640,8 Q660,0 680,13 Q700,21 720,9 Q740,3 760,15 Q780,23 800,10 Q820,2 840,14 Q860,22 880,9 Q895,4 900,12 L900,24 L0,24 Z' fill='%23e8dfc4' opacity='0.5'/%3E%3C/svg%3E");
            background-size: 900px 24px;
            background-repeat: no-repeat;
            pointer-events: none;
        }

        /* ── Search section ── */
        .search-block {
            position: relative;
            background: var(--aged);
            padding: 30px 34px 28px;
            transform: rotate(-0.4deg);
            box-shadow:
                4px 5px 0 rgba(26,16,8,0.08),
                -1px 2px 0 rgba(26,16,8,0.04);
            border-top: 3px solid var(--ink);
        }
        .search-block::after {
            content: '';
            position: absolute;
            inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='3' height='3'%3E%3Crect width='3' height='3' fill='%23e8dfc4'/%3E%3Crect x='0' y='0' width='1' height='1' fill='%23b0a070' opacity='0.1'/%3E%3C/svg%3E");
            pointer-events: none;
        }
        .search-headline {
            font-family: 'Playfair Display', serif;
            font-size: 28px;
            font-weight: 900;
            font-style: italic;
            color: var(--ink);
            border-bottom: 2px solid var(--ink);
            padding-bottom: 8px;
            margin-bottom: 6px;
            position: relative;
        }
        .search-deck {
            font-family: 'IM Fell English', serif;
            font-style: italic;
            font-size: 13px;
            color: var(--rule);
            margin-bottom: 20px;
            position: relative;
        }
        .search-row {
            display: flex;
            gap: 14px;
            align-items: flex-end;
            flex-wrap: wrap;
            position: relative;
        }
        .input-col { display: flex; flex-direction: column; gap: 5px; }
        .input-col.name { flex: 2; min-width: 200px; }
        .input-col.tag  { flex: 1; min-width: 130px; }
        .field-label {
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            letter-spacing: 2px;
            color: var(--rule);
            text-transform: uppercase;
        }
        input[type="text"] {
            background: var(--parchment) !important;
            border: none !important;
            border-bottom: 2px solid var(--ink) !important;
            padding: 8px 4px !important;
            font-family: 'Courier Prime', monospace !important;
            font-size: 13px !important;
            color: var(--ink) !important;
            outline: none !important;
            border-radius: 0 !important;
            width: 100% !important;
            background-color: transparent !important;
        }
        input[type="text"]::placeholder { color: var(--faded) !important; }
        input[type="text"]:focus { border-bottom-color: var(--accent) !important; }
        .search-btn {
            padding: 9px 26px;
            background: var(--ink);
            color: var(--parchment);
            border: none;
            border-radius: 0;
            font-family: 'Courier Prime', monospace;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            cursor: pointer;
            align-self: flex-end;
            margin-bottom: 1px;
            transition: background 0.15s;
            position: relative;
        }
        .search-btn:hover { background: var(--accent); }
        .error-msg {
            font-family: 'Courier Prime', monospace;
            font-size: 11px;
            color: var(--accent);
            margin-top: 10px;
            letter-spacing: 1px;
            min-height: 16px;
            position: relative;
        }

        /* Handwritten margin note */
        .margin-note {
            position: absolute;
            font-family: 'Caveat', cursive;
            font-size: 15px;
            color: var(--accent);
            opacity: 0.65;
            pointer-events: none;
            line-height: 1.3;
        }

        /* ── Stat cards ── */
        .stat-headline {
            font-family: 'Playfair Display', serif;
            font-size: 30px;
            font-weight: 900;
            font-style: italic;
            color: var(--ink);
            border-bottom: 2px solid var(--ink);
            padding-bottom: 10px;
            margin-bottom: 4px;
        }
        .stat-byline {
            font-family: 'Courier Prime', monospace;
            font-size: 8px;
            letter-spacing: 3px;
            color: var(--rule);
            margin-bottom: 24px;
        }
        .stat-columns {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0;
        }
        .stat-col {
            padding: 18px 16px;
            text-align: center;
            border-right: 1px dashed var(--faded);
            position: relative;
        }
        .stat-col:last-child { border-right: none; }
        .stat-label {
            font-family: 'Courier Prime', monospace;
            font-size: 8px;
            letter-spacing: 2px;
            color: var(--rule);
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .stat-value {
            font-family: 'Playfair Display', serif;
            font-size: 42px;
            font-weight: 900;
            color: var(--ink);
            line-height: 1;
        }
        .stat-value .unit {
            font-size: 18px;
            color: var(--rule);
            font-weight: 700;
        }
        .stat-sub {
            font-family: 'IM Fell English', serif;
            font-style: italic;
            font-size: 11px;
            color: var(--rule);
            margin-top: 5px;
        }

        /* ── Chart sections: borderless, on parchment ── */
        .chart-block {
            position: relative;
            padding: 10px 0 10px;
        }
        /* Some sections tilted slightly */
        .chart-block.tilt-left  { transform: rotate(-0.5deg); }
        .chart-block.tilt-right { transform: rotate(0.6deg); }

        .chart-headline {
            font-family: 'Playfair Display', serif;
            font-size: 22px;
            font-weight: 700;
            font-style: italic;
            color: var(--ink);
            border-bottom: 1px solid var(--ink);
            padding-bottom: 5px;
            margin-bottom: 4px;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }
        .chart-deck {
            font-family: 'IM Fell English', serif;
            font-style: italic;
            font-size: 12px;
            color: var(--rule);
            margin-bottom: 6px;
        }
        /* Hand-ruled lines above chart */
        .ruled-lines {
            width: 100%;
            height: 8px;
            background-image: repeating-linear-gradient(
                transparent 0px, transparent 5px,
                rgba(138, 122, 90, 0.2) 5px, rgba(138, 122, 90, 0.2) 6px
            );
            margin-bottom: 4px;
        }

        /* ── Ink blot decoration ── */
        .ink-blot {
            position: absolute;
            border-radius: 50%;
            background: rgba(26, 16, 8, 0.05);
            pointer-events: none;
        }

        /* ── Column rule for two-col layout ── */
        .two-col {
            display: grid;
            grid-template-columns: 1fr 2px 1fr;
            gap: 0 20px;
            margin: 10px 0;
        }
        .col-rule {
            background: repeating-linear-gradient(
                to bottom,
                var(--rule) 0, var(--rule) 4px,
                transparent 4px, transparent 8px
            );
            width: 1px;
            margin: 0 auto;
        }

        /* ── Stamp ── */
        .stamp {
            display: inline-block;
            font-family: 'Courier Prime', monospace;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 3px;
            color: var(--accent);
            border: 2px solid var(--accent);
            padding: 4px 10px;
            transform: rotate(-5deg);
            opacity: 0.55;
            text-transform: uppercase;
            position: absolute;
        }

        /* ── Progress dots ── */
        .progress-rail {
            position: fixed;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 200;
        }
        .progress-dot {
            width: 6px;
            height: 6px;
            border: 1px solid var(--rule);
            border-radius: 50%;
            background: transparent;
            cursor: pointer;
            transition: background 0.2s, border-color 0.2s;
        }
        .progress-dot.active {
            background: var(--ink);
            border-color: var(--ink);
        }

        /* ── Ornament dividers ── */
        .ornament {
            text-align: center;
            font-family: 'IM Fell English', serif;
            color: var(--faded);
            font-size: 16px;
            letter-spacing: 10px;
            padding: 16px 0 8px;
            opacity: 0.7;
        }

        /* Horizontal rule with center diamond */
        .hr-diamond {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 12px 0;
            color: var(--faded);
        }
        .hr-diamond::before, .hr-diamond::after {
            content: '';
            flex: 1;
            height: 1px;
            background: var(--rule);
            opacity: 0.5;
        }
        .hr-diamond span {
            font-size: 10px;
            transform: rotate(45deg);
            display: inline-block;
            color: var(--rule);
        }

        /* ── Awaiting dispatch ── */
        .awaiting {
            text-align: center;
            font-family: 'Courier Prime', monospace;
            font-size: 11px;
            letter-spacing: 2px;
            color: var(--rule);
            padding: 40px 0;
        }
    </style>
</head>
<body>

<!-- ── Weapon decorations scattered on background ── -->

<!-- Vandal rifle, top right area -->
<div class="weapon-deco" style="top: 280px; right: -20px; transform: rotate(-18deg);">
  <svg width="320" height="90" viewBox="0 0 320 90" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- Vandal-style assault rifle silhouette -->
    <g fill="#1a1008">
      <!-- Stock -->
      <rect x="0" y="35" width="60" height="16" rx="3"/>
      <rect x="5" y="28" width="18" height="8" rx="2"/>
      <!-- Body -->
      <rect x="55" y="28" width="130" height="30" rx="4"/>
      <!-- Grip -->
      <rect x="95" y="56" width="22" height="28" rx="3"/>
      <!-- Trigger guard -->
      <path d="M95 58 Q107 68 119 58" stroke="#1a1008" stroke-width="3" fill="none"/>
      <!-- Magazine -->
      <rect x="108" y="58" width="14" height="22" rx="2"/>
      <!-- Upper receiver / scope rail -->
      <rect x="60" y="22" width="100" height="8" rx="2"/>
      <!-- Barrel -->
      <rect x="183" y="34" width="100" height="10" rx="5"/>
      <!-- Muzzle device -->
      <rect x="278" y="30" width="14" height="18" rx="3"/>
      <line x1="281" y1="26" x2="281" y2="22" stroke="#1a1008" stroke-width="2.5"/>
      <line x1="287" y1="26" x2="287" y2="22" stroke="#1a1008" stroke-width="2.5"/>
      <line x1="284" y1="25" x2="291" y2="22" stroke="#1a1008" stroke-width="2"/>
      <!-- Handguard lines -->
      <line x1="68" y1="28" x2="68" y2="58" stroke="#f2ead5" stroke-width="1.5"/>
      <line x1="80" y1="28" x2="80" y2="58" stroke="#f2ead5" stroke-width="1.5"/>
      <line x1="92" y1="28" x2="92" y2="58" stroke="#f2ead5" stroke-width="1.5"/>
      <!-- Sight -->
      <rect x="130" y="18" width="28" height="12" rx="2"/>
      <circle cx="144" cy="24" r="4" fill="#f2ead5"/>
      <circle cx="144" cy="24" r="1.5" fill="#1a1008"/>
    </g>
  </svg>
</div>

<!-- Operator sniper rifle, left side lower -->
<div class="weapon-deco" style="top: 900px; left: -30px; transform: rotate(12deg);">
  <svg width="400" height="80" viewBox="0 0 400 80" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g fill="#1a1008">
      <!-- Stock -->
      <path d="M0 30 L55 30 L60 22 L75 22 L75 55 L60 55 L55 48 L0 48 Z"/>
      <!-- Cheek rest -->
      <rect x="8" y="22" width="35" height="8" rx="2"/>
      <!-- Body -->
      <rect x="70" y="24" width="200" height="30" rx="4"/>
      <!-- Scope mount -->
      <rect x="100" y="14" width="120" height="14" rx="3"/>
      <!-- Scope tube -->
      <rect x="90" y="10" width="140" height="12" rx="6"/>
      <!-- Scope lens rings -->
      <circle cx="97" cy="16" r="6" fill="#f2ead5" stroke="#1a1008" stroke-width="2"/>
      <circle cx="97" cy="16" r="3" fill="#1a1008"/>
      <circle cx="222" cy="16" r="7" fill="#f2ead5" stroke="#1a1008" stroke-width="2"/>
      <circle cx="222" cy="16" r="3.5" fill="#1a1008"/>
      <!-- Grip -->
      <rect x="148" y="52" width="24" height="24" rx="3"/>
      <!-- Trigger guard -->
      <path d="M148 56 Q160 68 172 56" stroke="#1a1008" stroke-width="3" fill="none"/>
      <!-- Bipod legs -->
      <line x1="115" y1="54" x2="105" y2="74" stroke="#1a1008" stroke-width="4" stroke-linecap="round"/>
      <line x1="135" y1="54" x2="145" y2="74" stroke="#1a1008" stroke-width="4" stroke-linecap="round"/>
      <line x1="100" y1="72" x2="110" y2="72" stroke="#1a1008" stroke-width="3" stroke-linecap="round"/>
      <line x1="140" y1="72" x2="150" y2="72" stroke="#1a1008" stroke-width="3" stroke-linecap="round"/>
      <!-- Barrel -->
      <rect x="268" y="32" width="118" height="12" rx="6"/>
      <!-- Muzzle brake -->
      <rect x="376" y="28" width="16" height="20" rx="2"/>
      <line x1="378" y1="24" x2="378" y2="20" stroke="#1a1008" stroke-width="2"/>
      <line x1="384" y1="24" x2="384" y2="20" stroke="#1a1008" stroke-width="2"/>
      <line x1="390" y1="24" x2="390" y2="20" stroke="#1a1008" stroke-width="2"/>
    </g>
  </svg>
</div>

<!-- Phantom, rotated on right mid -->
<div class="weapon-deco" style="top: 1600px; right: -10px; transform: rotate(-8deg);">
  <svg width="290" height="80" viewBox="0 0 290 80" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g fill="#1a1008">
      <!-- Stock (folded compact style) -->
      <rect x="0" y="32" width="45" height="14" rx="3"/>
      <rect x="40" y="24" width="15" height="10" rx="2"/>
      <!-- Receiver -->
      <rect x="50" y="22" width="120" height="32" rx="4"/>
      <!-- Top rail -->
      <rect x="54" y="16" width="95" height="8" rx="2"/>
      <!-- Suppressor (Phantom has integrated barrel) -->
      <rect x="168" y="28" width="90" height="14" rx="7"/>
      <!-- Suppressor vents -->
      <line x1="188" y1="28" x2="188" y2="42" stroke="#f2ead5" stroke-width="1.5"/>
      <line x1="202" y1="28" x2="202" y2="42" stroke="#f2ead5" stroke-width="1.5"/>
      <line x1="216" y1="28" x2="216" y2="42" stroke="#f2ead5" stroke-width="1.5"/>
      <line x1="230" y1="28" x2="230" y2="42" stroke="#f2ead5" stroke-width="1.5"/>
      <!-- Grip -->
      <rect x="88" y="52" width="20" height="24" rx="3"/>
      <!-- Mag -->
      <rect x="98" y="54" width="12" height="20" rx="2"/>
      <!-- Trigger guard -->
      <path d="M88 56 Q98 66 108 56" stroke="#1a1008" stroke-width="2.5" fill="none"/>
      <!-- Charging handle notch -->
      <rect x="155" y="20" width="8" height="6" rx="1"/>
      <!-- Iron sight front -->
      <rect x="148" y="12" width="4" height="6" rx="1"/>
      <!-- Iron sight rear -->
      <rect x="62" y="12" width="10" height="6" rx="1"/>
      <line x1="65" y1="12" x2="65" y2="8" stroke="#1a1008" stroke-width="2"/>
      <line x1="70" y1="12" x2="70" y2="8" stroke="#1a1008" stroke-width="2"/>
    </g>
  </svg>
</div>

<!-- Classic pistol, small, scattered bottom-left -->
<div class="weapon-deco" style="bottom: 300px; left: 20px; transform: rotate(20deg);">
  <svg width="130" height="100" viewBox="0 0 130 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g fill="#1a1008">
      <!-- Slide -->
      <rect x="20" y="18" width="90" height="22" rx="4"/>
      <!-- Frame -->
      <rect x="20" y="38" width="60" height="18" rx="3"/>
      <!-- Grip -->
      <rect x="22" y="54" width="28" height="38" rx="4"/>
      <!-- Grip texture lines -->
      <line x1="26" y1="58" x2="26" y2="86" stroke="#f2ead5" stroke-width="1.5"/>
      <line x1="32" y1="58" x2="32" y2="86" stroke="#f2ead5" stroke-width="1.5"/>
      <line x1="38" y1="58" x2="38" y2="86" stroke="#f2ead5" stroke-width="1.5"/>
      <line x1="44" y1="58" x2="44" y2="86" stroke="#f2ead5" stroke-width="1.5"/>
      <!-- Trigger guard -->
      <path d="M46 50 Q60 64 78 50" stroke="#1a1008" stroke-width="3" fill="none"/>
      <!-- Trigger -->
      <rect x="55" y="46" width="7" height="14" rx="2"/>
      <!-- Barrel -->
      <rect x="78" y="22" width="40" height="10" rx="5"/>
      <!-- Sight -->
      <rect x="90" y="14" width="10" height="6" rx="1"/>
      <rect x="28" y="14" width="12" height="6" rx="1"/>
      <!-- Mag base -->
      <rect x="22" y="88" width="28" height="5" rx="2"/>
    </g>
  </svg>
</div>

<!-- Knife / melee, top left -->
<div class="weapon-deco" style="top: 500px; left: 10px; transform: rotate(-30deg);">
  <svg width="80" height="200" viewBox="0 0 80 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g fill="#1a1008">
      <!-- Blade -->
      <path d="M35 0 L42 0 L44 130 L36 130 Z"/>
      <!-- Blade bevel -->
      <path d="M42 0 L44 130 L40 120 Z" fill="#8a7a5a" opacity="0.5"/>
      <!-- Guard -->
      <rect x="22" y="128" width="36" height="8" rx="3"/>
      <!-- Handle -->
      <rect x="28" y="134" width="24" height="58" rx="5"/>
      <!-- Handle wrapping lines -->
      <line x1="28" y1="142" x2="52" y2="142" stroke="#f2ead5" stroke-width="2"/>
      <line x1="28" y1="150" x2="52" y2="150" stroke="#f2ead5" stroke-width="2"/>
      <line x1="28" y1="158" x2="52" y2="158" stroke="#f2ead5" stroke-width="2"/>
      <line x1="28" y1="166" x2="52" y2="166" stroke="#f2ead5" stroke-width="2"/>
      <line x1="28" y1="174" x2="52" y2="174" stroke="#f2ead5" stroke-width="2"/>
      <!-- Pommel -->
      <ellipse cx="40" cy="193" rx="14" ry="7"/>
    </g>
  </svg>
</div>

<!-- Shorty / shotgun, lower right -->
<div class="weapon-deco" style="bottom: 500px; right: 5px; transform: rotate(15deg);">
  <svg width="180" height="100" viewBox="0 0 180 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g fill="#1a1008">
      <!-- Stock -->
      <rect x="0" y="28" width="50" height="18" rx="3"/>
      <rect x="5" y="20" width="20" height="10" rx="2"/>
      <!-- Receiver -->
      <rect x="45" y="20" width="80" height="32" rx="5"/>
      <!-- Pump handle -->
      <rect x="80" y="52" width="35" height="12" rx="4"/>
      <!-- Barrel set (two barrels) -->
      <rect x="122" y="22" width="50" height="8" rx="4"/>
      <rect x="122" y="34" width="50" height="8" rx="4"/>
      <!-- Grip -->
      <rect x="60" y="50" width="22" height="28" rx="4"/>
      <!-- Trigger guard -->
      <path d="M58 54 Q70 64 82 54" stroke="#1a1008" stroke-width="2.5" fill="none"/>
    </g>
  </svg>
</div>

<!-- Stinger SMG decoration -->
<div class="weapon-deco" style="top: 1200px; left: -15px; transform: rotate(8deg);">
  <svg width="200" height="70" viewBox="0 0 200 70" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g fill="#1a1008">
      <rect x="0" y="26" width="40" height="14" rx="3"/>
      <rect x="35" y="18" width="100" height="28" rx="5"/>
      <rect x="55" y="12" width="65" height="8" rx="2"/>
      <rect x="170" y="24" width="28" height="10" rx="5"/>
      <rect x="58" y="44" width="18" height="22" rx="3"/>
      <rect x="62" y="46" width="10" height="18" rx="2"/>
      <path d="M55 48 Q66 58 77 48" stroke="#1a1008" stroke-width="2" fill="none"/>
      <line x1="45" y1="18" x2="45" y2="46" stroke="#f2ead5" stroke-width="1.5"/>
      <line x1="55" y1="18" x2="55" y2="46" stroke="#f2ead5" stroke-width="1.5"/>
    </g>
  </svg>
</div>


    {%app_entry%}
    {%config%}
    {%scripts%}
    {%renderer%}
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        function updateSections() {
            const sections = document.querySelectorAll(".section");
            const mid = window.innerHeight / 2;
            sections.forEach(function(sec) {
                const rect = sec.getBoundingClientRect();
                const center = rect.top + rect.height / 2;
                const dist = Math.abs(center - mid);
                const threshold = window.innerHeight * 0.42;
                sec.classList.remove("visible", "faded");
                if (dist < threshold) {
                    sec.classList.add("visible");
                } else if (rect.bottom < mid) {
                    sec.classList.add("faded");
                }
            });
            const dots = document.querySelectorAll(".progress-dot");
            let closest = 0, minDist = Infinity;
            sections.forEach(function(sec, i) {
                const rect = sec.getBoundingClientRect();
                const center = rect.top + rect.height / 2;
                const dist = Math.abs(center - mid);
                if (dist < minDist) { minDist = dist; closest = i; }
            });
            dots.forEach(function(d, i) {
                d.classList.toggle("active", i === closest);
            });
        }
        window.addEventListener("scroll", updateSections, { passive: true });
        updateSections();
        document.querySelectorAll(".progress-dot").forEach(function(dot) {
            dot.addEventListener("click", function() {
                const i = parseInt(dot.getAttribute("data-index"), 10);
                const sections = document.querySelectorAll(".section");
                if (sections[i]) sections[i].scrollIntoView({ behavior: "smooth", block: "center" });
            });
        });
    });
    </script>
</body>
</html>
'''

# ── Layout ─────────────────────────────────────────────────────────────────

TICKER_ITEMS = [
    ("BREAKING", "Radiant tier fracas erupts on Ascent — full coverage inside"),
    ("REPORT",   "Jett usage falls for third consecutive act"),
    ("ANALYSIS", "Headshot percentages at historic low this episode"),
    ("DISPATCH", "New operator found dominant on long-range sightlines"),
    ("BULLETIN", "Chamber rework draws ire of professional circuit"),
]

def ticker_html():
    items = [
        html.Span([html.Em(label), text], className="ticker-item")
        for label, text in TICKER_ITEMS * 2
    ]
    return html.Div(className="ticker-wrap", children=[
        html.Div(items, className="ticker-inner")
    ])

app.layout = html.Div(children=[

    html.Div(className="masthead", children=[
        html.Div(className="masthead-rule-top", children=[
            html.Span("EST. PATCH 10.03"),
            html.Span("★  OFFICIAL RECORD  ★"),
            html.Span("FIVE ROUNDS OR BUST"),
        ]),
        html.Div("The Valorant Gazette", className="masthead-title"),
        html.Div("All The Frags Fit To Print — Competitive Intelligence Since Episode I", className="masthead-sub"),
        html.Div(className="masthead-rule-bot"),
    ]),

    ticker_html(),

    html.Div(className="progress-rail", children=[
        html.Div(id=f"dot-{i}", className="progress-dot", **{"data-index": str(i)})
        for i in range(6)
    ]),

    html.Div(className="page-wrap", children=[

        html.Div(className="dateline", children=[
            html.Span("COMPETITIVE DIVISION — UNRANKED TO RADIANT"),
            html.Span("ALL QUEUES · ALL MAPS"),
        ]),

        # ── Section 0: Search ───────────────────────
        html.Div(className="section", children=[
            html.Div(className="section-label", children="Intelligence Bureau — Player Registry"),
            html.Div(className="search-block", children=[
                # Margin annotation
                html.Div("look up\nyour guy →", className="margin-note",
                         style={"top": "-38px", "right": "10px", "transform": "rotate(-4deg)"}),
                html.Div("Field Correspondent Lookup", className="search-headline"),
                html.Div("Enter a Riot ID to retrieve the operative's full combat dossier.",
                         className="search-deck"),
                html.Div(className="search-row", children=[
                    html.Div(className="input-col name", children=[
                        html.Label("Agent Designation (Riot Name)", className="field-label"),
                        dcc.Input(id="name-input", type="text", placeholder="bananabrigade"),
                    ]),
                    html.Div(className="input-col tag", children=[
                        html.Label("Regiment Tag", className="field-label"),
                        dcc.Input(id="tag-input", type="text", placeholder="banan"),
                    ]),
                    html.Button("— Dispatch —", id="search-btn", n_clicks=0, className="search-btn"),
                ]),
                html.Div(id="error-msg", className="error-msg"),
            ]),
        ]),

        html.Div(className="ornament", children="✦  ✦  ✦"),

        # ── Section 1: Stat cards ───────────────────
        html.Div(className="section", children=[
            html.Div(className="section-label", children="Combat Record — Summary Dispatch"),
            html.Div(id="stat-cards-section", children=[
                html.Div("Awaiting dispatch…", className="awaiting")
            ]),
        ]),

        html.Div(className="ornament", children="— ◆ —"),

        # ── Section 2: K/D trend ────────────────────
        html.Div(className="section", children=[
            html.Div(className="section-label", children="Frontline Report — Kill/Death"),
            html.Div(className="chart-block tilt-left", children=[
                # Handwritten margin note
                html.Div("trending\ndown?!", className="margin-note",
                         style={"top": "60px", "right": "-10px", "transform": "rotate(5deg)", "fontSize": "14px"}),
                html.Div(className="chart-headline", children=[
                    html.Span("K/D Ratio — Recent Dispatches"),
                    html.Span("PER MATCH", style={"fontFamily": "'Courier Prime', monospace",
                                                   "fontSize": "9px", "letterSpacing": "2px", "color": "#8a7a5a"}),
                ]),
                html.Div("Green markers denote victories; red, defeats. Dashed line marks campaign average.",
                         className="chart-deck"),
                html.Div(className="ruled-lines"),
                dcc.Graph(id="kd-trend-chart", config={"displayModeBar": False}),
            ]),
        ]),

        html.Div(className="ornament", children="✦  ✦  ✦"),

        # ── Section 3: HS% trend ────────────────────
        html.Div(className="section", children=[
            html.Div(className="section-label", children="Marksman's Log — Headshot Analysis"),
            html.Div(className="chart-block tilt-right", children=[
                html.Div(className="chart-headline", children=[
                    html.Span("Headshot % — Field Reports"),
                    html.Span("PER MATCH", style={"fontFamily": "'Courier Prime', monospace",
                                                   "fontSize": "9px", "letterSpacing": "2px", "color": "#8a7a5a"}),
                ]),
                html.Div("Precision indexed per engagement. A steady hand separates the correspondent from the combatant.",
                         className="chart-deck"),
                html.Div(className="ruled-lines"),
                dcc.Graph(id="hs-trend-chart", config={"displayModeBar": False}),
            ]),
        ]),

        html.Div(className="ornament", children="— ◆ —"),

        # ── Section 4 & 5: Two-column agent + map ──
        html.Div(className="section", children=[
            html.Div(className="section-label", children="Operative Profiles & Theatre of Operations"),
            # Stamp element
            html.Div("Classified", className="stamp", style={"top": "30px", "right": "40px"}),
            html.Div(className="two-col", children=[
                # Left: Agent win rates
                html.Div(children=[
                    html.Div(className="chart-headline", style={"fontSize": "18px"}, children=[
                        html.Span("Agent Win Rates"),
                    ]),
                    html.Div("Which operatives proved effective this campaign.",
                             className="chart-deck"),
                    html.Div(className="ruled-lines"),
                    dcc.Graph(id="agent-chart", config={"displayModeBar": False},
                              style={"height": "300px"}),
                ]),
                # Column rule
                html.Div(className="col-rule"),
                # Right: Map win rates
                html.Div(children=[
                    html.Div(className="chart-headline", style={"fontSize": "18px"}, children=[
                        html.Span("Map Win Rates"),
                    ]),
                    html.Div("Territorial dominance across all active combat zones.",
                             className="chart-deck"),
                    html.Div(className="ruled-lines"),
                    dcc.Graph(id="map-chart", config={"displayModeBar": False},
                              style={"height": "300px"}),
                ]),
            ]),
        ]),

    ]),

    dcc.Store(id="player-data", data=None),
])


# ── Fetch player data ───────────────────────────────────────────────────────

@app.callback(
    Output("player-data", "data"),
    Output("error-msg",   "children"),
    Input("search-btn",   "n_clicks"),
    State("name-input",   "value"),
    State("tag-input",    "value"),
    prevent_initial_call=True,
)
def fetch_player(n_clicks, game_name, tag_line):
    if not game_name or not tag_line:
        return None, "— Please enter both a name and tag. —"
    try:
        r = requests.get(f"{API_BASE}/player/{game_name.strip()}/{tag_line.strip()}")
        if r.status_code == 404:
            return None, r.json().get("detail", "Operative not found in the registry.")
        r.raise_for_status()
        return r.json(), ""
    except Exception as e:
        return None, f"Correspondent unreachable: {e}"


# ── Render all visuals ──────────────────────────────────────────────────────

@app.callback(
    Output("stat-cards-section", "children"),
    Output("kd-trend-chart",     "figure"),
    Output("hs-trend-chart",     "figure"),
    Output("agent-chart",        "figure"),
    Output("map-chart",          "figure"),
    Input("player-data",         "data"),
)
def render_visuals(player_data):
    # Parchment palette — charts now transparent on parchment
    BG       = "rgba(0,0,0,0)"   # fully transparent so charts sit on parchment
    PAPER    = "#f2ead5"
    INK      = "#1a1008"
    RULE     = "#8a7a5a"
    FADED    = "#c8bc9a"
    ACCENT   = "#c0351a"
    WIN_CLR  = "#2a6e3f"
    LOSS_CLR = "#c0351a"

    MONO = "Courier Prime, monospace"
    DISP = "Playfair Display, serif"

    def base_layout(**kwargs):
        return dict(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font={"color": INK, "family": MONO},
            height=300,
            margin={"t": 10, "b": 50, "l": 50, "r": 20},
            xaxis={
                "showgrid": False,
                "color": RULE,
                "linecolor": INK,
                "linewidth": 1.5,
                "tickfont": {"family": MONO, "size": 10},
                "zeroline": False,
            },
            yaxis={
                "gridcolor": FADED,
                "gridwidth": 0.5,
                "griddash": "dot",
                "color": RULE,
                "linecolor": "rgba(0,0,0,0)",
                "tickfont": {"family": MONO, "size": 10},
                "zeroline": False,
            },
            hoverlabel={"bgcolor": INK, "font_color": PAPER, "font_family": MONO, "font_size": 11},
            showlegend=False,
            **kwargs,
        )

    def empty_fig():
        f = go.Figure()
        f.update_layout(**base_layout())
        f.add_annotation(
            text="Awaiting dispatch…", x=0.5, y=0.5,
            xref="paper", yref="paper", showarrow=False,
            font={"family": MONO, "size": 12, "color": RULE},
        )
        return f

    if not player_data:
        return html.Div("Awaiting dispatch…", className="awaiting"), \
               empty_fig(), empty_fig(), empty_fig(), empty_fig()

    summary    = player_data["summary"]
    matches    = player_data["matches"]
    match_nums = list(range(1, len(matches) + 1))
    colors     = [WIN_CLR if m["won"] else LOSS_CLR for m in matches]

    # ── Stat cards ──────────────────────────────────
    def stat_col(label, value, unit="", sub=""):
        return html.Div(className="stat-col", children=[
            html.Div(label, className="stat-label"),
            html.Div([value, html.Span(unit, className="unit")], className="stat-value"),
            html.Div(sub, className="stat-sub"),
        ])

    stat_section = html.Div(children=[
        html.Div("Combat Dossier — Season Summary", className="stat-headline"),
        html.Div("✦  VERIFIED DISPATCH  ✦  ALL QUEUES  ✦  LAST 20 MATCHES  ✦",
                 className="stat-byline"),
        html.Div(className="stat-columns", children=[
            stat_col("Win Rate",        str(summary["win_rate"]),             "%",  "Of battles contested"),
            stat_col("Avg K/D",         str(summary["avg_kd"]),               "",   "Kills per death"),
            stat_col("Avg Headshot %",  str(summary["avg_hs_pct"]),           "%",  "Precision in the field"),
            stat_col("Avg DMG / Round", str(summary["avg_damage_per_round"]), "",   "Damage inflicted per round"),
        ]),
    ])

    # ── K/D trend ───────────────────────────────────
    kd_fig = go.Figure()
    kd_fig.add_trace(go.Scatter(
        x=match_nums,
        y=[m["kd_ratio"] for m in matches],
        mode="lines+markers",
        line={"color": INK, "width": 1.5},
        marker={"color": colors, "size": 9, "symbol": "circle",
                "line": {"width": 1.5, "color": PAPER}},
        customdata=[[m["damage_per_round"], m["rounds_played"]] for m in matches],
        hovertemplate=(
            "<b>Match %{x}</b><br>"
            "K/D: %{y}<br>"
            "DMG/R: %{customdata[0]}<br>"
            "Rounds: %{customdata[1]}"
            "<extra></extra>"
        ),
    ))
    kd_fig.add_hline(
        y=summary["avg_kd"], line_dash="dash", line_color=RULE, line_width=1,
        annotation_text=f"avg {summary['avg_kd']}",
        annotation_font={"color": RULE, "family": MONO, "size": 10},
    )
    kd_fig.update_layout(**base_layout(xaxis_title="Match #", yaxis_title="K/D Ratio"))

    # ── HS% trend ───────────────────────────────────
    hs_fig = go.Figure()
    hs_fig.add_trace(go.Scatter(
        x=match_nums,
        y=[m["hs_pct"] for m in matches],
        mode="lines+markers",
        line={"color": ACCENT, "width": 1.5},
        marker={"color": colors, "size": 9, "symbol": "circle",
                "line": {"width": 1.5, "color": PAPER}},
        hovertemplate="<b>Match %{x}</b><br>HS%%: %{y}%%<extra></extra>",
    ))
    hs_fig.add_hline(
        y=summary["avg_hs_pct"], line_dash="dash", line_color=RULE, line_width=1,
        annotation_text=f"avg {summary['avg_hs_pct']}%",
        annotation_font={"color": RULE, "family": MONO, "size": 10},
    )
    hs_fig.update_layout(**base_layout(xaxis_title="Match #", yaxis_title="Headshot %"))

    # ── Agent win rates ──────────────────────────────
    agent_fig = go.Figure(go.Bar(
        x=list(summary["agent_win_rates"].keys()),
        y=list(summary["agent_win_rates"].values()),
        marker_color=INK,
        marker_pattern_shape="/",
        marker_pattern_fgcolor=PAPER,
        marker_pattern_size=5,
        marker_line_color=INK,
        marker_line_width=1,
        hovertemplate="<b>%{x}</b><br>Win rate: %{y}%<extra></extra>",
    ))
    agent_fig.update_layout(
        **base_layout(xaxis_title="Agent", yaxis_title="Win Rate %", yaxis_range=[0, 100]),
        height=280,
    )

    # ── Map win rates ────────────────────────────────
    map_fig = go.Figure(go.Bar(
        x=list(summary["map_win_rates"].keys()),
        y=list(summary["map_win_rates"].values()),
        marker_color=ACCENT,
        marker_pattern_shape="\\",
        marker_pattern_fgcolor=PAPER,
        marker_pattern_size=5,
        marker_line_color=ACCENT,
        marker_line_width=1,
        hovertemplate="<b>%{x}</b><br>Win rate: %{y}%<extra></extra>",
    ))
    map_fig.update_layout(
        **base_layout(xaxis_title="Map", yaxis_title="Win Rate %", yaxis_range=[0, 100]),
        height=280,
    )

    return stat_section, kd_fig, hs_fig, agent_fig, map_fig


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)