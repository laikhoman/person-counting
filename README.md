# cara jalankan program
1 buka terminal baru <br/>
2 cd PycharmProjects/PersonCounting/dashboard <br/> 
3 export FLASK_APP=dashboard.py 
export FLASK_DEBUG=1
export MAIL_USERNAME=xihuan.ai8@gmail.com
export MAIL_PASSWORD='Dz87!GPfP$&V'
flask run --reload --port=5000 <br/>
4 buka tab baru browser chrome , ketik 0.0.0.0:5000
   jika ter log out silakan login dengan email: luxkoman@yahoo.com & password: 123456 <br/>
5 klik link Add Place / Edit Place <br/>
6 edit jika diperlukan, klik submit pada form edit place <br/>
7 edit jika diperlukan, klik submit pada form edit camera on place <br/>
8 klik edit line pada halaman selanjutnya <br/>
9 tetap edit posisi 2 titik garis secara sembarang, klik submit <br/> 
10 klik tombol ’on' pada halaman list cctv untuk mengaktifkan fitur person counting <br/>

untuk melihat daftar foto orang yang masuk dan keluar dapat dilihat di folder : 
~/PycharmProjects/PersonCounting/dashboard/FirstAndLastPersonIn untuk orang masuk 
~/PycharmProjects/PersonCounting/dashboard/FirstAndLastPersonOut untuk orang keluar

penamaan file berdasarkan tanggal dan waktu yg di log
