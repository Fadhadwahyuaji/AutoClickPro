🖱️ Auto Clicker for Windows

Auto Clicker adalah aplikasi sederhana berbasis Python yang digunakan untuk melakukan klik otomatis di Windows. Aplikasi ini dirancang untuk membantu pengguna melakukan klik berulang secara cepat, konsisten, dan dapat dikustomisasi sesuai kebutuhan.

🚀 Fitur Utama

1. Pengaturan Interval Klik

- Interval klik dapat diatur secara detail dengan format jam, menit, detik, dan milidetik.
- Contoh: 00:00:05:500 → klik setiap 5,5 detik.

2. Tipe Klik

- Klik kiri.
- Klik kanan.
- Double click.

3. Lokasi Klik

- Current Position → klik dilakukan di posisi kursor saat ini.
- Custom Coordinate (X, Y) → klik dilakukan di titik tertentu sesuai koordinat layar.

4. Hotkey untuk Kontrol Cepat

- Tekan F6 untuk memulai auto click.
- Tekan F7 untuk menghentikan auto click.

5. User Interface (UI) Sederhana

- Antarmuka berbasis Tkinter yang mudah digunakan.
- Input field untuk interval klik, tipe klik, lokasi klik, serta tombol Start dan Stop.

6. Counter (opsional, coming soon)

- Opsi untuk menghentikan auto click setelah sejumlah klik tertentu.

🛠️ Teknologi yang Digunakan

- Python 3.x
- PyAutoGUI → untuk simulasi klik mouse.
- Keyboard → untuk mendeteksi hotkey.
- Tkinter → untuk membangun GUI aplikasi.
- (opsional) Threading → agar auto click berjalan tanpa mengganggu GUI.

⚙️ Cara Kerja Sistem

1. Pengguna mengatur parameter

- Interval klik (jam, menit, detik, milidetik).
- Tipe klik (left/right/double).
- Lokasi klik (current atau custom).

2. Pengguna menekan tombol Start / Hotkey F6

- Sistem menghitung total interval dalam milidetik.
- Auto click dijalankan sesuai parameter.

3. Klik otomatis berlangsung

- Kursor akan melakukan klik sesuai interval dan lokasi yang dipilih.

4. Pengguna menghentikan auto click

- Menekan tombol Stop / Hotkey F7.
- Proses dihentikan, sistem kembali ke kondisi siap.
