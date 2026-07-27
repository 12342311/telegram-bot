import json,os,random,time
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,CommandHandler,MessageHandler,CallbackQueryHandler,filters

TOKEN="8804943669:AAGNV_N2IRF5KkUSBSE9kQby5K-7est-RIs"
OWNER_ID=8551856799;STAR_PRICE=1500;LMP_PRICE=1000;REF_BONUS=1000;START_BALANCE=100;DB="users.json";TOWER_GAMES={}
USER_COMMANDS={}

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

async def start(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
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

async def commands_list(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 await u.message.reply_text("📋 ДОСТУПНЫЕ КОМАНДЫ\n\n🎮 ИГРЫ:\nкраш <ставка> <множитель>\nкраш всё\nбашня <ставка>\nлотерея\nслоты <ставка>\n\n💰 ФИНАНСЫ:\nбаланс / б / бал\nпоинт - LMP\nбонус\nдонат <⭐>\n\n🔗 РЕФЕРАЛКА:\nреф - ссылка\nрефы - статистика\n\n🏪 ОБМЕННИК:\nобменник\n\n📊 ИНФО:\nигры\nтоп")

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
 await u.message.reply_text(f"🎮 ДОСТУПНЫЕ ИГРЫ\n\n1️⃣ КРАШ\nкраш <ставка> <множитель>\nкраш всё\n\n2️⃣ БАШНЯ\nбашня <ставка>\nбашня всё\n7 уровней\n\n3️⃣ ЛОТЕРЕЯ\nлотерея\nПриз 1000 lkoin, 6ч перезарядка\n\n4️⃣ СЛОТЫ\nслоты <ставка>\n777 - x5, три одинаковых - x2\n\n💎 1 LMP = {LMP_PRICE} lkoin")

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
 await u.message.reply_text(f"💎 {d.get('lmp',0)} LMP\n1 LMP = {LMP_PRICE} lkoin")

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

async def lottery(u,c):
 if not can_send_command(u.effective_user.id):return await u.message.reply_text("⏳ Подожди 1 минуту!")
 uid=u.effective_user.id;d=get_user(uid);now=int(time.time())
 d["games"]=d.get("games",0)+1
 if d.get("lottery",0)and(now-d["lottery"])<21600:
  left=21600-(now-d["lottery"]);return await u.message.reply_text(f"⏳ {left//3600}ч {(left%3600)//60}мин")
 win=random.randint(0,2);kb=[[InlineKeyboardButton("❓",callback_data=f"l_{uid}_{win}_{i}")for i in range(3)]]
 await u.message.reply_text("🎰 ЛОТЕРЕЯ\n💰 Приз: 1000 lkoin",reply_markup=InlineKeyboardMarkup(kb))

async def lottery_cb(update,context):
 q=update.callback_query;data=q.data
 if data.startswith("l_"):
  _,uid,w,c=data.split("_")
  if not can_send_command(int(uid)):return await q.answer("⏳ Подожди 1 минуту!")
  if int(uid)!=q.from_user.id:return await q.answer("❌ Не твоя!")
  kb=[[InlineKeyboardButton("💰1000"if i==int(w)else"❌",callback_data="done")for i in range(3)]]
  d=get_user(uid)
  if int(c)==int(w):
   d["balance"]=d.get("balance",0)+1000;d["lottery"]=int(time.time());save()
   await q.edit_message_text(f"🎉 +1000 lkoin\n💰 {fmt(d.get('balance',0))} lkoin\n⏳ 6ч",reply_markup=InlineKeyboardMarkup(kb))
  else:
   d["lottery"]=int(time.time());save()
   await q.edit_message_text(f"😢 ПРОИГРЫШ\n💰 {fmt(d.get('balance',0))} lkoin\n⏳ 6ч",reply_markup=InlineKeyboardMarkup(kb))
  await q.answer()

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
 TOWER_GAMES[gid]={"user_id":u.effective_user.id,"bet":b,"bomb":random.randint(0,4),"level":0,"revealed":[],"rows":1}
 await show_tower(u,c,gid,0)

async def show_tower(update,context,gid,is_callback):
 g=TOWER_GAMES.get(gid)
 if not g:return
 kb=[]
 for r in range(g["rows"]):
  row=[]
  for i in range(5):
   key=f"{r}_{i}"
   if key in g["revealed"]:
    if g["bomb"]==i and r==g["rows"]-1:
     row.append(InlineKeyboardButton("💣",callback_data="done"))
    else:
     row.append(InlineKeyboardButton("✅",callback_data="done"))
   elif r==g["rows"]-1 and len([x for x in g["revealed"] if x.startswith(f"{r}_")])>0:
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
  if not g or g["user_id"]!=q.from_user.id:return await q.answer("❌ Не твоя игра!")
  if not can_send_command(g["user_id"]):return await q.answer("⏳ Подожди 1 минуту!")
  key=f"{r}_{c}"
  if key in g["revealed"]:return await q.answer("❌ Уже открыто!")
  if r==g["rows"]-1 and len([x for x in g["revealed"] if x.startswith(f"{r}_")])>0:
   return await q.answer("❌ В этом ряду уже открыта клетка!")
  g["revealed"].append(key)
  if g["bomb"]==c and r==g["rows"]-1:
   await q.answer("💣 БОМБА!");d=get_user(g["user_id"]);d["losses"]=d.get("losses",0)+g["bet"];save()
   kb=[[InlineKeyboardButton("💣"if g["bomb"]==i else"✅",callback_data="done")for i in range(5)]for _ in range(g["rows"])]
   await q.edit_message_text(f"🏗️ БАШНЯ\n💰 {fmt(g['bet'])} lkoin\n💥 ПРОИГРЫШ!\n❌ Потерял {fmt(g['bet'])} lkoin",reply_markup=InlineKeyboardMarkup(kb))
   del TOWER_GAMES[gid];return
  g["level"]+=1
  if g["level"]<7:g["rows"]+=1
  if g["level"]>=7:
   w=int(g["bet"]*TOWER_MULT[6]);d=get_user(g["user_id"]);d["balance"]=d.get("balance",0)+w;save()
   kb=[[InlineKeyboardButton("💣"if g["bomb"]==i else"✅",callback_data="done")for i in range(5)]for _ in range(g["rows"])]
   await q.edit_message_text(f"🏗️ БАШНЯ\n💰 {fmt(g['bet'])} lkoin\n🎉 ПОБЕДА!\n📈 x{TOWER_MULT[6]}\n💎 +{fmt(w)} lkoin",reply_markup=InlineKeyboardMarkup(kb))
   del TOWER_GAMES[gid];return
  await q.answer(f"✅ Уровень {g['level']}/7!")
  await show_tower(q,context,gid,1)
 elif data.startswith("tco_"):
  p=data.split("_");gid=f"{p[1]}_{p[2]}"
  g=TOWER_GAMES.get(gid)
  if not g or g["user_id"]!=q.from_user.id:return await q.answer("❌ Не твоя игра!")
  if not can_send_command(g["user_id"]):return await q.answer("⏳ Подожди 1 минуту!")
  if g["level"]<=0:return await q.answer("❌ Открой клетку!")
  m=TOWER_MULT[g["level"]-1];w=int(g["bet"]*m);d=get_user(g["user_id"]);d["balance"]=d.get("balance",0)+w;save()
  kb=[[InlineKeyboardButton("💣"if g["bomb"]==i else"✅",callback_data="done")for i in range(5)]for _ in range(g["rows"])]
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
 if not c.args:return await u.message.reply_text("👑 АДМИН\n\nвыдать <ID> <сумма>\nвыдать_lmp <ID> <сумма>\nзабрать <ID> <сумма>\nстатистика\nсброс <ID>\nобнулить\nрассылка <текст>")
 
 cmd=c.args[0].lower()
 
 if cmd=="статистика":
  total_lkoin=sum(d.get("balance",0)for d in users.values())
  total_lmp=sum(d.get("lmp",0)for d in users.values())
  total_games=sum(d.get("games",0)for d in users.values())
  total_refs=sum(d.get("refs",0)for d in users.values())
  await u.message.reply_text(f"📊 СТАТИСТИКА\n\n👥 Пользователей: {len(users)}\n💰 lkoin: {fmt(total_lkoin)}\n💎 LMP: {fmt(total_lmp)}\n🎮 Игр: {total_games}\n👥 Рефов: {total_refs}")
 
 elif cmd=="выдать"and len(c.args)==3:
  try:
   uid=c.args[1];amount=int(c.args[2])
   if amount<=0:return await u.message.reply_text("❌ Сумма >0!")
   d=get_user(uid);d["balance"]=d.get("balance",0)+amount;save()
   await u.message.reply_text(f"✅ Выдано {amount} lkoin пользователю {uid}")
  except:await u.message.reply_text("❌ Ошибка!")
 
 elif cmd=="выдать_lmp"and len(c.args)==3:
  try:
   uid=c.args[1];amount=int(c.args[2])
   if amount<=0:return await u.message.reply_text("❌ Сумма >0!")
   d=get_user(uid);d["lmp"]=d.get("lmp",0)+amount;save()
   await u.message.reply_text(f"✅ Выдано {amount} LMP пользователю {uid}")
  except:await u.message.reply_text("❌ Ошибка!")
 
 elif cmd=="забрать"and len(c.args)==3:
  try:
   uid=c.args[1];amount=int(c.args[2])
   if amount<=0:return await u.message.reply_text("❌ Сумма >0!")
   d=get_user(uid)
   if d.get("balance",0)<amount:return await u.message.reply_text(f"❌ У пользователя {d.get('balance',0)} lkoin")
   d["balance"]=d.get("balance",0)-amount;save()
   await u.message.reply_text(f"✅ Забрано {amount} lkoin у {uid}")
  except:await u.message.reply_text("❌ Ошибка!")
 
 elif cmd=="сброс"and len(c.args)==2:
  try:
   uid=c.args[1]
   if uid not in users:return await u.message.reply_text("❌ Пользователь не найден!")
   del users[uid];save()
   await u.message.reply_text(f"✅ Пользователь {uid} удален")
  except:await u.message.reply_text("❌ Ошибка!")
 
 elif cmd=="обнулить":
  try:
   count=0
   for uid in users:
    users[uid]["balance"]=0
    users[uid]["bonus"]=0
    users[uid]["lottery"]=0
    users[uid]["lmp"]=0
    users[uid]["games"]=0
    users[uid]["losses"]=0
    users[uid]["refs"]=0
    count+=1
   save()
   await u.message.reply_text(f"✅ Обнулено {count} пользователей!")
  except:await u.message.reply_text("❌ Ошибка!")
 
 elif cmd=="рассылка"and len(c.args)>=2:
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
  except:await u.message.reply_text("❌ Ошибка!")
 
 else:
  await u.message.reply_text("❌ Неизвестная команда!\n\nвыдать <ID> <сумма>\nвыдать_lmp <ID> <сумма>\nзабрать <ID> <сумма>\nстатистика\nсброс <ID>\nобнулить\nрассылка <текст>")

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
 if t in["бонус"]:return await bonus(u,c)
 if t in["баланс","бал"]:return await balance(u,c)
 if t in["поинт","point"]:return await point(u,c)
 if t in["топ"]:return await top(u,c)
 if t in["донат","дон"]:return await donate(u,c)
 if t in["лотерея","lottery"]:return await lottery(u,c)
 if t in["игры","game"]:return await games(u,c)
 if t in["команды","команда","commands","help"]:return await commands_list(u,c)
 if t in["обменник","exchanger"]:return await exchanger(u,c)
 if t in["реф","ref"]:return await ref_link(u,c)
 if t in["рефы","refs"]:return await ref_stats(u,c)
 if t.startswith("слоты ")or t.startswith("slots "):
  c.args=[t.split()[1]];return await slots(u,c)
 if t.startswith("донат ")or t.startswith("дон "):
  c.args=[t.split()[1]];return await donate(u,c)
 if t.startswith("купить "):
  c.args=[t.split()[1]];return await buy_lmp(u,c)
 if t.startswith("продать "):
  c.args=[t.split()[1]];return await sell_lmp(u,c)
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

app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("bonus",bonus))
app.add_handler(CommandHandler("balance",balance))
app.add_handler(CommandHandler("crash",crash))
app.add_handler(CommandHandler("tower",tower))
app.add_handler(CommandHandler("top",top))
app.add_handler(CommandHandler("donate",donate))
app.add_handler(CommandHandler("lottery",lottery))
app.add_handler(CommandHandler("games",games))
app.add_handler(CommandHandler("game",games))
app.add_handler(CommandHandler("commands",commands_list))
app.add_handler(CommandHandler("admin",admin))
app.add_handler(CommandHandler("point",point))
app.add_handler(CommandHandler("exchanger",exchanger))
app.add_handler(CommandHandler("slots",slots))
app.add_handler(CommandHandler("slot",slots))
app.add_handler(CallbackQueryHandler(lottery_cb,pattern="^l_"))
app.add_handler(CallbackQueryHandler(tower_cb,pattern="^tc_|^tco_|^tn_"))
app.add_handler(CallbackQueryHandler(sell_callback,pattern="^sell_"))
app.add_handler(CallbackQueryHandler(confirm_callback,pattern="^cf_"))
app.add_handler(CallbackQueryHandler(cancel_callback,pattern="^cn_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text))

print("✅ Бот запущен!")
print(f"💎 1 LMP = {LMP_PRICE} lkoin")
print(f"🔗 Реферальный бонус: {REF_BONUS} lkoin")
print("⏳ Лимит: 20 команд в минуту")
app.run_polling()