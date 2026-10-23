"""Tayyor kontent bazasi (API kalitsiz rejim uchun). Postlarni oʻzingiz tahrirlab, koʻpaytirishingiz mumkin."""
import random

# (sarlavha rasm uchun, post matni)
EDU = [
 ("Telegram bot nima?", "<b>Telegram bot nima?</b>\n\nBu Telegram ichida ishlaydigan dastur. Mijoz yozadi, bot oʻzi javob beradi, buyurtma qabul qiladi, eslatma yuboradi. Alohida ilova oʻrnatish shart emas: mijoz allaqachon Telegramda. Shuning uchun bot orqali xizmat koʻrsatish oddiy va tez."),
 ("Savdo boti qanday ishlaydi?", "<b>Savdo boti qanday ishlaydi?</b>\n\n1️⃣ Mijoz katalogni koʻradi\n2️⃣ Mahsulotni savatga qoʻshadi\n3️⃣ Manzil va toʻlov usulini tanlaydi\n4️⃣ Buyurtma sizga tayyor holda tushadi\n\nSiz har bir xabarga qoʻlda javob yozmaysiz, faqat tayyor buyurtmalarni bajarasiz."),
 ("Bron boti nima beradi?", "<b>Bron boti nima beradi?</b>\n\nMijoz oʻzi qulay vaqtni tanlab yoziladi. Bot band vaqtlarni koʻrsatmaydi va qabuldan oldin eslatma yuboradi. Telefon qoʻngʻiroqlari kamayadi, jadval esa tartibli boʻladi. Salon, klinika va oʻquv markazi uchun juda mos."),
 ("Toʻlov boti: nega kerak?", "<b>Toʻlov boti: nega kerak?</b>\n\nMijoz toʻlov havolasini oladi va toʻlaydi, bot toʻlov holatini tekshirib, chekni yuboradi. Siz „pul tushdimi?” deb tekshirib oʻtirmaysiz. Qaysi toʻlov tizimini ulash mumkinligi loyihaga qarab hal qilinadi."),
 ("Bot yoki jonli operator?", "<b>Bot yoki jonli operator?</b>\n\nIkkisi bir-birini toʻldiradi. Bot takroriy savollarga (narx, manzil, ish vaqti) darhol javob beradi. Murakkab savolni esa sizga uzatadi. Shunda xodim faqat haqiqatan insoniy yordam kerak joyda ishlaydi."),
 ("Birinchi daqiqalar hal qiladi", "<b>Birinchi daqiqalar hal qiladi</b>\n\nMijoz bir nechta joyga yozadi va birinchi javob bergan joyga koʻproq ishonadi. Bot kechasi ham, dam olish kunida ham darhol javob beradi. Javobni kutib ketib qolgan mijozlar kamayadi."),
 ("Telegram Mini App nima?", "<b>Telegram Mini App nima?</b>\n\nBu Telegram ichida ochiladigan kichik ilova: katalog, forma yoki buyurtma oynasi koʻrinishida. Mahsulot koʻp boʻlsa, oddiy tugmalardan qulayroq. Qaysi biri sizga mosligini biznes turiga qarab tanlaymiz."),
 ("Mijozlarga xabar yuborish qoidalari", "<b>Mijozlarga xabar yuborish qoidalari</b>\n\nBot orqali aksiya yoki yangilikni hammaga yuborish mumkin. Lekin kuniga koʻp xabar yuborsangiz, odamlar botni bloklaydi. Yaxshi qoida: kam, foydali va mijozga aloqador xabar yuboring."),
 ("Bot mijozlar bazasini oʻzi toʻplaydi", "<b>Bot mijozlar bazasini oʻzi toʻplaydi</b>\n\nHar bir mijoz botga yozganda ismi va tanlovi saqlanadi. Keyin kim nimani buyurtma qilganini koʻrib, mos taklif yuborish mumkin. Qoʻlda daftarga yozish shart emas."),
 ("Savol-javob botini nimadan boshlash kerak?", "<b>Savol-javob botini nimadan boshlash kerak?</b>\n\nOxirgi bir oyda mijozlar eng koʻp soʻragan 10 ta savolni yozib chiqing: narx, manzil, ish vaqti, yetkazish. Bot avval shularga javob bersin. Qolganini keyin qoʻshasiz."),
 ("Instagramdan Telegram botga", "<b>Instagramdan Telegram botga</b>\n\nInstagramda mijoz qiziqadi, lekin yozishmalar yoʻqolib ketadi. Profil havolasiga bot qoʻysangiz, mijoz narx, buyurtma va savollarni bir joyda hal qiladi. Siz esa hamma soʻrovni bitta tartibli joyda koʻrasiz."),
 ("Yaxshi bot menyusi qanday boʻladi?", "<b>Yaxshi bot menyusi qanday boʻladi?</b>\n\nTugmalar 4-6 tadan oshmasin, nomlari tushunarli boʻlsin: „Narxlar”, „Buyurtma”, „Aloqa”. Mijoz birinchi bosishdayoq nima qilishni bilishi kerak. Murakkab menyu mijozni charchatadi."),
 ("Eslatma — eng arzon sotuv vositasi", "<b>Eslatma — eng arzon sotuv vositasi</b>\n\nQabuldan oldin yuborilgan eslatma kelmay qolishlarni kamaytiradi. Aksiya haqidagi eslatma esa eski mijozni qaytaradi. Bot bu ishni har safar oʻzi qiladi."),
 ("Bot qaysi raqamlarni koʻrsatadi?", "<b>Bot qaysi raqamlarni koʻrsatadi?</b>\n\nNechta mijoz yozdi, nechtasi buyurtma berdi, qaysi savol koʻp takrorlandi. Shu raqamlar asosida xizmatni yaxshilash osonlashadi. Taxmin emas, aniq maʼlumot."),
 ("Mijoz maʼlumoti — masʼuliyat", "<b>Mijoz maʼlumoti — masʼuliyat</b>\n\nBotga faqat kerakli maʼlumotni soʻrang: ism, telefon. Ortiqcha narsa soʻramang va bot tokenini hech kimga bermang. Ishonch shu oddiy qoidalardan boshlanadi."),
 ("Bot haqida 3 ta afsona", "<b>Bot haqida 3 ta afsona</b>\n\n❌ „Bot faqat katta biznesga kerak” — kichik biznesda vaqt tejashi koʻproq seziladi.\n❌ „Mijoz botni yoqtirmaydi” — mijoz tez va aniq javob kutadi.\n❌ „Bir marta yasab qoʻyiladi” — yaxshi bot vaqt oʻtishi bilan yangilanib boradi."),
 ("Bot buyurtma qilishdan oldin 5 savol", "<b>Bot buyurtma qilishdan oldin 5 savol</b>\n\n1. Qaysi ish eng koʻp vaqt oladi?\n2. Mijozlar eng koʻp nima soʻraydi?\n3. Buyurtma qayerdan keladi?\n4. Toʻlov qanday qabul qilinadi?\n5. Natijani qanday oʻlchaysiz?\n\nShu javoblar botning rejasini tayyorlab beradi."),
 ("Oʻquv markazi uchun bot", "<b>Oʻquv markazi uchun bot</b>\n\nDars jadvali, eslatma, davomat, qisqa test va natijalar bir joyda. Oʻquvchi ham, ota-ona ham kerakli maʼlumotni botdan oladi. Oʻqituvchi esa vaqtini darsga sarflaydi."),
 ("Kafe va restoran uchun bot", "<b>Kafe va restoran uchun bot</b>\n\nMenyu, stol bron qilish va buyurtma qabul qilish. Band soatlarda ham mijozga bir zumda javob beriladi, xodimlar esa yigʻilib qolgan qoʻngʻiroqlardan xalos boʻladi."),
 ("Kanal va bot birga ishlaganda", "<b>Kanal va bot birga ishlaganda</b>\n\nKanal mijozni qiziqtiradi, bot esa uni buyurtmagacha olib boradi. Postga bot havolasini qoʻysangiz, qiziqqan odam darhol savol berishi yoki buyurtma qilishi mumkin."),
]

