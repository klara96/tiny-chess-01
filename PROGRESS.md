# PROGRESS tiny-chess-01 (updated 2026-11-20 ~20:30 UTC+8)
## Selesai
- git init + 2 commit lokal: init stub; engine source+compressed entry (main.py 3955B <= 4096)
- Perft ALL PASS (6 posisi, d1-d4) pada engine source (entry_source.py)
- FIX BUG KRITIS #1: keyk() kehilangan side-to-move di hash (TT collision -> search delusi) -> diperbaiki + load() HK parity
- FIX BUG KRITIS #2: um() tidak restore KSQ/BSQ setelah king move -> search legalitas salah -> diperbaiki
- Practice trial 0 (sebelum fix): elo 0, 0/6 (semua checkmate, karena bug di atas)
## Sedang dikerjakan
- Practice trial ulang (trial-0, port 8907) SEDANG BERJALAN background (proc_bc81c74dc479, uptime ~15 menit);
  sinyal awal positif: draw + 1 win terlihat di run tersendat (tercampur proses bocor, sudah di-kill semua)
- Setelah hasil trial: commit+push, buat repo GitHub klara96/tiny-chess-01 (README badge), bundle, submit makefun
## Rencana berikutnya
- iterasi maks 4 round trial; target Elo >=1300, min 1154
- push GitHub + badge; bundle transcripts dari /root/.hermes-build/.hermes; submit via makefun.mjs
## Catatan
- main.py saat ini di repo = build SEBELUM fix (3955B) -> akan re-compress setelah fix dikonfirmasi trial
# UPDATE 2026-11-20T12:54:55Z: Elo 1099 (1W2D3L) pada trial fix#1+2. Iterasi round-2: QS_MAX 6->4, delta pruning qs, budget 150000. Perft ALL PASS, src 10265B. Trial round-2 launching.
# UPDATE 2026-11-20T13:12:24Z: round-2 (qs4+delta+150k) REGRESI 0/6 elo 0. Direvert ke search round-1 (qs6, no delta) + budget 350000. Perft PASS. Trial round-3 launching (proc baru).
# UPDATE 2026-11-20T13:39:09Z: round-3 (revert+350k): 2W4L, elo 1099 (menang checkmate depth-2&3). Round-4: history heuristic utk quiet ordering. src 10475B. Trial round-4 launching.
