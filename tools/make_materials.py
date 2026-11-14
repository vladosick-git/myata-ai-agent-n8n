# Собирает 5 скриншотов 1920x1280 и кадры для видео из сырых снимков экрана.
# Запуск: python tools/make_materials.py <папка с сырыми снимками>
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAW = sys.argv[1]
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "materials")
FRAMES = os.path.join(OUT, "video_frames")
ANN = os.path.join(OUT, "s_podpisyami")
PLAIN = os.path.join(OUT, "skrinshoty")
os.makedirs(ANN, exist_ok=True)
os.makedirs(PLAIN, exist_ok=True)
os.makedirs(FRAMES, exist_ok=True)

BG = (13, 20, 17)
PANEL = (22, 32, 28)
MINT = (126, 217, 168)
WHITE = (240, 245, 242)
GREY = (160, 175, 168)


def font(size, bold=False):
    return ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf", size)


def raw(suffix):
    for f in os.listdir(RAW):
        if suffix in f:
            return Image.open(os.path.join(RAW, f)).convert("RGB")
    raise SystemExit("нет файла " + suffix)


def fit(img, w, h):
    k = min(w / img.width, h / img.height)
    return img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)


def rounded(img, r=18):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.width - 1, img.height - 1], r, fill=255)
    return img, mask


def canvas(w, h, title, sub):
    c = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, w, 8], fill=MINT)
    d.text((80, 44), title, font=font(58, True), fill=WHITE)
    d.text((82, 122), sub, font=font(30), fill=GREY)
    d.text((w - 80, 62), "Цветочная студия «Мята»", font=font(28), fill=MINT, anchor="ra")
    return c, d


def paste(c, img, x, y):
    im, mask = rounded(img)
    ImageDraw.Draw(c).rounded_rectangle([x - 3, y - 3, x + im.width + 2, y + im.height + 2], 20, outline=(45, 62, 54), width=3)
    c.paste(im, (x, y), mask)


def notes(d, x, y, items, width_chars=34, size=32):
    for head, text in items:
        d.ellipse([x, y + 12, x + 16, y + 28], fill=MINT)
        d.text((x + 36, y), head, font=font(size, True), fill=WHITE)
        y += size + 14
        line = ""
        for word in text.split():
            if len(line) + len(word) + 1 > width_chars:
                d.text((x + 36, y), line, font=font(size - 4), fill=GREY)
                y += size + 6
                line = word
            else:
                line = (line + " " + word).strip()
        if line:
            d.text((x + 36, y), line, font=font(size - 4), fill=GREY)
            y += size + 6
        y += 30


CHAT_X = (632, 1285)


def chat(suffix, y0, y1=712):
    return raw(suffix).crop((CHAT_X[0], y0, CHAT_X[1], y1))


# ---------- 5 скриншотов 1920x1280
W, H = 1920, 1280

# 1. Диалог с клиентом
c, d = canvas(W, H, "Диалог с клиентом", "Агент отвечает в Telegram по базе знаний и сам доводит разговор до заявки")
img = fit(chat("q3478n", 150), 1060, 1040)
paste(c, img, 80, 200)
notes(d, 80 + img.width + 70, 230, [
    ("Цены только из базы", "25 роз 4 600 ₽ и доставка 350 ₽ взяты из прайса студии, сумму агент посчитал сам"),
    ("Сам спрашивает недостающее", "Для заявки нужны имя, запрос и контакт. Чего нет, агент уточняет"),
    ("Заявка принята", "Клиент получает подтверждение, администратор получает уведомление"),
    ("Память диалога", "Агент помнит адрес, время и цвет роз из прошлых сообщений"),
], width_chars=36)
c.save(os.path.join(ANN, "01_dialog_s_klientom.png"))

# 2. Таблица заявок
c, d = canvas(W, H, "Таблица заявок", "Имя, запрос и контакт попадают в Google таблицу, администратору уходит сообщение")
t = fit(raw("73gvmr").crop((0, 0, 1345, 330)), 1760, 440)
paste(c, t, 80, 200)
n = fit(raw("6lylak").crop((632, 510, 1130, 608)), 1000, 520)
paste(c, n, 80, 200 + t.height + 60)
notes(d, 80 + n.width + 70, 200 + t.height + 70, [
    ("Запись без участия человека", "Строка появляется в момент, когда агент принял заявку"),
    ("Уведомление в группе", "Администратор сразу видит имя, запрос и контакт"),
    ("Статус ведёт владелец", "Новая, подтверждена, выполнена"),
], width_chars=40, size=30)
c.save(os.path.join(ANN, "02_tablica_zayavok.png"))

# 3. Журнал решений
c, d = canvas(W, H, "Журнал решений агента", "По каждому сообщению видно, какое действие выбрано, почему и на какие пункты базы агент опирался")
j = fit(raw("eb1fe9").crop((0, 128, 1548, 728)), 1760, 1000)
paste(c, j, 80, 200)
d.text((80, 200 + j.height + 40), "Действия: ответ по базе, уточняющий вопрос, заявка, передача человеку. Столбец «Почему» агент заполняет сам.", font=font(30), fill=GREY)
c.save(os.path.join(ANN, "03_zhurnal_resheniy.png"))