TIPS = [
 ("Birinchi javob avtomatik boʻlsin", "<b>Maslahat:</b> mijozga „Salom, yozganingiz uchun rahmat” deb avtomatik birinchi javob qoʻying. Odam eʼtibor olganini sezadi va sabr bilan kutadi."),
 ("Savollarni yozib boring", "<b>Maslahat:</b> bir hafta davomida mijozlar soʻragan savollarni yozib boring. Eng koʻp takrorlanadigan 5 tasi botga birinchi navbatda joylanadi."),
 ("Menyuda 6 tadan koʻp tugma boʻlmasin", "<b>Maslahat:</b> bot menyusida 6 tadan koʻp tugma qoʻymang. Koʻp tanlov — kam harakat."),
 ("Postda bitta aniq chaqiruv", "<b>Maslahat:</b> har postingiz oxirida bitta aniq chaqiruv boʻlsin: „Buyurtma berish” yoki „Savol berish”. Bir nechta chaqiruv odamni chalgʻitadi."),
 ("Operator tugmasi doim boʻlsin", "<b>Maslahat:</b> botda doim „Operator bilan bogʻlanish” tugmasi boʻlsin. Mijoz botga ishonmay qolgan paytda ham sizga yetib keladi."),
 ("Mijozni ismi bilan chaqiring", "<b>Maslahat:</b> botda mijozni ismi bilan chaqiring. Kichik narsa, lekin muloqot iliqroq boʻladi."),
 ("Bot javobi qisqa boʻlsin", "<b>Maslahat:</b> bot javobi 2-3 jumladan oshmasin. Uzun matnni mijoz oʻqimaydi, oʻrniga tugma bering."),
 ("Ishga tushirishdan oldin sinang", "<b>Maslahat:</b> botni ishga tushirishdan oldin 3-4 doʻstingizga bering va qayerda adashganini kuzating. Eng foydali kamchiliklar shunda topiladi."),
 ("Ommaviy xabar vaqti", "<b>Maslahat:</b> ommaviy xabarni ish vaqtida, odamlar band boʻlmagan soatda yuboring. Tunda kelgan xabar koʻpincha oʻqilmay qoladi."),
 ("Katalogda sifatli rasm", "<b>Maslahat:</b> savdo botida har mahsulot uchun sifatli rasm va 1-2 qator tavsif yetarli. Ortiqcha matn buyurtmani sekinlashtiradi."),
 ("Buyurtmadan keyin baho soʻrang", "<b>Maslahat:</b> buyurtmadan keyin bot orqali „Xizmatimizni baholang” deb soʻrang. Bitta tugma bilan fikr yigʻish mumkin."),
 ("Bitta bot — bitta maqsad", "<b>Maslahat:</b> birinchi botni bitta aniq vazifa uchun yasang, masalan faqat bron. Ishlab ketgach, imkoniyatlarni qoʻshib boraverasiz."),
 ("Takroriy ish — botga topshiring", "<b>Maslahat:</b> kun davomida bir xil javobni 3 martadan koʻp yozsangiz, bu ish botga topshiriladigan ish."),
 ("Bot tokenini sir saqlang", "<b>Maslahat:</b> bot tokenini hech kimga bermang va ochiq joyga yozmang. Kimdir tokenni bilsa, botingizni boshqara oladi."),
]

