import json,os,random,time
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,CommandHandler,MessageHandler,CallbackQueryHandler,filters

TOKEN="8804943669:AAGNV_N2IRF5KkUSBSE9kQby5K-7est-RIs"
OWNER_ID=8551856799;STAR_PRICE=1500;LMP_PRICE=1000;REF_BONUS=1000;START_BALANCE=100;TRANSFER_FEE=0.04;DB="users.json";TOWER_GAMES={};PROMOCODES={}
USER_COMMANDS={}
REQUIRED_CHANNEL="@mines_channel1"
CHANNEL_LINK="https://t.me/mines_channel1"
MINES_GAMES={}
MINES_MULTIPLIERS=[1.1,1.26,1.45,1.67,1.92,2.21,2.54,2.92,3.36,3.86,4.44,5.11,5.88,6.76,7.77,8.94,10.28,11.82,13.59,15.63,17.97,20.67,23.77,27.33,31.43,36.14,41.56,47.79,54.96,63.20,72.68,83.58,96.12,110.54,127.12]

def can_send_command(user_id):
 now=time.time()
 if user_id not in USER_COMMANDS:USER_COMMANDS[user_id]=[]
 USER_COMMANDS[user_id]=[t for t in USER_COMMANDS[user_id] if now-t<60]
 if len(USER_COMMANDS[user_id])>=20:return False
 USER_COMMANDS[user_id].append(now);return True

if os.path.exists(DB):
 with open(DB,"r",encoding="utf-8")as f:users=json.load(f)
else:users={}
def save():json.dump(users,open(DB,"w",encoding="utf-8"),ensure_ascii=False,indent=4)
def get_user(uid):
 uid=str(uid)
 if uid not in users:users[uid]={"balance":START_BALANCE,"bonus":0,"lottery":0,"lmp":0,"games":0,"losses":0,"refs":0,"referrer":"","username":"","name":""};save()
 else:
  for k in["lmp","games","losses","refs","referrer"]:
   if k not in users[uid]:users[uid][k]=0 if k!="referrer" else "";save()
 return users[uid]
def is_owner(id):return str(id)==str(OWNER_ID)
def fmt(n):return f"{n:,}".replace(","," ")
def parse_bet(t):
 t=t.lower().strip().replace(" ","")
 if t in["всё","все","всe"]:return"all"
 try:
  if t.isdigit():return int(t)
  if"ккк"in t:return int(float(t.replace("ккк",""))*1000000000)
  if"кк"in t:return int(float(t.replace("кк",""))*1000000)
  if"к"in t:return int(float(t.replace("к",""))*1000)
  if"млн"in t:return int(float(t.replace("млн",""))*1000000)
  return int(t)
 except:return None
def get_crash_point(m):
 r=random.random()
 if m<=1.5:return round(random.uniform(m,m*2.5),2)if r<0.7 else round(random.uniform(1.0,m),2)
 elif m<=2:return round(random.uniform(m,m*2.2),2)if r<0.55 else round(random.uniform(1.0,m),2)
 elif m<=3:return round(random.uniform(m,m*2.0),2)if r<0.35 else round(random.uniform(1.0,m),2)
 elif m<=5:return round(random.uniform(m,m*1.8),2)if r<0.18 else round(random.uniform(1.0,m),2)
 elif m<=10:return round(random.uniform(m,m*1.5),2)if r<0.07 else round(random.uniform(1.0,m),2)
 elif m<=20:return round(random.uniform(m,m*1.3),2)if r<0.02 else round(random.uniform(1.0,m),2)
 elif m<=50:return round(random.uniform(m,m*1.2),2)if r<0.005 else round(random.uniform(1.0,m),2)
 else:return round(random.uniform(m,m*1.1),2)if r<0.001 else round(random.uniform(1.0,m),2)
TOWER_MULT=[1.3,1.8,2.6,3.8,5.5,8.0,12.0]

SLOT_SYMBOLS=["🍒","🍋","🍊","🍇","🔔","7⃣"]
SLOT_WEIGHTS=[30,25,20,15,7,3]
def get_slot_result():
 return [random.choices(SLOT_SYMBOLS, weights=SLOT_WEIGHTS, k=1)[0] for _ in range(3)]

async def check_subscription(u,c):
    user_id=u.effective_user.id
    try:
        chat_member=await c.bot.get_chat_member(chat_id=REQUIRED_CHANNEL,user_id=user_id)
        if chat_member.status in ["member","administrator","creator"]:
            return True
        return False
    except:return False

async def create_promo(u,c):
    if not is_owner(u.effective_user.id):return
    if len(c.args)!=3:
        return await u.message.reply_text("❌ Использование: промокод <название> <сумма> <кол-во>\nПример: промокод WELCOME100 100 5")
    name=c.args[0].upper()
    try:
        amount=int(c.args[1])
        uses=int(c.args[2])
        if amount<=0 or uses<=0:
            return await u.message.reply_text("❌ Сумма и кол-во должны быть >0!")
    except:
        return await u.message.reply_text("❌ Введите числа!")
    if name in PROMOCODES:
        return await u.message.reply_text(f"❌ Промокод {name} уже существует!")
    PROMOCODES[name]={"amount":amount,"uses":uses,"used":0,"users_used":[]}
    await u.message.reply_text(f"✅ Промокод {name} создан!\n💰 Сумма: {amount} lkoin\n🔄 Активаций: {uses}")

async def activate_promo(u,c):
    if not c.args:
        return await u.message.reply_text("❌ Использование: <промокод>\nПример: WELCOME100")
    name=c.args[0].upper().strip()
    if name not in PROMOCODES:
        return await u.message.reply_text("❌ Промокод не найден!")
    promo=PROMOCODES[name]
    if promo["used"]>=promo["uses"]:
        return await u.message.reply_text("❌ Промокод уже использован!")
    uid=str(u.effective_user.id)
    if uid in promo["users_used"]:
        return await u.message.reply_text("❌ Вы уже активировали этот промокод!")
    d=get_user(uid)
    d["balance"]=d.get("balance",0)+promo["amount"]
    promo["used"]+=1
    promo["users_used"].append(uid)
    save()
    await u.message.reply_text(f"✅ Промокод {name} активирован!\n💰 +{promo['amount']} lkoin")
    try:
        await u.bot.send_message(chat_id=int(uid), text=f"🎁 Промокод {name} активирован!\n💰 +{promo['amount']} lkoin\n💰 Баланс: {d.get('balance',0)} lkoin")
    except:pass

