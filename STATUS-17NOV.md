# BriefMinion — Status 17 Nov 2026 (13:17–13:30 WIB)

Cortensor Hackathon #5 (DoraHacks). Deadline: **19 Des 2026 14:59 WIB**.
Hadiah: **$1.150 COR** (juara 1 $500; tiap hadiah 50% liquid + 50%
staking lock 1 bulan). Repo publik: https://github.com/Shanumameyra/briefminion

## Hasil kerja hari ini (17 Nov 2026)

| # | Langkah | Hasil |
|---|---|---|
| 1 | Test suite | **23/23 lolos** (12,7 dtk), re-verified 17 Nov ~13:17 WIB. Repo sinkron: main, commit 63d6511, working tree bersih sebelum kerja; tidak ada commit tertinggal. |
| 2 | Cek repo target PR | **MASIH BELUM DIUMUMKAN** (cek 17 Nov ~13:17 WIB). Halaman DoraHacks (dorahacks.io/hackathon/2418/detail) + docs Cortensor (docs-v2.cortensor.network/ecosystem/hackathon-5/) masih tertulis "The repository URL will be added before kickoff" — padahal kickoff 16 Okt 2026. Org GitHub `cortensor` hanya punya 4 repo (installer, community-projects, salt, desktop-app); org `openminion` juga tidak punya repo hackathon-5 (dicek via GitHub API). Kandidat yang mungkin ditanyakan ke tim lewat Discord: `cortensor/community-projects` (deskripsinya "community hub for ecosystem apps") — tapi JANGAN ditebak sebagai target sebelum pengumuman resmi. |
| 3 | Video demo wajib 1–5 menit | **SELESAI — `demo.mp4`: 80,2 detik, 1280×720, h264, 620 KB.** Direkam dari sesi `run_demo.py` NYATA dengan `script` (output + timing asli), di-render jadi frame terminal agar terbaca; 6 frame dicek visual (kartu judul, replay agen, isi brief, kartu hasil) — semua terbaca, footer tidak menabrak teks. Naskah: `video/demo-script.md`. Video tanpa audio; kartu akhir menyatakan jujur demo memakai model stub lokal. |
| 4 | Paket submission | Draf deskripsi PR: `PR-DRAFT.md`. Checklist diperbarui: `SUBMISSION_CHECKLIST.md` (video + repo + deadline dicentang). Semua file baru di-commit + push ke `main` (lihat git log). |

## Yang masih BLOKIR (hanya bisa dari Romi / panitia)

1. **Kunci model asli** — model saat ini stub deterministik lokal
   (`briefminion/stub_model.py`). Swap ke model asli = satu edit config
   di `agents.json` (provider `cortensor-portal` + `CORTENSOR_API_KEY`,
   atau provider OpenAI-compatible lain). Perlu: akses Cortensor Portal
   via Discord @jancuk4075, atau kunci OpenAI-compatible apa pun.
   Portal bersifat opsional untuk kualifikasi (tidak dihukum bila tidak
   ada), tapi aturan minta "real model-backed run" — rekaman demo perlu
   diulang dengan model asli bila akses didapat.
2. **Repo target PR** — belum diumumkan (lihat #2 di atas). PR TIDAK
   bisa diajukan sebelum URL-nya ada. Perlu dipantau: halaman DoraHacks,
   docs Cortensor, atau Discord Cortensor.
3. **Upload video ke YouTube** — `demo.mp4` siap, tapi upload ke channel
   Romi + link-nya dicantumkan di PR adalah langkah Romi.
4. **Persetujuan Romi** — jangan submit PR apa pun tanpa OK Romi
   (aturan 17 Nov 09:18 WIB).

## Kejujuran / batasan

- Tidak ada kunci API berbayar yang diminta/digunakan. Tidak ada PR yang
  diajukan ke mana pun. Model stub TIDAK diklaim sebagai model asli di
  dokumen mana pun (README, video, PR-DRAFT).
- Deadline 19 Des 2026 14:59 WIB = 18 Des 2026 PT (DoraHacks/Eventbrite).
  Evaluasi/pengumuman pemenang: TBD. Hadiah diskresioner — memenuhi
  syarat tidak menjamin hadiah/penempatan.