# 4. Схема в n8n
c, d = canvas(W, H, "Схема агента в n8n", "Сообщение клиента, база знаний, модель Claude, решение и четыре ветки действий")
s = raw("34bpig")
s = fit(s.crop((0, 34, s.width, s.height)), 1760, 420)
paste(c, s, 80, 200)
lst = fit(raw("29rzye").crop((330, 170, 1420, 380)), 1000, 330)
paste(c, lst, 80, 200 + s.height + 60)
notes(d, 80 + lst.width + 70, 200 + s.height + 60, [
    ("Три сценария", "Приём сообщений, агент, отчёт за день"),
    ("Агент решает сам", "Узел «Что решил агент» разводит по веткам: ответ, уточнение, заявка, передача человеку"),
    ("Всё пишется в журнал", "Последний узел записывает решение и причину"),
], width_chars=40, size=30)
c.save(os.path.join(ANN, "04_shema_n8n.png"))

# 5. Ежедневный отчёт
c, d = canvas(W, H, "Отчёт за день", "Каждый вечер в 20:00 владелец получает цифры за день и разбор вопросов")
r = fit(chat("9ij5bn", 100), 1060, 1040)
paste(c, r, 80, 200)
notes(d, 80 + r.width + 70, 230, [
    ("Цифры за день", "Диалоги, сообщения, заявки и сколько раз понадобился человек"),
    ("Частые вопросы", "Модель сама группирует обращения по смыслу и считает повторы"),
    ("Что добавить в базу", "Советы собраны из вопросов, на которые агент не смог ответить сам"),
    ("По запросу тоже", "Команда /otchet в группе администратора присылает отчёт сразу"),
], width_chars=36)
c.save(os.path.join(ANN, "05_otchet_za_den.png"))

# ---------- кадры для видео 1920x1080
VW, VH = 1920, 1080


def slide(name, title, sub, img, note=None):
    c, d = canvas(VW, VH, title, sub)
    if note:
        im = fit(img, 1100, 840)
        paste(c, im, 80, 200)
        notes(d, 80 + im.width + 60, 240, note, width_chars=30, size=32)
    else:
        im = fit(img, 1760, 840)
        paste(c, im, (VW - im.width) // 2, 200)
    c.save(os.path.join(FRAMES, name))


c, d = canvas(VW, VH, "", "")
d.text((VW // 2, 400), "Цветочная студия «Мята»", font=font(96, True), fill=WHITE, anchor="mm")
d.text((VW // 2, 520), "ИИ агент отвечает клиентам в Telegram", font=font(48), fill=MINT, anchor="mm")
d.text((VW // 2, 610), "n8n, Claude, Google Таблицы", font=font(36), fill=GREY, anchor="mm")
c.save(os.path.join(FRAMES, "00.png"))

slide("01.png", "Клиент спрашивает цену", "Ответ собран из базы знаний студии", chat("zjjmt3", 440), [("Вопрос в Telegram", "Сколько стоит букет из 25 роз с доставкой"), ("Ответ за несколько секунд", "4 600 ₽ и доставка 350 ₽, итого 4 950 ₽")])
slide("02.png", "Клиент хочет заказать", "Агент понимает, что для заявки не хватает данных", chat("swprm1", 395), [("Агент уточняет сам", "Спрашивает имя, контакт и количество роз")])
slide("03.png", "Клиент называет имя и телефон", "Агент продолжает собирать заявку", chat("iarhaj", 270), [("Память диалога", "Адрес и время из прошлых сообщений агент помнит")])
slide("04.png", "Заявка принята", "Все три поля есть: имя, запрос, контакт", chat("q3478n", 300), [("Решение агента", "Действие «Заявка»"), ("Клиенту", "Подтверждение с суммой 4 950 ₽")])
slide("05.png", "Заявка в таблице", "Строка появилась в Google таблице без участия человека", raw("73gvmr").crop((0, 0, 1345, 330)))
slide("06.png", "Уведомление администратору", "Сообщение в рабочей группе студии", raw("6lylak").crop((632, 510, 1130, 608)), [("Сразу после заявки", "Имя, запрос, контакт и ник клиента")])
slide("07.png", "Журнал решений", "Что агент ответил, какое действие выбрал и почему", raw("eb1fe9").crop((0, 128, 1548, 728)))
slide("08.png", "Отчёт за день", "Цифры, частые вопросы и что добавить в базу знаний", chat("9ij5bn", 100), [("Каждый день в 20:00", "Отчёт приходит владельцу в Telegram")])
# ---------- обычные скриншоты сервиса 1920x1280, без рамок и подписей
for name, suffix in [("01_dialog_s_klientom.png", "x68msl"), ("02_tablica_zayavok.png", "73gvmr"), ("03_zhurnal_resheniy.png", "nilrbq"), ("04_shema_n8n.png", "sidjpo"), ("05_otchet_za_den.png", "heet82")]:
    im = raw(suffix)
    if suffix == "heet82":
        # В кадре видна команда с адресом бота. Размываем её, чтобы по скриншоту нельзя было найти бота.
        box = (770, 58, 1050, 98)
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(9)), box)
    im.resize((1920, 1280), Image.LANCZOS).save(os.path.join(PLAIN, name))
print("готово")