async def promo_list(u,c):
    if not is_owner(u.effective_user.id):return
    if not PROMOCODES:
        return await u.message.reply_text("📋 Нет активных промокодов!")
    msg="📋 СПИСОК ПРОМОКОДОВ\n\n"
    for name,data in PROMOCODES.items():
        msg+=f"🔑 {name}\n💰 {data['amount']} lkoin\n🔄 {data['used']}/{data['uses']}\n\n"
    await u.message.reply_text(msg)

async def promo_delete(u,c):
    if not is_owner(u.effective_user.id):return
    if not c.args:
        return await u.message.reply_text("❌ Использование: удалить_промо <название>")
    name=c.args[0].upper()
    if name not in PROMOCODES:
        return await u.message.reply_text("❌ Промокод не найден!")
    del PROMOCODES[name]
    await u.message.reply_text(f"✅ Промокод {name} удален!")
async def start(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 is_subscribed=await check_subscription(u,c)
 if not is_subscribed:
  kb=[[InlineKeyboardButton("📢 Подписаться на канал",url=CHANNEL_LINK),InlineKeyboardButton("✅ Проверить подписку",callback_data="check_sub")]]
  await u.message.reply_text(f"📢 Для использования бота подпишись на канал!\n\n🔗 {REQUIRED_CHANNEL}\n\nПосле подписки нажми проверку:",reply_markup=InlineKeyboardMarkup(kb))
  return
 d=get_user(u.effective_user.id)
 if u.effective_user.username:d["username"]=u.effective_user.username
 if u.effective_user.first_name:d["name"]=u.effective_user.first_name
 bot_name=(await c.bot.get_me()).username
 ref_link=f"https://t.me/{bot_name}?start=ref_{u.effective_user.id}"
 if c.args and len(c.args)>0 and c.args[0].startswith("ref_"):
  ref_id=c.args[0].split("_")[1]
  if ref_id!=str(u.effective_user.id)and not d.get("referrer"):
   ref_user=get_user(ref_id);ref_user["balance"]=ref_user.get("balance",0)+REF_BONUS
   ref_user["refs"]=ref_user.get("refs",0)+1
   d["referrer"]=ref_id;d["balance"]=d.get("balance",0)+REF_BONUS;save()
   await u.message.reply_text(f"🎉 По рефералке!\n💰 +{REF_BONUS} lkoin\n👤 Реферер +{REF_BONUS} lkoin")
   return
 save()
 await u.message.reply_text(f"👋 Добро пожаловать!\n🔗 Твоя ссылка: {ref_link}\n💎 За друга {REF_BONUS} lkoin\n👥 Приглашено: {d.get('refs',0)}\n📋 'команды' - список")

async def check_sub_callback(update,context):
 q=update.callback_query
 is_subscribed=await check_subscription(q,context)
 if is_subscribed:
  await q.answer("✅ Подписка подтверждена!")
  await q.edit_message_text("✅ Вы подписаны на канал!\n\nТеперь используйте /start")
 else:
  kb=[[InlineKeyboardButton("📢 Подписаться на канал",url=CHANNEL_LINK),InlineKeyboardButton("✅ Проверить подписку",callback_data="check_sub")]]
  await q.answer("❌ Вы не подписаны!",show_alert=True)
  await q.edit_message_text(f"📢 Подпишись на канал!\n\n🔗 {REQUIRED_CHANNEL}\n\nПосле подписки нажми проверку:",reply_markup=InlineKeyboardMarkup(kb))

async def commands_list(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 await u.message.reply_text("📋 ДОСТУПНЫЕ КОМАНДЫ\n\n🎮 ИГРЫ:\nкраш <ставка> <множитель>\nкраш всё\nбашня <ставка>\nслоты <ставка>\nмины <ставка>\n\n💰 ФИНАНСЫ:\nбаланс / б / бал\nпоинт - LMP\nбонус\nдонат <⭐>\n\n💸 ПЕРЕВОДЫ:\nдать <сумма> (ответом на сообщение)\n\n🔗 РЕФЕРАЛКА:\nреф - ссылка\nрефы - статистика\n\n🔑 ПРОМОКОДЫ:\n<промокод> - активировать (в любом регистре)\n(админ: промокод <название> <сумма> <кол-во>)\n\n🏪 ОБМЕННИК:\nобменник\n\n📊 ИНФО:\nигры\nтоп")

async def ref_link(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 bot_name=(await c.bot.get_me()).username
 await u.message.reply_text(f"🔗 Ссылка для друзей:\nhttps://t.me/{bot_name}?start=ref_{u.effective_user.id}\n💎 За каждого друга {REF_BONUS} lkoin")

async def ref_stats(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 d=get_user(u.effective_user.id)
 await u.message.reply_text(f"👥 Приглашено: {d.get('refs',0)} чел\n💎 Заработано: {d.get('refs',0)*REF_BONUS} lkoin")

async def games(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 await u.message.reply_text(f"🎮 ДОСТУПНЫЕ ИГРЫ\n\n1️⃣ КРАШ\nкраш <ставка> <множитель>\nкраш всё\n\n2️⃣ БАШНЯ\nбашня <ставка>\nбашня всё\n7 уровней\n\n3️⃣ СЛОТЫ\nслоты <ставка>\n777 - x5, три одинаковых - x2\n\n4️⃣ МИНЫ\nмины <ставка>\nПоле 5x5, 3 бомбы, до 127x")

async def bonus(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 d=get_user(u.effective_user.id)
 if is_owner(u.effective_user.id):return await u.message.reply_text(f"🎁 +{random.randint(30,500)} lkoin!\n💰 0")
 now=int(time.time())
 if d.get("bonus",0)and(now-d["bonus"])<3600:return await u.message.reply_text(f"⏳ Бонус через {(3600-(now-d['bonus']))//60} мин.")
 m=random.randint(30,500);d["bonus"]=now;d["balance"]=d.get("balance",0)+m;save()
 await u.message.reply_text(f"🎁 +{m} lkoin!\n💰 {d.get('balance',0)}")

async def balance(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 d=get_user(u.effective_user.id)
 if is_owner(u.effective_user.id):return await u.message.reply_text("💰 0 lkoin\n·············\n💣 Игр: 0\n🗿 Проиграно: 0\n👥 Рефов: 0")
 await u.message.reply_text(f"💰 {d.get('balance',0)} lkoin\n·············\n💣 Игр: {d.get('games',0)}\n🗿 Проиграно: {fmt(d.get('losses',0))}\n👥 Рефов: {d.get('refs',0)}\n💎 LMP: {d.get('lmp',0)}")

async def point(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 d=get_user(u.effective_user.id)
 await u.message.reply_text(f"💎 {d.get('lmp',0)} LMP")

async def buy_lmp(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 if not c.args:return await u.message.reply_text(f"❌ купить <количество>\n1 LMP = {LMP_PRICE} lkoin")
 try:
  a=int(c.args[0])
  if a<=0:return await u.message.reply_text("❌ >0!")
  d=get_user(u.effective_user.id);cost=a*LMP_PRICE
  if d.get("balance",0)<cost:return await u.message.reply_text(f"❌ Нужно {cost} lkoin!\n💰 {d.get('balance',0)} lkoin")
  d["balance"]=d.get("balance",0)-cost;d["lmp"]=d.get("lmp",0)+a;save()
  await u.message.reply_text(f"✅ Куплено {a} LMP за {cost} lkoin\n💰 {d.get('balance',0)} lkoin\n💎 {d.get('lmp',0)} LMP")
 except:await u.message.reply_text("❌ Введите число!")

async def sell_lmp(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 if not c.args:return await u.message.reply_text(f"❌ продать <количество>\n1 LMP = {LMP_PRICE} lkoin")
 try:
  a=int(c.args[0])
  if a<=0:return await u.message.reply_text("❌ >0!")
  d=get_user(u.effective_user.id)
  if d.get("lmp",0)<a:return await u.message.reply_text(f"❌ Не хватает! 💎 {d.get('lmp',0)} LMP")
  earned=a*LMP_PRICE;d["lmp"]=d.get("lmp",0)-a;d["balance"]=d.get("balance",0)+earned;save()
  await u.message.reply_text(f"✅ Продано {a} LMP за {earned} lkoin\n💰 {d.get('balance',0)} lkoin\n💎 {d.get('lmp',0)} LMP")
 except:await u.message.reply_text("❌ Введите число!")

async def exchanger(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 d=get_user(u.effective_user.id);lmp=d.get("lmp",0);balance=d.get("balance",0);kb=[]
 if lmp>=1:kb.append([InlineKeyboardButton(f"💰 1 LMP = {LMP_PRICE} lkoin",callback_data=f"sell_1_{u.effective_user.id}")])
 if lmp>=5:kb.append([InlineKeyboardButton(f"💰 5 LMP = {LMP_PRICE*5} lkoin",callback_data=f"sell_5_{u.effective_user.id}")])
 if lmp>=10:kb.append([InlineKeyboardButton(f"💰 10 LMP = {LMP_PRICE*10} lkoin",callback_data=f"sell_10_{u.effective_user.id}")])
 if lmp>0:kb.append([InlineKeyboardButton(f"💰 Всё ({lmp} LMP = {lmp*LMP_PRICE} lkoin)",callback_data=f"sell_all_{u.effective_user.id}")])
 if not kb:kb.append([InlineKeyboardButton("❌ Нет LMP",callback_data="none")])
 await u.message.reply_text(f"🏪 ОБМЕННИК\n\n💎 LMP: {lmp}\n💰 lkoin: {balance}\n📌 1 LMP = {LMP_PRICE} lkoin",reply_markup=InlineKeyboardMarkup(kb))

async def sell_callback(update,context):
 q=update.callback_query;data=q.data
 if data.startswith("sell_"):
  p=data.split("_");a=p[1];uid=int(p[2])
  if not can_send_command(uid):return await q.answer("⏳ Подожди 1 минуту!")
  if q.from_user.id!=uid:return await q.answer("❌ Не твоя!")
  d=get_user(uid);lmp=d.get("lmp",0)
  if a=="all":a=lmp
  else:a=int(a)
  if a<=0 or d.get("lmp",0)<a:await q.answer("❌ Нет LMP!");return
  earned=a*LMP_PRICE
  kb=[[InlineKeyboardButton("✅ Да",callback_data=f"cf_{uid}_{a}"),InlineKeyboardButton("❌ Нет",callback_data=f"cn_{uid}")]]
  await q.edit_message_text(f"💎 Обмен {a} LMP\nПолучишь: {fmt(earned)} lkoin\nПодтверди?",reply_markup=InlineKeyboardMarkup(kb))
  await q.answer()

async def confirm_callback(update,context):
 q=update.callback_query;data=q.data
 if data.startswith("cf_"):
  _,uid,a=data.split("_");uid=int(uid);a=int(a)
  if not can_send_command(uid):return await q.answer("⏳ Подожди 1 минуту!")
  if q.from_user.id!=uid:return await q.answer("❌ Не твоя!")
  d=get_user(uid)
  if d.get("lmp",0)<a:await q.edit_message_text("❌ Не хватает LMP!");return
  earned=a*LMP_PRICE;d["lmp"]=d.get("lmp",0)-a;d["balance"]=d.get("balance",0)+earned;save()
  await q.edit_message_text(f"✅ Обменяно {a} LMP\n+{fmt(earned)} lkoin\n💰 {d.get('balance',0)} lkoin\n💎 {d.get('lmp',0)} LMP")
  await q.answer()

async def cancel_callback(update,context):
 q=update.callback_query;data=q.data
 if data.startswith("cn_"):
  uid=int(data.split("_")[1])
  if not can_send_command(uid):return await q.answer("⏳ Подожди 1 минуту!")
  if q.from_user.id!=uid:return await q.answer("❌ Не твоя!")
  await q.edit_message_text("❌ Отменено!");await q.answer()

async def slots(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 d=get_user(u.effective_user.id);owner=is_owner(u.effective_user.id)
 if not c.args:return await u.message.reply_text("❌ слоты <ставка>")
 bet=parse_bet(c.args[0])
 if bet=="all":bet=999999999 if owner else d.get("balance",0)
 if bet is None or bet<=0:return await u.message.reply_text("❌ Неверная ставка!")
 if not owner and d.get("balance",0)<bet:return await u.message.reply_text(f"❌ Не хватает! {d.get('balance',0)} lkoin")
 if not owner:d["balance"]=d.get("balance",0)-bet
 d["games"]=d.get("games",0)+1
 result=get_slot_result();player_num=random.randint(1,999)
 win_mult=5 if result[0]==result[1]==result[2]=="7⃣" else (2 if result[0]==result[1]==result[2] else 0)
 if win_mult>0:
  win=int(bet*win_mult)
  if not owner:d["balance"]=d.get("balance",0)+win
  save()
  await u.message.reply_text(f"🎰 player #{player_num}\n💥 Слоты · Выигрыш!\n·····················\n💸 Ставка: {fmt(bet)} lkoin\n🏆 Выигрыш: +{fmt(win)} (x{win_mult})\n🔮 {result[0]}{result[1]}{result[2]}")
 else:
  if not owner:d["losses"]=d.get("losses",0)+bet
  save()
  await u.message.reply_text(f"🎰 player #{player_num}\n💥 Слоты · Проигрыш!\n·····················\n💸 Ставка: {fmt(bet)} lkoin\n🔮 {result[0]}{result[1]}{result[2]}")

async def mines(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 d=get_user(u.effective_user.id);owner=is_owner(u.effective_user.id)
 if not c.args:return await u.message.reply_text("❌ мины <ставка>\nПример: мины 100")
 bet=parse_bet(c.args[0])
 if bet=="all":bet=999999999 if owner else d.get("balance",0)
 if bet is None or bet<=0:return await u.message.reply_text("❌ Неверная ставка!")
 if not owner and d.get("balance",0)<bet:return await u.message.reply_text(f"❌ Не хватает! {d.get('balance',0)} lkoin")
 if not owner:d["balance"]=d.get("balance",0)-bet
 d["games"]=d.get("games",0)+1
 save()
 bombs=set()
 while len(bombs)<3:bombs.add(random.randint(0,24))
 gid=f"{u.effective_user.id}_{int(time.time())}"
 MINES_GAMES[gid]={"user_id":u.effective_user.id,"bet":bet,"bombs":list(bombs),"level":0,"revealed":[],"rows":5,"cols":5}
 await show_mines(u,c,gid,0)

async def show_mines(update,context,gid,is_callback):
 g=MINES_GAMES.get(gid)
 if not g:return
 kb=[]
 for r in range(g["rows"]):
  row=[]
  for c in range(g["cols"]):
   idx=r*g["cols"]+c
   if idx in g["revealed"]:
    if idx in g["bombs"]:row.append(InlineKeyboardButton("💣",callback_data="done"))
    else:row.append(InlineKeyboardButton("✅",callback_data="done"))
   else:row.append(InlineKeyboardButton("❓",callback_data=f"mn_{gid}_{idx}"))
  kb.append(row)
 if g["level"]>0:
  mult=MINES_MULTIPLIERS[g["level"]-1] if g["level"]-1<len(MINES_MULTIPLIERS) else MINES_MULTIPLIERS[-1]
  win=int(g["bet"]*mult)
  kb.append([InlineKeyboardButton(f"💰 Забрать {win} lkoin (x{mult:.2f})",callback_data=f"mco_{gid}")])
 t=f"💣 МИНЫ\n💰 Ставка: {fmt(g['bet'])} lkoin\n📊 Открыто: {g['level']}/3"
 if g["level"]>0:
  mult=MINES_MULTIPLIERS[g["level"]-1] if g["level"]-1<len(MINES_MULTIPLIERS) else MINES_MULTIPLIERS[-1]
  t+=f"\n📈 x{mult:.2f}\n💎 {fmt(int(g['bet']*mult))} lkoin"
 t+="\n\n❓-не открыто|✅-безопасно|💣-бомба"
 if is_callback:await update.edit_message_text(t,reply_markup=InlineKeyboardMarkup(kb))
 else:await update.message.reply_text(t,reply_markup=InlineKeyboardMarkup(kb))

async def mines_cb(update,context):
 q=update.callback_query;data=q.data
 if data.startswith("mn_"):
  parts=data.split("_")
  gid=f"{parts[1]}_{parts[2]}"
  idx=int(parts[3])
  g=MINES_GAMES.get(gid)
  if not g or g["user_id"]!=q.from_user.id:
   return await q.answer("❌ Не твоя игра!")
  if not can_send_command(g["user_id"]):
   return await q.answer("⏳ Подожди 1 минуту!")
  if idx in g["revealed"]:
   return await q.answer("❌ Уже открыто!")
  g["revealed"].append(idx)
  if idx in g["bombs"]:
   await q.answer("💣 БОМБА!")
   d=get_user(g["user_id"])
   d["losses"]=d.get("losses",0)+g["bet"]
   save()
   kb=[]
   for r in range(g["rows"]):
    row=[]
    for c in range(g["cols"]):
     idx2=r*g["cols"]+c
     if idx2 in g["bombs"]:
      row.append(InlineKeyboardButton("💣",callback_data="done"))
     else:
      row.append(InlineKeyboardButton("✅",callback_data="done"))
    kb.append(row)
   await q.edit_message_text(f"💣 МИНЫ\n💰 Ставка: {fmt(g['bet'])} lkoin\n💥 ПРОИГРЫШ!\n❌ Потерял {fmt(g['bet'])} lkoin",reply_markup=InlineKeyboardMarkup(kb))
   del MINES_GAMES[gid]
   return
  g["level"]+=1
  if g["level"]>=3:
   mult=MINES_MULTIPLIERS[g["level"]-1] if g["level"]-1<len(MINES_MULTIPLIERS) else MINES_MULTIPLIERS[-1]
   win=int(g["bet"]*mult)
   d=get_user(g["user_id"])
   d["balance"]=d.get("balance",0)+win
   save()
   kb=[]
   for r in range(g["rows"]):
    row=[]
    for c in range(g["cols"]):
     idx2=r*g["cols"]+c
     if idx2 in g["bombs"]:
      row.append(InlineKeyboardButton("💣",callback_data="done"))
     else:
      row.append(InlineKeyboardButton("✅",callback_data="done"))
    kb.append(row)
   await q.edit_message_text(f"💣 МИНЫ\n💰 Ставка: {fmt(g['bet'])} lkoin\n🎉 ПОБЕДА!\n📈 x{mult:.2f}\n💎 +{fmt(win)} lkoin",reply_markup=InlineKeyboardMarkup(kb))
   del MINES_GAMES[gid]
   return
  await q.answer(f"✅ {g['level']}/3 пройдено!")
  await show_mines(q,context,gid,1)
 elif data.startswith("mco_"):
  parts=data.split("_")
  gid=f"{parts[1]}_{parts[2]}"
  g=MINES_GAMES.get(gid)
  if not g or g["user_id"]!=q.from_user.id:
   return await q.answer("❌ Не твоя игра!")
  if not can_send_command(g["user_id"]):
   return await q.answer("⏳ Подожди 1 минуту!")
  if g["level"]<=0:
   return await q.answer("❌ Открой клетку!")
  mult=MINES_MULTIPLIERS[g["level"]-1] if g["level"]-1<len(MINES_MULTIPLIERS) else MINES_MULTIPLIERS[-1]
  win=int(g["bet"]*mult)
  d=get_user(g["user_id"])
  d["balance"]=d.get("balance",0)+win
  save()
  kb=[]
  for r in range(g["rows"]):
   row=[]
   for c in range(g["cols"]):
    idx2=r*g["cols"]+c
    if idx2 in g["bombs"]:
     row.append(InlineKeyboardButton("💣",callback_data="done"))
    else:
     row.append(InlineKeyboardButton("✅",callback_data="done"))
   kb.append(row)
  await q.edit_message_text(f"💣 МИНЫ\n💰 Ставка: {fmt(g['bet'])} lkoin\n✅ Забрал!\n📈 x{mult:.2f}\n💎 +{fmt(win)} lkoin",reply_markup=InlineKeyboardMarkup(kb))
  del MINES_GAMES[gid]
 else:await q.answer()
async def transfer(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 if not u.message.reply_to_message:
  return await u.message.reply_text("❌ Ответь на сообщение игрока, которому хочешь перевести!")
 try:
  recipient_id = u.message.reply_to_message.from_user.id
 except:
  return await u.message.reply_text("❌ Не удалось определить получателя!")
 if not c.args:
  return await u.message.reply_text("❌ Использование: дать <сумма>\nПример: дать 100")
 try:
  amount = int(c.args[0])
  if amount <= 0:return await u.message.reply_text("❌ Сумма должна быть больше 0!")
 except:
  return await u.message.reply_text("❌ Введите число!\nПример: дать 100")
 sender_id = u.effective_user.id
 sender = get_user(sender_id)
 recipient = get_user(recipient_id)
 if str(sender_id) == str(recipient_id):
  return await u.message.reply_text("❌ Нельзя перевести самому себе!")
 if is_owner(sender_id):
  fee = 0
  total = amount
 else:
  if sender.get("balance",0) < amount:
   return await u.message.reply_text(f"❌ Недостаточно средств!\n💰 Баланс: {sender.get('balance',0)} lkoin\n🎯 Нужно: {amount} lkoin")
  fee = int(amount * TRANSFER_FEE)
  total = amount + fee
  if sender.get("balance",0) < total:
   return await u.message.reply_text(f"❌ Недостаточно средств с учётом комиссии 4%!\n💰 Баланс: {sender.get('balance',0)} lkoin\n🎯 Нужно: {total} lkoin (с комиссией {fee})")
  sender["balance"] = sender.get("balance",0) - total
 recipient["balance"] = recipient.get("balance",0) + amount
 save()
 sender_name = f"@{sender.get('username','')}" if sender.get('username') else sender.get('name','Игрок')
 recipient_name = f"@{recipient.get('username','')}" if recipient.get('username') else recipient.get('name','Игрок')
 await u.message.reply_text(
  f"✅ ПЕРЕВОД ВЫПОЛНЕН!\n\n"
  f"👤 От: {sender_name}\n"
  f"👤 Кому: {recipient_name}\n"
  f"💰 Сумма: {amount} lkoin\n"
  f"💸 Комиссия (4%): {fee} lkoin\n"
  f"📊 Всего списано: {total} lkoin\n\n"
  f"💰 Баланс отправителя: {sender.get('balance',0)} lkoin\n"
  f"💰 Баланс получателя: {recipient.get('balance',0)} lkoin"
 )

async def crash(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 d=get_user(u.effective_user.id);o=is_owner(u.effective_user.id);n=f"@{d.get('username','')}"if d.get('username')else d.get('name','Игрок')
 d["games"]=d.get("games",0)+1
 if c.args and len(c.args)>=1 and c.args[0].lower().replace("ё","е")in["всё","все","всe"]:
  b=999999999 if o else d.get("balance",0)
  if b<=0:return await u.message.reply_text("❌ 0 lkoin!")
  if len(c.args)>=2:
   try:
    m=float(c.args[1])
    if m<1.01 or m>100:return await u.message.reply_text("❌ 1.01-100")
   except:return await u.message.reply_text("❌ Пример: краш всё 3")
  else:m=round(random.uniform(1.1,50.0),2)
  cp=get_crash_point(m)
  if cp>=m:
   w=int(b*m)
   if not o:d["balance"]=d.get("balance",0)+w
   save();await u.message.reply_text(f"🎮 {n}\n☑️ Ракета улетела на x{cp}\n☑️ Выиграл! +{fmt(w)} lkoin")
  else:
   if not o:d["balance"]=0;d["losses"]=d.get("losses",0)+b
   save();await u.message.reply_text(f"🎮 {n}\n☠️ Ракета упала на x{cp}\n❌ Проиграл -{fmt(b)} lkoin")
  return
 if len(c.args)!=2:return await u.message.reply_text("❌ краш <ставка> <множитель>\nкраш всё")
 try:
  b=parse_bet(c.args[0])
  if b is None or b=="all":raise
  m=float(c.args[1])
 except:return await u.message.reply_text("❌ Неверные числа!")
 if m<1.01 or m>100:return await u.message.reply_text("❌ 1.01-100")
 if b<=0:return await u.message.reply_text("❌ >0!")
 if not o and d.get("balance",0)<b:return await u.message.reply_text(f"❌ Не хватает! {d.get('balance',0)} lkoin")
 if not o:d["balance"]=d.get("balance",0)-b
 cp=get_crash_point(m)
 if cp>=m:
  w=int(b*m)
  if not o:d["balance"]=d.get("balance",0)+w
  save();await u.message.reply_text(f"🎮 {n}\n☑️ Ракета улетела на x{cp}\n☑️ Выиграл! +{fmt(w)} lkoin")
 else:
  if not o:d["losses"]=d.get("losses",0)+b
  save();await u.message.reply_text(f"🎮 {n}\n☠️ Ракета упала на x{cp}\n❌ Проиграл -{fmt(b)} lkoin")

async def tower(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 d=get_user(u.effective_user.id);o=is_owner(u.effective_user.id)
 d["games"]=d.get("games",0)+1
 if not c.args:return await u.message.reply_text("❌ башня <ставка>")
 b=parse_bet(c.args[0])
 if b=="all":b=999999999 if o else d.get("balance",0)
 if b is None or b<=0:return await u.message.reply_text("❌ Неверная ставка!")
 if not o and d.get("balance",0)<b:return await u.message.reply_text(f"❌ Не хватает! {d.get('balance',0)} lkoin")
 if not o:d["balance"]=d.get("balance",0)-b
 save();gid=f"{u.effective_user.id}_{int(time.time())}"
 bombs=[random.randint(0,4) for _ in range(7)]
 TOWER_GAMES[gid]={"user_id":u.effective_user.id,"bet":b,"bombs":bombs,"level":0,"revealed":[],"rows":1}
 await show_tower(u,c,gid,0)

async def show_tower(update,context,gid,is_callback):
    g=TOWER_GAMES.get(gid)
    if not g:return
    kb=[]
    for r in range(g["rows"]):
        row=[]
        bomb_pos=g["bombs"][r] if r<len(g["bombs"]) else 0
        row_has_open=any(key in g["revealed"] for key in [f"{r}_{i}" for i in range(5)])
        for i in range(5):
            key=f"{r}_{i}"
            if key in g["revealed"]:
                if bomb_pos==i and r==g["rows"]-1:
                    row.append(InlineKeyboardButton("💣",callback_data="done"))
                else:
                    row.append(InlineKeyboardButton("✅",callback_data="done"))
            elif row_has_open:
                row.append(InlineKeyboardButton("🔒",callback_data="done"))
            else:
                row.append(InlineKeyboardButton("❓",callback_data=f"tc_{gid}_{r}_{i}"))
        kb.append(row)
    if g["level"]>0:
        m=TOWER_MULT[g["level"]-1]
        kb.append([InlineKeyboardButton(f"💰 Забрать {int(g['bet']*m)} lkoin (x{m})",callback_data=f"tco_{gid}")])
    t=f"🏗️ БАШНЯ\n💰 Ставка: {fmt(g['bet'])} lkoin\n📊 {g['level']}/7"
    if g["level"]>0:t+=f"\n📈 x{TOWER_MULT[g['level']-1]}\n💎 {fmt(int(g['bet']*TOWER_MULT[g['level']-1]))} lkoin"
    t+="\n\n✅ - пройдено | ❓ - можно открыть | 🔒 - заблокировано | 💣 - бомба"
    if is_callback:await update.edit_message_text(t,reply_markup=InlineKeyboardMarkup(kb))
    else:await update.message.reply_text(t,reply_markup=InlineKeyboardMarkup(kb))

async def tower_cb(update,context):
    q=update.callback_query;data=q.data
    if data.startswith("tc_"):
        p=data.split("_");gid=f"{p[1]}_{p[2]}";r,c=int(p[3]),int(p[4])
        g=TOWER_GAMES.get(gid)
        if not g or g["user_id"]!=q.from_user.id:
            return await q.answer("❌ Не твоя игра!")
        if not can_send_command(g["user_id"]):
            return await q.answer("⏳ Подожди 1 минуту!")
        key=f"{r}_{c}"
        if key in g["revealed"]:return await q.answer("❌ Уже открыто!")
        row_has_open=any(k in g["revealed"] for k in [f"{r}_{i}" for i in range(5)])
        if row_has_open:return await q.answer("❌ В этом ряду уже открыта клетка!")
        bomb_pos=g["bombs"][r] if r<len(g["bombs"]) else 0
        g["revealed"].append(key)
        if bomb_pos==c:
            await q.answer("💣 БОМБА!")
            d=get_user(g["user_id"]);d["losses"]=d.get("losses",0)+g["bet"];save()
            kb=[]
            for row in range(g["rows"]):
                row_btns=[]
                bomb_pos_row=g["bombs"][row] if row<len(g["bombs"]) else 0
                for i in range(5):
                    row_btns.append(InlineKeyboardButton("💣"if bomb_pos_row==i else"✅",callback_data="done"))
                kb.append(row_btns)
            await q.edit_message_text(f"🏗️ БАШНЯ\n💰 {fmt(g['bet'])} lkoin\n💥 ПРОИГРЫШ!\n❌ Потерял {fmt(g['bet'])} lkoin",reply_markup=InlineKeyboardMarkup(kb))
            del TOWER_GAMES[gid];return
        g["level"]+=1
        if g["level"]<7:g["rows"]+=1
        if g["level"]>=7:
            w=int(g["bet"]*TOWER_MULT[6]);d=get_user(g["user_id"]);d["balance"]=d.get("balance",0)+w;save()
            kb=[]
            for row in range(g["rows"]):
                row_btns=[]
                bomb_pos_row=g["bombs"][row] if row<len(g["bombs"]) else 0
                for i in range(5):
                    row_btns.append(InlineKeyboardButton("💣"if bomb_pos_row==i else"✅",callback_data="done"))
                kb.append(row_btns)
            await q.edit_message_text(f"🏗️ БАШНЯ\n💰 {fmt(g['bet'])} lkoin\n🎉 ПОБЕДА!\n📈 x{TOWER_MULT[6]}\n💎 +{fmt(w)} lkoin",reply_markup=InlineKeyboardMarkup(kb))
            del TOWER_GAMES[gid];return
        await q.answer(f"✅ Уровень {g['level']}/7!")
        await show_tower(q,context,gid,1)
    elif data.startswith("tco_"):
        p=data.split("_");gid=f"{p[1]}_{p[2]}"
        g=TOWER_GAMES.get(gid)
        if not g or g["user_id"]!=q.from_user.id:
            return await q.answer("❌ Не твоя игра!")
        if not can_send_command(g["user_id"]):
            return await q.answer("⏳ Подожди 1 минуту!")
        if g["level"]<=0:return await q.answer("❌ Открой клетку!")
        m=TOWER_MULT[g["level"]-1];w=int(g["bet"]*m);d=get_user(g["user_id"]);d["balance"]=d.get("balance",0)+w;save()
        kb=[]
        for row in range(g["rows"]):
            row_btns=[]
            bomb_pos_row=g["bombs"][row] if row<len(g["bombs"]) else 0
            for i in range(5):
                row_btns.append(InlineKeyboardButton("💣"if bomb_pos_row==i else"✅",callback_data="done"))
            kb.append(row_btns)
        await q.edit_message_text(f"🏗️ БАШНЯ\n💰 {fmt(g['bet'])} lkoin\n✅ Забрал!\n📈 x{m}\n💎 +{fmt(w)} lkoin",reply_markup=InlineKeyboardMarkup(kb))
        del TOWER_GAMES[gid]
    else:await q.answer()

async def top(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 t=sorted([(uid,d.get("balance",0))for uid,d in users.items()if uid!=str(OWNER_ID)],key=lambda x:x[1],reverse=True)[:10]
 if not t:return await u.message.reply_text("📊 Топ пуст!")
 m="🏆 ТОП\n\n"
 for i,(uid,b)in enumerate(t):
  n=f"@{users[uid].get('username','')}"if users[uid].get('username')else users[uid].get('name',f"ID:{uid}")
  l=users[uid].get('lmp',0);g=users[uid].get('games',0);r=users[uid].get('refs',0)
  m+=f"{'🥇'if i==0 else'🥈'if i==1 else'🥉'if i==2 else f'{i+1}.'} {n}\n   💰 {fmt(b)} lkoin | 💎 {fmt(l)} LMP | 🎮 {g} | 👥 {r}\n"
 await u.message.reply_text(m)

async def donate(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 d=get_user(u.effective_user.id)
 if c.args:
  try:
   s=int(c.args[0])
   if s<=0 or s>1000:return await u.message.reply_text("❌ 1-1000")
   await u.message.reply_text(f"⭐ {s}⭐ = {s*STAR_PRICE} lkoin\n💰 {d.get('balance',0)} lkoin\n💳 @Melitsov")
  except:await u.message.reply_text("❌ Введите число!")
 else:await u.message.reply_text(f"⭐ 1⭐={STAR_PRICE} lkoin\n💰 {d.get('balance',0)} lkoin\nКоманда: донат <⭐>")

async def admin(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 if not is_owner(u.effective_user.id):return
 if not c.args:return await u.message.reply_text("👑 АДМИН\n\nвыдать <ID> <сумма>\nвыдать_lmp <ID> <сумма>\nзабрать <ID> <сумма>\nстатистика\nсброс <ID>\nобнулить\nрассылка <текст>\nпромокод <название> <сумма> <кол-во>\nпромокоды - список\nудалить_промо <название>")
 
 cmd=c.args[0].lower()
 
 if cmd=="статистика":
  total_lkoin=sum(d.get("balance",0)for d in users.values())
  total_lmp=sum(d.get("lmp",0)for d in users.values())
  total_games=sum(d.get("games",0)for d in users.values())
  total_refs=sum(d.get("refs",0)for d in users.values())
  await u.message.reply_text(f"📊 СТАТИСТИКА\n\n👥 Пользователей: {len(users)}\n💰 lkoin: {fmt(total_lkoin)}\n💎 LMP: {fmt(total_lmp)}\n🎮 Игр: {total_games}\n👥 Рефов: {total_refs}")
 
 elif cmd=="выдать" and len(c.args)==3:
  try:
   uid=c.args[1];amount=int(c.args[2])
   if amount<=0:return await u.message.reply_text("❌ Сумма >0!")
   d=get_user(uid);d["balance"]=d.get("balance",0)+amount;save()
   await u.message.reply_text(f"✅ Выдано {amount} lkoin пользователю {uid}")
  except Exception as e:
   await u.message.reply_text(f"❌ Ошибка: {str(e)}")
 
 elif cmd=="выдать_lmp" and len(c.args)==3:
  try:
   uid=c.args[1];amount=int(c.args[2])
   if amount<=0:return await u.message.reply_text("❌ Сумма >0!")
   d=get_user(uid);d["lmp"]=d.get("lmp",0)+amount;save()
   await u.message.reply_text(f"✅ Выдано {amount} LMP пользователю {uid}")
  except Exception as e:
   await u.message.reply_text(f"❌ Ошибка: {str(e)}")
 
 elif cmd=="забрать" and len(c.args)==3:
  try:
   uid=c.args[1];amount=int(c.args[2])
   if amount<=0:return await u.message.reply_text("❌ Сумма >0!")
   d=get_user(uid)
   if d.get("balance",0)<amount:return await u.message.reply_text(f"❌ У пользователя {d.get('balance',0)} lkoin")
   d["balance"]=d.get("balance",0)-amount;save()
   await u.message.reply_text(f"✅ Забрано {amount} lkoin у {uid}")
  except Exception as e:
   await u.message.reply_text(f"❌ Ошибка: {str(e)}")
 
 elif cmd=="сброс" and len(c.args)==2:
  try:
   uid=c.args[1]
   if uid not in users:return await u.message.reply_text("❌ Пользователь не найден!")
   del users[uid];save()
   await u.message.reply_text(f"✅ Пользователь {uid} удален")
  except Exception as e:
   await u.message.reply_text(f"❌ Ошибка: {str(e)}")
 
 elif cmd=="обнулить":
  try:
   count=0
   for uid in users:
    users[uid]["balance"]=0
    users[uid]["bonus"]=0
    users[uid]["lottery"]=0
    users[uid]["lmp"]=0
    count+=1
   save()
   await u.message.reply_text(f"✅ Обнулены балансы {count} пользователей!\n📊 Статистика игр и рефералов сохранена!")
  except Exception as e:
   await u.message.reply_text(f"❌ Ошибка: {str(e)}")
 
 elif cmd=="рассылка" and len(c.args)>=2:
  try:
   text=" ".join(c.args[1:])
   count=0
   for uid in users:
    try:
     await u.bot.send_message(chat_id=int(uid), text=f"📢 РАССЫЛКА\n\n{text}")
     count+=1
     time.sleep(0.05)
    except:pass
   await u.message.reply_text(f"✅ Отправлено {count} пользователям!")
  except Exception as e:
   await u.message.reply_text(f"❌ Ошибка: {str(e)}")
 
 elif cmd=="промокод" and len(c.args)==3:
  await create_promo(u,c)
 
 elif cmd=="промокоды":
  await promo_list(u,c)
 
 elif cmd=="удалить_промо" and len(c.args)==2:
  await promo_delete(u,c)
 
 else:
  await u.message.reply_text("❌ Неизвестная команда!\n\nвыдать <ID> <сумма>\nвыдать_lmp <ID> <сумма>\nзабрать <ID> <сумма>\nстатистика\nсброс <ID>\nобнулить\nрассылка <текст>\nпромокод <название> <сумма> <кол-во>\nпромокоды - список\nудалить_промо <название>")

async def text(u,c):
 t=u.message.text.lower().strip().replace("ё","е")
 if t=="б":return await balance(u,c)
 if is_owner(u.effective_user.id):
  if t in["админ","админ панель","панель"]:c.args=[];return await admin(u,c)
  if t.startswith("выдать "):
   p=t.split()
   if len(p)==3:c.args=[p[1],p[2]];return await admin(u,c)
  if t.startswith("выдать_lmp "):
   p=t.split()
   if len(p)==3:c.args=["выдать_lmp",p[1],p[2]];return await admin(u,c)
  if t.startswith("забрать "):
   p=t.split()
   if len(p)==3:c.args=[p[1],p[2]];return await admin(u,c)
  if t=="статистика":c.args=["статистика"];return await admin(u,c)
  if t.startswith("сброс "):
   p=t.split()
   if len(p)==2:c.args=["сброс",p[1]];return await admin(u,c)
  if t=="обнулить":c.args=["обнулить"];return await admin(u,c)
  if t.startswith("рассылка "):
   p=t.split()
   if len(p)>=2:c.args=["рассылка"]+p[1:];return await admin(u,c)
  if t.startswith("промокод "):
   p=t.split()
   if len(p)==4:c.args=[p[1],p[2],p[3]];return await create_promo(u,c)
  if t=="промокоды":c.args=["промокоды"];return await admin(u,c)
  if t.startswith("удалить_промо "):
   p=t.split()
   if len(p)==2:c.args=["удалить_промо",p[1]];return await admin(u,c)
 if t in["бонус"]:return await bonus(u,c)
 if t in["баланс","бал"]:return await balance(u,c)
 if t in["поинт","point"]:return await point(u,c)
 if t in["топ"]:return await top(u,c)
 if t in["донат","дон"]:return await donate(u,c)
 if t in["игры","game"]:return await games(u,c)
 if t in["команды","команда","commands","help"]:return await commands_list(u,c)
 if t in["обменник","exchanger"]:return await exchanger(u,c)
 if t in["реф","ref"]:return await ref_link(u,c)
 if t in["рефы","refs"]:return await ref_stats(u,c)
 if t.startswith("слоты ")or t.startswith("slots "):
  c.args=[t.split()[1]];return await slots(u,c)
 if t.startswith("мины ")or t.startswith("mines "):
  c.args=[t.split()[1]];return await mines(u,c)
 if t.startswith("донат ")or t.startswith("дон "):
  c.args=[t.split()[1]];return await donate(u,c)
 if t.startswith("купить "):
  c.args=[t.split()[1]];return await buy_lmp(u,c)
 if t.startswith("продать "):
  c.args=[t.split()[1]];return await sell_lmp(u,c)
 if t.startswith("дать "):
  c.args=[t.split()[1]] if len(t.split())>=2 else []
  return await transfer(u,c)
 if t.startswith("башня "):
  p=t.split()
  c.args=["всё"]if len(p)==2 and p[1]in["всё","все","всe"]else[p[1]]
  return await tower(u,c)
 if t.startswith("краш "):
  p=t.split()
  if len(p)>=2 and p[1]in["всё","все","всe"]:
   c.args=["всё"]+([p[2]]if len(p)>=3 else[])
   return await crash(u,c)
  elif len(p)==3:
   c.args=[p[1],p[2]]
   return await crash(u,c)
 # Проверка на промокод
 if len(t)>=3:
  promo_name=t.upper().strip()
  if promo_name in PROMOCODES:
   c.args=[t]
   return await activate_promo(u,c)

app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("bonus",bonus))
app.add_handler(CommandHandler("balance",balance))
app.add_handler(CommandHandler("crash",crash))
app.add_handler(CommandHandler("tower",tower))
app.add_handler(CommandHandler("top",top))
app.add_handler(CommandHandler("donate",donate))
app.add_handler(CommandHandler("games",games))
app.add_handler(CommandHandler("game",games))
app.add_handler(CommandHandler("commands",commands_list))
app.add_handler(CommandHandler("admin",admin))
app.add_handler(CommandHandler("point",point))
app.add_handler(CommandHandler("exchanger",exchanger))
app.add_handler(CommandHandler("slots",slots))
app.add_handler(CommandHandler("slot",slots))
app.add_handler(CommandHandler("mines",mines))
app.add_handler(CommandHandler("mine",mines))
app.add_handler(CommandHandler("promo",create_promo))
app.add_handler(CommandHandler("promocodes",promo_list))
app.add_handler(CommandHandler("deletepromo",promo_delete))
app.add_handler(CallbackQueryHandler(check_sub_callback,pattern="^check_sub$"))
app.add_handler(CallbackQueryHandler(tower_cb,pattern="^tc_|^tco_|^tn_"))
app.add_handler(CallbackQueryHandler(sell_callback,pattern="^sell_"))
app.add_handler(CallbackQueryHandler(confirm_callback,pattern="^cf_"))
app.add_handler(CallbackQueryHandler(cancel_callback,pattern="^cn_"))
app.add_handler(CallbackQueryHandler(mines_cb,pattern="^mn_|^mco_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text))

print("✅ Бот запущен!")
print(f"💎 1 LMP = {LMP_PRICE} lkoin")
print(f"🔗 Реферальный бонус: {REF_BONUS} lkoin")
print("⏳ Лимит: 20 команд в минуту")
print("🔑 Система промокодов активна!")
print(f"📢 Обязательная подписка: {REQUIRED_CHANNEL}")
print("💣 Игра 'Мины' добавлена!")
app.run_polling()
