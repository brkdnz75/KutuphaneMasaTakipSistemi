import cv2
import time
import mediapipe as mp
from tkinter import *
from tkinter import messagebox

yuz_algila = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
el_algila = mp.solutions.hands.Hands()
vucut_algila = mp.solutions.pose.Pose()


def ciz_yuzler(goruntu, yuzler):
    for (x, y, w, h) in yuzler:
        cv2.rectangle(goruntu, (x, y), (x + w, y + h), (255, 0, 0), 2)


def ciz_eller(goruntu, eller):
    if eller.multi_hand_landmarks:
        for hand_landmarks in eller.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                goruntu, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
            )


def ciz_vucut(goruntu, vucutlar):
    if vucutlar.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(
            goruntu, vucutlar.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS,
            mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2),
            mp.solutions.drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
        )


def baslat_sistem():
    kamera = cv2.VideoCapture(0)

    if not kamera.isOpened():
        print("Kamera açılmadı.")
        return

    dolu = False
    masa_bos_kalma_suresi = 0
    masa_dolu_kalma_suresi = 0
    sayac_bos = 0
    sayac_dolu = 0

    bos_sure_limiti = 10
    dolu_sure_limiti = 10

    while True:
        durum, goruntu = kamera.read()

        if not durum:
            print("Görüntü alınamadı.")
            break

        gri_goruntu = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
        yuzler = yuz_algila.detectMultiScale(gri_goruntu)
        renkli_goruntu = cv2.cvtColor(goruntu, cv2.COLOR_BGR2RGB)
        eller = el_algila.process(renkli_goruntu)
        vucutlar = vucut_algila.process(renkli_goruntu)


        ciz_yuzler(goruntu, yuzler)
        ciz_eller(goruntu, eller)
        ciz_vucut(goruntu, vucutlar)


        kisi_var = len(yuzler) > 0 or eller.multi_hand_landmarks or vucutlar.pose_landmarks

        if kisi_var:
            if not dolu:
                sayac_dolu = time.time()
                dolu = True
                print("Masa dolu")
            else:
                masa_dolu_kalma_suresi = time.time() - sayac_dolu
                if masa_dolu_kalma_suresi >= dolu_sure_limiti:
                    masa_bos_kalma_suresi = 0
                    print("Masa dolu. Çalışma devam ediyor.")
        else:
            if dolu:
                dolu = False
                sayac_bos = time.time()
                print("Masa boş.")
            else:
                masa_bos_kalma_suresi = time.time() - sayac_bos
                if masa_bos_kalma_suresi >= bos_sure_limiti:
                    print(f"Masa {int(masa_bos_kalma_suresi)} saniyedir boş. Lütfen masayı boşaltın.")
                    masa_bos_kalma_suresi = 0
                    dolu = False

        cv2.imshow("İzleme", goruntu)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    kamera.release()
    cv2.destroyAllWindows()


def giris_kontrol():
    kullanici_adi = kullanici_adi_entry.get()
    sifre = sifre_giris.get()

    if kullanici_adi == "admin" and sifre == "1234":
        messagebox.showinfo("Başarılı", "Giriş başarılı. Sistem başlatılıyor.")
        root.destroy()
        baslat_sistem()
    else:
        messagebox.showerror("Hatalı", "Kullanıcı adı veya şifre yanlış.Tekrar deneyin.")


root = Tk()
root.title("Kütüphane Masa Takip Sistemine Giriş")
root.geometry("300x200")


k_label = Label(root, text="Kullanıcı Adı:")
kullanici_adi_entry = Entry(root)
k_label.grid(row=0, column=0, padx=8, pady=8, sticky="e")
kullanici_adi_entry.grid(row=0, column=1, padx=8, pady=8)


l_sifre = Label(root, text="Şifre:")
sifre_giris = Entry(root, show="*")
l_sifre.grid(row=1, column=0, padx=8, pady=8, sticky="e")
sifre_giris.grid(row=1, column=1, padx=8, pady=8)


g_buton = Button(root, text="Giriş Yap", command=giris_kontrol)
g_buton.grid(row=2, column=0, columnspan=2, pady=20)


root.mainloop()


''' EKSİKLER
    *arkadaki yüzleri algılıyor
    *Maximum el sayısı ve güven oranı varsayılan değer olarak alındı değiştirlmedi.
    *sayaç saymıyor 
    *birden fazla yüz algılanırsa aynı masada uyarı versin (bunun için her masada kamera olması gerekebilir)
    *elimi yüzümle kapatınca masa boş diyor
    *Kütüphane kamerasından masalar nasıl tespit edilecek
    *Masa dolu sayılmaya başlanabilmesi için(yani sayaç sıfırlanabilmesi için) oturan kişinin yeniden geldikten sonra en az 30dk çalışması gerekir
    *Masada eşya yoksa masa tamamen boş kabul edilir
'''