# (sarlavha, matn) — CTA keyin avtomatik qoʻshiladi
PROMO = [
 ("Savdo boti yasab beramiz", "<b>Savdo boti yasab beramiz 🛒</b>\n\nKatalog, savat va buyurtma qabul qilish bir joyda. Mijozlaringiz Telegram ichida buyurtma beradi, siz esa tayyor buyurtmalarni olasiz.\n\nQanday bot kerakligini yozing, mos yechim tayyorlaymiz."),
 ("Bron boti yasab beramiz", "<b>Bron boti yasab beramiz 📅</b>\n\nMijozlar oʻzi vaqt tanlab yoziladi, bot tasdiqlaydi va eslatma yuboradi. Salon, klinika, oʻquv markazi va xizmat koʻrsatuvchilar uchun.\n\nBiznesingizni yozing, jadvalga moslab beramiz."),
 ("Toʻlov boti yasab beramiz", "<b>Toʻlov boti yasab beramiz 💳</b>\n\nToʻlov havolasi, toʻlovni tekshirish va chek yuborish avtomatik boʻladi. Siz qoʻlda tekshirib oʻtirmaysiz.\n\nQaysi toʻlov tizimi kerakligini yozing, imkoniyatini aniqlab beramiz."),
 ("Oʻquv boti yasab beramiz", "<b>Oʻquv boti yasab beramiz 🎓</b>\n\nDars eslatmalari, qisqa testlar va natijalar Telegram ichida. Oʻquv markazlari va kurs egalari uchun qulay.\n\nKursingiz haqida yozing, mos bot tayyorlaymiz."),
 ("Savol-javob boti yasab beramiz", "<b>Savol-javob boti yasab beramiz 💬</b>\n\nNarx, manzil, ish vaqti kabi takroriy savollarga bot oʻzi javob beradi, murakkab savolni sizga uzatadi.\n\nMijozlar eng koʻp nimani soʻrashini yozing, shu asosida tuzamiz."),
 ("Xabar yuboruvchi bot", "<b>Aksiya va yangiliklarni bot yuboradi 📣</b>\n\nMijozlaringizga qiziqarli xabar va eslatmalarni bir zumda yetkazing, toʻgʻri va kam yuborish qoidasi bilan.\n\nQanday xabarlar kerakligini yozing, tizimini tuzib beramiz."),
 ("Biznesingizga maxsus bot", "<b>Gʻoyangiz bormi? 🤖</b>\n\nBiznesingizga moslangan maxsus Telegram bot yasaymiz. Qaysi ish sizning vaqtingizni koʻp oladi? Shuni aytsangiz, shu ishni botga topshirish yoʻlini topamiz."),
 ("Instagramni botga ulaymiz", "<b>Instagramdagi mijozni botga olib keling 📲</b>\n\nProfil havolasiga bot qoʻyilsa, qiziqqan mijoz narx, buyurtma va savolni bir joyda hal qiladi. Sizga esa tartibli soʻrovlar keladi.\n\nBiz shu tizimni tayyorlab beramiz."),
]

