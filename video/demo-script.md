# Demo script — BriefMinion (Cortensor Hackathon #5)

Video: `demo.mp4` — 80 detik, 1280×720, tanpa audio (narasi lewat kartu
judul). Semua cuplikan terminal adalah rekaman nyata `run_demo.py` yang
direkam 17 Nov 2026 dengan `script` (`demo.typescript` + `demo.timing`),
di-render ulang menjadi frame terminal agar bisa dibaca. Tidak ada teks
output yang dibuat-buat.

## Alur (durasi)

| Waktu | Isi |
|---|---|
| 0:00–0:07 | Kartu judul: BriefMinion — research-brief agent on OpenMinion 0.1 |
| 0:07–0:13 | Kartu tools: search_notes · read_note · save_brief · recall_briefs |
| 0:13–0:30 | Run 1: `Buatkan brief tentang Cortensor` → agen mencari catatan, membaca `notes/cortensor.md`, menyimpan `briefs/brief-cortensor-hackathon-5.md` |
| 0:30–0:40 | Run 2 (sesi sama, `demo-1`): `Brief apa saja yang sudah dibuat?` → agen mengingat brief dari sesi sebelumnya (durable session + memory di disk) |
| 0:40–1:05 | Isi brief yang tersimpan ditampilkan: Ringkasan, Fakta kunci, Sumber |
| 1:05–1:12 | Tes: 23 tes unit, hasil OK |
| 1:12–1:20 | Kartu hasil: brief tersimpan, recall bekerja, tes 23/23, repo, dan catatan model yang jujur |

## Catatan jujur yang tampil di video

Demo berjalan dengan **model stub deterministik lokal** (bukan model asli),
karena builder tidak punya kunci model. Kartu akhir video menyatakan ini
secara eksplisit, dan README menjelaskan cara ganti ke model asli: satu
edit config di `agents.json` (provider `cortensor-portal` / OpenAI-compatible
lainnya), tanpa perubahan kode.
