"""Kontent sozlamalari. Shu faylni oʻzingizga moslab tahrirlang."""

# Yangilik manbalari (RSS). Oʻzbekcha yoki sohaga oid manbalarni qoʻshishingiz mumkin.
FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://hnrss.org/frontpage",
]

# Yangilik shu soʻzlardan birini oʻz ichiga olsagina koʻrib chiqiladi.
KEYWORDS = ["telegram", "chatbot", "messenger", "whatsapp", "automation", "ai agent", "ai assistant",
            "mini app", "payments", "e-commerce", "crm", "customer support", "bot ", " bots", "openai", "anthropic"]

TOPICS = [
    "Telegram bot nima va u biznesga qanday yordam beradi",
    "Savdo boti: katalog, savat va buyurtma qanday ishlaydi",
    "Bron boti: yozilishni avtomatlashtirish",
    "Toʻlov botlari: toʻlovni qabul qilish va chek yuborish",
    "Mijozga birinchi 5 daqiqada javob berish nega muhim",
    "Chatbot va jonli operator: qachon qaysi biri kerak",
    "Telegram Mini App nima va kimga kerak",
    "Botda mijozni kutib olish (onboarding): birinchi taassurot",
    "Ommaviy xabar yuborish: spamga tushmaslik qoidalari",
    "Bot va mijozlar bazasi (CRM): nimani saqlash kerak",
    "Savol-javob botini tayyorlash: qaysi savollardan boshlash",
    "Bot menyusi dizayni: oddiy tugmalar qoidasi",
    "Instagramdan Telegram botga mijoz olib kelish",
    "Eslatmalar yordamida kelmay qolishlarni kamaytirish",
    "Bot statistikasi: qaysi koʻrsatkichlarni kuzatish kerak",
    "Mijoz maʼlumotlarini himoya qilish: bot egasi uchun minimal qoidalar",
    "Bot buyurtma qilishdan oldin oʻzingizga beradigan 5 ta savol",
    "Oʻquv markazlari uchun bot imkoniyatlari",
    "Kafe va restoranlar uchun buyurtma boti",
    "Goʻzallik salonlari uchun bron boti",
    "Onlayn doʻkon uchun buyurtma boti",
    "Klinika va shifoxonalar uchun navbat boti",
    "Takroriy savollarga sarflanadigan vaqtni hisoblash",
    "Bot yasashda keng tarqalgan xatolar",
    "Inline tugmalar va oddiy tugmalar farqi",
    "Botda ariza formasi: qancha savol yetarli",
    "Referal tizimi bot orqali: doʻstni taklif qilish",
    "Eski mijozlarni qaytarish: aksiya va eslatmalar",
    "Veb-sayt yoki bot: biznes uchun qaysi biri avval",
    "Telegram kanal va bot birga: kontentdan sotuvgacha",
    "Viktorina botlari: oʻquvchilarni qiziqtirish",
    "Bot tokenini sir saqlash nega muhim",
    "Yozishmalarni tahlil qilib, xizmatni yaxshilash",
    "AI yordamchi botlar: imkoniyat va chegaralar",
    "Toʻlovni avtomatik tasdiqlash: qoʻlda ishlashdan farqi",
    "Ikki tilli bot (oʻzbek va rus): mijozga qulaylik",
    "Botda fikr-mulohaza yigʻish",
    "Yetkazib berish xizmatlari uchun bot",
    "Bot haqida 5 ta keng tarqalgan afsona",
    "Botni birinchi 7 kunda qanday sinash kerak",
]

PROMO_TYPES = ["savdo boti", "bron boti", "toʻlov boti", "oʻquv boti", "savol-javob boti", "xabar yuboruvchi bot"]

SYSTEM = (
    "Sen «sahifabot» Telegram kanalining muharririsan. Kanal Telegram bot yasash xizmati va "
    "biznesni botlar bilan avtomatlashtirish haqida. Oʻzbek tilida (lotin yozuvida) yoz: sodda, jonli, "
    "ortiqcha dabdabasiz. Matnni Telegram HTML teglari bilan formatla: faqat <b>, <i>, <code>, <a href>. "
    "Boshqa teg ishlatma. 1-3 ta emoji yetarli. Hajmi 400-900 belgi. "
    "Faqat berilgan faktlarga tayan: raqam, sana, narx, nom va natijalarni oʻzingdan toʻqima. "
    "Manbadan nusxa koʻchirma, oʻz soʻzing bilan qayta yoz. "
    "Faqat tayyor post matnini qaytar, izoh yoki sarlavha yozma."
)

NEWS_PROMPT = (
    "Yangilik sarlavhasi: {title}\nQisqa mazmuni: {summary}\n\n"
    "Agar bu yangilik Telegram, botlar, chatbotlar, AI yordamchilar yoki biznesni avtomatlashtirish "
    "bilan bogʻliq boʻlmasa yoki ishonchsiz boʻlsa, faqat SKIP deb yoz.\n"
    "Aks holda post yoz: nima yangilik boʻldi va bu bot yaratadigan yoki botdan foydalanadigan "
    "kichik biznes uchun nimani anglatadi. Havolani yozma, uni oʻzim qoʻshaman."
)
EDU_PROMPT = "Mavzu: {topic}\n\nShu mavzuda taʼlimiy post yoz. Bitta amaliy misol keltir va oxirida bitta aniq xulosa ber."
TIP_PROMPT = "Mavzu: {topic}\n\nKichik biznes egasi uchun shu mavzuda bitta qisqa, amaliy maslahat yoz (3-5 jumla)."
PROMO_PROMPT = (
    "sahifabot studiyasi {kind} yasab berishi haqida qisqa, bosimsiz reklama posti yoz. "
    "Narx, muddat, mijoz soni yoki natijalarni oʻzingdan toʻqima. Bu bot biznesdagi qaysi qoʻlda ishni "
    "yengillashtirishini tushuntir. Murojaat havolasini yozma, uni oʻzim qoʻshaman."
)
QUIZ_PROMPT = (
    "Mavzu: {topic}\n\nShu mavzuda Telegram botlar haqida bitta viktorina savoli tuz. "
    "Faqat JSON qaytar: {{\"question\": \"...\", \"options\": [\"...\", \"...\", \"...\", \"...\"], "
    "\"correct\": 0, \"explanation\": \"...\"}}. correct — toʻgʻri variant indeksi (0-3). "
    "Savol 250 belgidan, har bir variant 90 belgidan, izoh 180 belgidan oshmasin. Oʻzbek tilida."
)