# (savol, [variantlar, toʻgʻrisi birinchi], izoh)
QUIZ = [
 ("Telegramda yangi bot yaratish va token olish qaysi bot orqali amalga oshadi?", ["@BotFather", "@Telegram", "@BotMaker", "@Support"], "Yangi bot yaratish va token olish @BotFather orqali amalga oshadi."),
 ("Bot tokenini kimga berish mumkin?", ["Hech kimga, sir saqlanadi", "Hammaga", "Faqat doʻstlarga", "Kanal obunachilariga"], "Token botni boshqarish kaliti. Uni sir saqlash kerak."),
 ("Quyidagilardan qaysi biri bot qila OLMAYDIGAN ish?", ["Mijoz telefonini bloklash", "Buyurtma qabul qilish", "Eslatma yuborish", "Savolga avtomatik javob berish"], "Bot Telegram ichida ishlaydi va mijoz telefonini boshqara olmaydi."),
 ("Kechasi soat 3 da kelgan mijoz savoliga kim darhol javob beradi?", ["Bot", "Uxlayotgan xodim", "Hech kim", "Faqat direktor"], "Bot 24/7 ishlaydi va darhol javob beradi."),
 ("Bron botining asosiy vazifasi nima?", ["Vaqtga yozilishni avtomatlashtirish", "Rasm tahrirlash", "Musiqa ijro etish", "Video montaj"], "Bron boti mijozni vaqtga yozadi va eslatma yuboradi."),
 ("Inline tugmalar qayerda koʻrinadi?", ["Xabar ostida", "Faqat profilda", "Kanal nomida", "Qidiruv oynasida"], "Inline tugmalar xabarning ostida chiqadi."),
 ("Ommaviy xabar yuborishda eng yaxshi qoida qaysi?", ["Kam, foydali va mos xabar", "Kuniga koʻp marta yuborish", "Faqat tunda yuborish", "Hammasini bosh harflarda yozish"], "Koʻp xabar yuborsangiz, odamlar botni bloklaydi."),
 ("Bot orqali mijozdan qaysi maʼlumotni soʻrash yetarli?", ["Ism va telefon", "Karta paroli", "Pasport nusxasi", "Uy manzilining kaliti"], "Faqat kerakli maʼlumotni soʻrang, ortiqchasini emas."),
 ("Botni ishga tushirishdan oldin nima qilish kerak?", ["Sinovdan oʻtkazish", "Tokenni eʼlon qilish", "Hech narsa", "Botning nomini oʻchirish"], "Sinov paytida koʻp kamchilik topiladi."),
 ("Telegram Mini App nima?", ["Telegram ichida ochiladigan kichik ilova", "Yangi telefon modeli", "Mobil operator", "Antivirus"], "Mini App katalog yoki forma koʻrinishida Telegram ichida ochiladi."),
 ("Savdo botida buyurtma odatda nima bilan boshlanadi?", ["Katalogni koʻrish", "Botni oʻchirish", "Kanalni tark etish", "Pul qaytarish"], "Mijoz avval katalogni koʻradi, keyin savatga qoʻshadi."),
 ("Instagramdagi mijozni botga olib kelishning yaxshi yoʻli qaysi?", ["Profil havolasiga bot qoʻyish", "Hech narsa qilmaslik", "Rasmlarni oʻchirish", "Profilni yopish"], "Profil havolasi mijozni toʻgʻridan-toʻgʻri botga olib keladi."),
]

# (sarlavha, [(kim, matn), ...]) — GIF animatsiya uchun
DIALOGS = [
 ("Savdo boti", [("me", "Salom, narxlar bormi?"), ("bot", "Salom! Mana katalog."), ("me", "Qora krossovka, 42"), ("bot", "Savatga qoʻshildi. Buyurtma beramizmi?")]),
 ("Bron boti", [("me", "Ertaga yozilsam boʻladimi?"), ("bot", "Albatta! 10:00, 12:30 yoki 16:00"), ("me", "12:30 ga"), ("bot", "Yozildingiz. Qabuldan oldin eslatamiz.")]),
 ("Toʻlov boti", [("me", "Qanday toʻlayman?"), ("bot", "Toʻlov havolasi tayyor."), ("me", "Toʻladim"), ("bot", "Toʻlov qabul qilindi. Chek yuborildi.")]),
 ("Oʻquv boti", [("bot", "Mini test: 12 x 3 = ?"), ("me", "36"), ("bot", "Toʻgʻri! +10 ball"), ("me", "Keyingisi!")]),
 ("Savol-javob boti", [("me", "Yetkazib berish bormi?"), ("bot", "Ha, shahar boʻylab."), ("me", "Ish vaqtingiz?"), ("bot", "Har kuni 9:00 dan 21:00 gacha.")]),
 ("Xabar yuboruvchi bot", [("bot", "Yangi aksiya: chegirma boshlandi!"), ("me", "Qanday olaman?"), ("bot", "Buyurtma bering, chegirma avtomatik hisoblanadi."), ("me", "Zoʻr!")]),
 ("Tungi mijoz", [("me", "Soat 03:00. Ishlaysizlarmi?"), ("bot", "Ha! Bot doim ishlaydi."), ("me", "Narxi qancha?"), ("bot", "Mana narxlar roʻyxati.")]),
 ("Ariza boti", [("me", "Menga bot kerak"), ("bot", "Ajoyib! Biznesingiz nima?"), ("me", "Goʻzallik saloni"), ("bot", "Bron boti mos keladi. Ariza qoldiramizmi?")]),
]

VIDEO_CAPTIONS = [
 "🎬 <b>Bot amalda</b>\n\nQisqa videoda Telegram bot biznesga qanday yordam berishini koʻring.",
 "🎬 <b>30 soniyada tushuntiramiz</b>\n\nMijozlarga javob berish, buyurtma va bron: bot hammasini oʻzi bajaradi.",
 "🎬 <b>Qiziq video</b>\n\nBotning kundalik ishdagi foydasi haqida qisqa lavha.",
]
CTA_FOOTERS = ["🤖 Sizga ham shunday bot kerakmi? @{bot}", "👉 Biznesingizga bot kerakmi? @{bot}", "📩 Savolingiz bormi? @{bot} ga yozing"]
HASHTAGS = ["#telegrambot", "#avtomatlashtirish", "#biznes", "#chatbot"]


def build(kind, rnd, used, bot_username, insta):
    """Bazadan post tanlaydi. used: {kalit: oxirgi_ishlatilgan_vaqt}. Qaytaradi: (kalit, post_dict)."""
    from helpers import pick_least_used
    pools = {"edu": EDU, "tip": TIPS, "promo": PROMO, "quiz": QUIZ, "demo": DIALOGS}
    pool = pools[kind]
    i = pick_least_used([f"{kind}:{n}" for n in range(len(pool))], used, rnd)
    key = f"{kind}:{i}"
    item = pool[i]
    if kind in ("edu", "tip"):
        text = item[1]
        if rnd.random() < .4:
            text += "\n\n" + rnd.choice(CTA_FOOTERS).format(bot=bot_username)
        text += "\n\n" + " ".join(rnd.sample(HASHTAGS, 2))
        return key, dict(head=item[0], text=text)
    if kind == "promo":
        text = item[1] + f"\n\n👉 Buyurtma: @{bot_username}\n📷 Instagram: @{insta}"
        return key, dict(head=item[0], text=text)
    if kind == "quiz":
        q, opts, expl = item
        order = list(range(len(opts))); rnd.shuffle(order)
        shuffled = [opts[j] for j in order]
        return key, dict(head=q, text=q, poll={"question": q[:290], "options": shuffled, "correct": order.index(0), "explanation": expl[:190]})
    title, msgs = item
    text = (f"<b>{title} amalda 👆</b>\n\nBot mijoz bilan shunday muloqot qiladi. Sizga ham shunday bot kerakmi?\n\n"
            f"👉 @{bot_username}\n📷 Instagram: @{insta}")
    return key, dict(head=title, text=text, dialog=(title, msgs))
