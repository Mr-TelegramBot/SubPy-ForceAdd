from telebot import TeleBot
from telebot.types import Message
from redis import StrictRedis
from re import match, MULTILINE
from threading import Timer
import info

Token = info.Token
bot = TeleBot(Token)
redis = StrictRedis(decode_responses=True)
manager = info.manager
sudo_list = {198726079} | info.sudo_list
cmds = info.cmds
command_help = info.command_help
help_txt = ''
allows = {}
creators = {}
force_on = set({})


def get_help_text():
    global help_txt
    help_txt = '*🛡دستورات مربوط به صاحب اصلی ربات🛡*\n\n'
    for i in command_help['manager']:
        help_txt += '`📍{0}`\n_🔹{1}_\n\n'.format(i, command_help['manager'][i])
    help_txt += '\n\n*🛡دستورات مربوط به صاحبان ربات🛡*\n\n'
    for i in command_help['sudo']:
        help_txt += '`📍{0}`\n_🔹{1}_\n\n'.format(i, command_help['sudo'][i])
    help_txt += '\n\n*🛡دستورات مربوط به سازنده گروه🛡*\n\n'
    for i in command_help['creator']:
        help_txt += '`📍{0}`\n_🔹{1}_\n\n'.format(i, command_help['creator'][i])


get_help_text()


def cmd(text: str):
    return text[1:].lower() if text[0] in cmds else text.lower()


def is_sudo(user_id: str or int):
    try:
        sudoers = get_sudoers()
        return True if str(user_id) in sudoers or int(user_id) in sudoers else False
    except Exception as error:
        return error


def is_manager(user_id: str or int):
    try:
        if (str(user_id) == manager) or (int(user_id) == manager):
            return True
        return False
    except Exception as error:
        return error


def add_sudo(user_id: str or int, answer_to=None):
    try:
        bid = bot.get_me().id
        redis.sadd('{}:sudoers'.format(bid), user_id)
        sudoers = get_sudoers()
        if type(answer_to) == Message:
            txt = 'کاربر {} با موفقیت به ادمین های اصلی ربات افزوده شد.'.format(
                '[{0}](tg://user?id={0})'.format(user_id))
            try:
                bot.reply_to(answer_to, txt, parse_mode='markdown')
            except:
                bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')
        return user_id in sudoers
    except Exception as error:
        return error


def rem_sudo(user_id: str or int, answer_to=None):
    try:
        bid = bot.get_me().id
        redis.srem('{}:sudoers'.format(bid), user_id)
        sudoers = get_sudoers()
        if type(answer_to) == Message:
            txt = 'کاربر {} با موفقیت از ادمین های اصلی ربات حذف شد.'.format('[{0}](tg://user?id={0})'.format(user_id))
            try:
                bot.reply_to(answer_to, txt, parse_mode='markdown')
            except:
                bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')
        return user_id in sudoers
    except Exception as error:
        return error


def get_sudoers(answer_to=None):
    try:
        bid = bot.get_me().id
        sudoers = sudo_list | redis.smembers('{}:sudoers'.format(bid))
        if type(answer_to) == Message:
            txt = 'ادمین های اصلی ربات:' if sudoers else 'هیچ ادمینی وجود ندارد.'
            for admin in sudoers:
                txt += '\n[{0}](tg://user?id={0})'.format(admin)
            try:
                bot.reply_to(answer_to, txt, parse_mode='markdown')
            except:
                bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')
        return sudoers
    except Exception as error:
        return error


def add_group(chat_id: str or int, answer_to=None):
    try:
        bid = bot.get_me().id
        redis.sadd('{}:groups'.format(bid), chat_id)
        groups = get_groups()
        if type(answer_to) == Message:
            gpname = markdown_escape(answer_to.chat.title)
            txt = 'گروه {0} با موفقیت به گروه های ربات افزوده شد.'.format(gpname)
            try:
                bot.reply_to(answer_to, txt, parse_mode='markdown')
            except:
                bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')
        return chat_id in groups
    except Exception as error:
        return error


def rem_group(chat_id: str or int, answer_to=None):
    try:
        bid = bot.get_me().id
        redis.srem('{}:groups'.format(bid), chat_id)
        groups = get_groups()
        if type(answer_to) == Message:
            gpname = markdown_escape(answer_to.chat.title)
            txt = 'گروه {0} با موفقیت از گروه های ربات حذف شد.'.format(gpname)
            try:
                bot.reply_to(answer_to, txt, parse_mode='markdown')
            except:
                bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')
            txt = 'ربات به دستور مدیر از گروه خارج میشود.'
            bot.send_message(chat_id, txt)
            bot.leave_chat(chat_id)
        return chat_id in groups
    except Exception as error:
        return error


def get_groups(answer_to=None):
    try:
        bid = bot.get_me().id
        groups = redis.smembers('{}:groups'.format(bid))
        if type(answer_to) == Message:
            txt = 'گروه های ربات:' if groups else 'هیچ گروهی وجود ندارد.'
            for group in groups:
                txt += '\n{0}'.format(group)
            try:
                bot.reply_to(answer_to, txt, parse_mode='markdown')
            except:
                bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')
        return groups
    except Exception as error:
        return error


def is_creator(chat_id: str or int, user_id: str or int):
    if is_sudo(user_id):
        return True
    if bot.get_chat_member(chat_id, user_id).status == 'creator':
        return True
    else:
        return False


def enable_force_add(chat_id: str or int, answer_to=None):
    redis.sadd('{}:forceadd'.format(bot.get_me().id), chat_id)
    if type(answer_to) == Message:
        txt = 'ادد اجباری با موفقیت فعال شد.'
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def disable_force_add(chat_id: str or int, answer_to=None):
    redis.srem('{}:forceadd'.format(bot.get_me().id), chat_id)
    if type(answer_to) == Message:
        txt = 'ادد اجباری با موفقیت غیرفعال شد.'
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def add_allow(chat_id: str or int, user_id: str or int, answer_to=None):
    redis.sadd('{}:{}-allow'.format(bot.get_me().id, chat_id), user_id)
    if type(answer_to) == Message:
        txt = 'کاربر {} به لیست افراد مجاز اضافه شد.'.format(
            '[{0}](tg://user?id={1})'.format(user_id, user_id))
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def rem_allow(chat_id: str or int, user_id: str or int, answer_to=None):
    redis.srem('{}:{}-allow'.format(bot.get_me().id, chat_id), user_id)
    if type(answer_to) == Message:
        txt = 'کاربر {} از لیست افراد مجاز حذف شد.'.format(
            '[{0}](tg://user?id={1})'.format(user_id, user_id))
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def is_allow(chat_id: str or int, user_id: str or int):
    r = redis.sismember('{}:{}-allow'.format(bot.get_me().id, chat_id), user_id)
    return True if is_creator(chat_id, user_id) else r


def get_allows(chat_id: str or int, answer_to=None):
    try:
        allows = redis.smembers('{}:{}-allow'.format(bot.get_me().id, chat_id))
        if type(answer_to) == Message:
            txt = 'مجاز های گروه:' if allows else 'هیچ فرد مجازی وجود ندارد.'
            for allow in allows:
                txt += '\n[{0}](tg://user?id={0})'.format(allow)
            try:
                bot.reply_to(answer_to, txt, parse_mode='markdown')
            except:
                bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')
        return allows
    except Exception as error:
        return error


def config(chat_id: str or int, answer_to=None):
    admin_count = 0
    for admin in bot.get_chat_administrators(chat_id):
        admin_count += 1
        redis.sadd('{}:{}-allow'.format(bot.get_me().id, chat_id), admin.user.id)
    if type(answer_to) == Message:
        var = 'پیوست' if admin_count == 1 else 'پیوستند.'
        txt = '{0} ادمین به لیست مجاز {1}'.format(admin_count, var)
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def set_add_count(chat_id: str or int, count: int, answer_to=None):
    if count in range(1, 101):
        redis.hset(bot.get_me().id, '{}:count'.format(chat_id), count)
        if type(answer_to) == Message:
            txt = 'تعداد ادداجباری به {} نفر تغییر کرد'.format(count)
            try:
                bot.reply_to(answer_to, txt, parse_mode='markdown')
            except:
                bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def set_warn_msg_delete_time(chat_id: str or int, time: int, answer_to=None):
    if time in range(1, 21):
        redis.hset(bot.get_me().id, '{}:warntime'.format(chat_id), time)
        if type(answer_to) == Message:
            txt = 'زمان حذف خودکار پیام اخطار به {} ثانیه تغییر کرد.'.format(time)
            try:
                bot.reply_to(answer_to, txt, parse_mode='markdown')
            except:
                bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def set_sign(sign: str, answer_to=None):
    redis.hset(bot.get_me().id, 'sign', sign)
    if type(answer_to) == Message:
        txt = 'امضای پیام ها به:\n `{}`  \nتغییر کرد.'.format(sign)
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def del_sign(answer_to=None):
    redis.hdel(bot.get_me().id, 'sign')
    if type(answer_to) == Message:
        txt = 'امضای پیام ها با موافقیت حذف شد.'
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def set_warn_text(chat_id: str or int, text: str, answer_to=None):
    redis.hset(bot.get_me().id, '{}:text'.format(chat_id), text)
    if type(answer_to) == Message:
        txt = 'پیام هشدار به:\n `{}`  \nتغییر کرد.'.format(text)
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def del_warn_text(chat_id: str or int, answer_to=None):
    redis.hdel(bot.get_me().id, '{}:text'.format(chat_id))
    if type(answer_to) == Message:
        txt = 'پیام هشدار با موفقیت حذف شد.'
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def has_access(chat_id: str or int, user_id: str or int):
    count_added = int(redis.scard('{}:{}:{}:count'.format(bot.get_me().id, chat_id, user_id)))
    max_added = 3 if redis.hget(bot.get_me().id, '{}:count'.format(chat_id)) is None else int(
        redis.hget(bot.get_me().id, '{}:count'.format(chat_id)))
    return True if count_added >= max_added else False


def del_msg(msg):
    if redis.sismember('{}:forceadd'.format(bot.get_me().id), msg.chat.id):
        if (not is_creator(msg.chat.id, msg.from_user.id)) and\
                (not is_allow(msg.chat.id, msg.from_user.id)) and\
                (not has_access(msg.chat.id, msg.from_user.id)):
            bot.delete_message(msg.chat.id, msg.message_id)
            t = redis.hget(bot.get_me().id, '{}:text'.format(msg.chat.id))
            t2 = "سلام کاربرعزیز👈 $mention$\n"
            t2 += "برای گفتگو در گروه باید تعداد $max$ عضو درگروه اضافه کنی\n"
            t2 += "> تعدادعضو افزوده شده توسط شما: $added$\n"
            txt = '{}'.format(t or t2)
            txt = txt.replace(
                '$firstname$',
                markdown_escape(msg.from_user.first_name)
            )
            txt = txt.replace(
                '$lastname$',
                markdown_escape('{}'.format(msg.from_user.last_name or ''))
            )
            txt = txt.replace(
                '$username$',
                markdown_escape('{}'.format(msg.from_user.username or ''))
            )
            txt = txt.replace(
                '$max$',
                '{}'.format(redis.hget(bot.get_me().id, '{}:count'.format(msg.chat.id)) or 3)
            )
            txt = txt.replace(
                '$added$',
                str(redis.scard('{}:{}:{}:count'.format(bot.get_me().id, msg.chat.id, msg.from_user.id)))
            )
            txt = txt.replace(
                '$gpname$',
                msg.chat.title
            )
            txt = txt.replace(
                '$mention$',
                '[{0}](tg://user?id={1})'.format(msg.from_user.first_name, msg.from_user.id)
            )
            sign = redis.hget(bot.get_me().id, 'sign')
            sign = '{}'.format(sign or '')
            txt += '\n{}'.format(sign)
            txt = txt
            m = bot.send_message(msg.chat.id, txt, parse_mode='markdown')
            _time = '{}'.format(redis.hget(bot.get_me().id, '{}:warntime'.format(msg.chat.id)) or 3)
            Timer(interval=float(_time), function=bot.delete_message, args=[msg.chat.id, m.message_id]).start()


def get_expire(chat_id: int or str):
    if redis.get('expire:{}'.format(chat_id)) == 'enable':
        exp = redis.ttl('expire:{}'.format(chat_id))
        if exp > 0:
            day = exp // 86400
            a = exp % 86400
            hour = a // 3600
            a = a % 3600
            minute = a // 60
            second = a % 60
            return '{} روز و {} ساعت و {} دقیقه و {} ثانیه'.format(day, hour, minute, second)
        else:
            return 'نامحدود'


def lock_bot(chat_id: str or int, answer_to=None):
    redis.hset('{}'.format(bot.get_me().id), '{}:lockbot'.format(chat_id), 'enable')
    if type(answer_to) == Message:
        txt = 'قفل ربات با موفقیت فعال شد.'
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def unlock_bot(chat_id: str or int, answer_to=None):
    redis.hset('{}'.format(bot.get_me().id), '{}:lockbot'.format(chat_id), 'disable')
    if type(answer_to) == Message:
        txt = 'قفل ربات با موفقیت غیرفعال شد.'
        try:
            bot.reply_to(answer_to, txt, parse_mode='markdown')
        except:
            bot.send_message(answer_to.chat.id, txt, parse_mode='markdown')


def check_charge(msg):
    if is_sudo(msg.from_user.id) or is_manager(msg.from_user.id):
        return
    if not redis.get('expire:{}'.format(msg.chat.id)) == 'enable':
        redis.set('expire:{}'.format(msg.chat.id), 'disable')
        bot.send_message(msg.chat.id, 'شارژ گروه به پایان رسیده است.')
        bot.leave_chat(msg.chat.id)
    else:
        for i in range(0, 4):
            if (i*86400) < redis.ttl('expire:{}'.format(msg.chat.id)) < ((i+1)*86400):
                bot.send_message(msg.chat.id, 'کمتر از {} روز دیگر از شارژ گروه باقی مانده است.'.format(i+1))


def markdown_escape(text):
    text = text.replace("_", "\\_")
    text = text.replace("*", "\\*")
    text = text.replace("`", "\\`")
    return text


@bot.message_handler(content_types=['text'])
def _text(message):
    mtxt = cmd(message.text)
    uid = message.from_user.id
    Timer(30, check_charge, args=[message]).start()
    if redis.get('expire:{}'.format(message.chat.id)) == 'enable':
        del_msg(message)
    if is_manager(uid):
        if match('^addsudo(.*)$', mtxt):
            useid = match('addsudo(.*)', mtxt).group(1).strip()
            if (not useid) and message.reply_to_message:
                add_sudo(message.reply_to_message.from_user.id, message)
            elif useid.isnumeric():
                add_sudo(useid, message)
        elif match('^remsudo(.*)$', mtxt):
            useid = match('remsudo(.*)', mtxt).group(1).strip()
            if (not useid) and message.reply_to_message:
                rem_sudo(message.reply_to_message.from_user.id, message)
            elif useid.isnumeric():
                rem_sudo(useid, message)
    if is_sudo(uid):
        if match('^sudolist$', mtxt):
            get_sudoers(message)
        elif match('^add$', mtxt):
            add_group(message.chat.id, message)
        elif match('^rem$', mtxt):
            rem_group(message.chat.id, message)
        elif match('^charge(\s(\d+)([smhd]))?$', mtxt):
            count = str(match('charge(\s(\d+)([smhd]))?', mtxt).group(2))
            mode = str(match('charge(\s(\d+)([smhd]))?', mtxt).group(3))
            if mode.lower() == 's':
                exp = int(count)
                redis.setex('expire:{}'.format(message.chat.id), int(exp), 'enable')
                txt = 'ربات به مدت {0} ثانیه برای گروه {1} فعال شد.'.format(count, message.chat.id)
            elif mode.lower() == 'm':
                exp = int(count) * 60
                redis.setex('expire:{}'.format(message.chat.id), int(exp), 'enable')
                txt = 'ربات به مدت {0} دقیقه برای گروه {1} فعال شد.'.format(count, message.chat.id)
            elif mode.lower() == 'h':
                exp = int(count) * 60 * 60
                redis.setex('expire:{}'.format(message.chat.id), int(exp), 'enable')
                txt = 'ربات به مدت {0} ساعت برای گروه {1} فعال شد.'.format(count, message.chat.id)
            elif mode.lower() == 'd':
                exp = int(count) * 60 * 60 * 24
                redis.setex('expire:{}'.format(message.chat.id), int(exp), 'enable')
                txt = 'ربات به مدت {0} روز برای گروه {1} فعال شد.'.format(count, message.chat.id)
            else:
                redis.set('expire:{}'.format(message.chat.id), 'enable')
                txt = 'ربات برای همیشه برای گروه {1} فعال شد.'.format(count, message.chat.id)
            try:
                bot.reply_to(message, txt)
            except:
                bot.send_message(message.chat.id, txt)
        elif match('^sign\s(.*)$', mtxt, MULTILINE):
            text = message.text.replace('sign', '').strip()
            if text == '-':
                del_sign(message)
            else:
                set_sign(text, message)
    if is_creator(message.chat.id, message.from_user.id):
        if redis.get('expire:{}'.format(message.chat.id)) == 'enable':
            if match('^leave$', mtxt):
                rem_group(message.chat.id, message)
                pass
            elif match('^force (.*)$', mtxt):
                mode = match('force (.*)', mtxt).group(1)
                if mode == 'on':
                    enable_force_add(message.chat.id, message)
                elif mode == 'off':
                    disable_force_add(message.chat.id, message)
            elif match('^allows$', mtxt):
                get_allows(message.chat.id, message)
                pass
            elif match('^allow$', mtxt):
                if message.reply_to_message:
                    if message.reply_to_message.forward_from:
                        useid = message.reply_to_message.forward_from.id
                    else:
                        useid = message.reply_to_message.from_user.id
                    add_allow(message.chat.id, useid, message)
            elif match('^limit$', mtxt):
                if message.reply_to_message:
                    if message.reply_to_message.forward_from:
                        useid = message.reply_to_message.forward_from.id
                    else:
                        useid = message.reply_to_message.from_user.id
                    rem_allow(message.chat.id, useid, message)
            elif match('^config$', mtxt):
                config(message.chat.id, message)
                pass
            elif match('^setadd\s(\d+)$', mtxt):
                count = match('setadd\s(\d+)', mtxt).group(1)
                if count.isnumeric():
                    count = int(count)
                    set_add_count(message.chat.id, count, message)
            elif match('^time\s(\d+)$', mtxt):
                time = match('time\s(\d+)', mtxt).group(1)
                if time.isnumeric():
                    time = int(time)
                    set_warn_msg_delete_time(message.chat.id, time, message)
            elif match('^text\s(.*)$', mtxt, MULTILINE):
                text = message.text.replace('text', '').strip()
                if text == '-':
                    del_warn_text(message.chat.id, message)
                else:
                    set_warn_text(message.chat.id, text, message)
            elif match('^help$', mtxt):
                txt = help_txt
                try:
                    bot.reply_to(message, txt, parse_mode='markdown')
                except:
                    bot.send_message(message.chat.id, txt, parse_mode='markdown')
            elif match('^menu$', mtxt):
                t1 = '{}'.format(redis.hget(bot.get_me().id, '{}:count'.format(message.chat.id)) or '3(پیشفرض)')
                txt = '{0} : {1}\n'.format('تعداد اد اجباری', t1)
                t1 = '{}'.format(redis.hget(bot.get_me().id, '{}:warntime'.format(message.chat.id)) or '3(پیشفرض)')
                txt += '{0} : {1}\n'.format('زمان حذف پیام اخطار', t1)
                t1 = '{}'.format(redis.sismember('{}:forceadd'.format(bot.get_me().id), message.chat.id) or 'غیرفعال').replace('True', 'فعال').replace('False', 'غیرفعال')
                txt += '{0} : {1}\n'.format('وضعیت اد اجباری', t1)
                t1 = '{}'.format(redis.hget('{}'.format(bot.get_me().id), '{}:lockbot'.format(message.chat.id)) or 'غیرفعال')
                txt += '{0} : {1}\n'.format('وضعیت قفل ربات', t1)
                t1 = '{}'.format(get_expire(message.chat.id))
                txt += '{0} : {1}\n'.format('اعتبار گروه', t1)
                try:
                    bot.reply_to(message, txt, parse_mode='markdown')
                except:
                    bot.send_message(message.chat.id, txt, parse_mode='markdown')
            elif match('^lock bot$', mtxt):
                lock_bot(message.chat.id, message)
            elif match('^unlock bot$', mtxt):
                unlock_bot(message.chat.id, message)


@bot.message_handler(content_types=['new_chat_members'])
def _new_chat_member(message: Message):
    for added in message.new_chat_members:
        if added.id == bot.get_me().id:
            if not is_sudo(message.from_user.id):
                txt = 'برای افزودن این ربات با {} هماهنگ کنید.'.format('[مدیر ربات](tg://user?id={0})'.format(manager))
                try:
                    bot.reply_to(message, txt, parse_mode='markdown')
                except:
                    bot.send_message(message.chat.id, txt, parse_mode='markdown')
                bot.leave_chat(message.chat.id)
        if added.is_bot and redis.hget('{}'.format(bot.get_me().id), '{}:lockbot'.format(message.chat.id)) == 'enable':
            bot.kick_chat_member(message.chat.id, added.id, 0)
        else:
            if not added.is_bot:
                redis.sadd('{}:{}:{}:count'.format(bot.get_me().id, message.chat.id, message.from_user.id), added.id)
                max_added = '{}'.format(redis.hget(bot.get_me().id, '{}:count'.format(message.chat.id)) or 3)
                uadded = str(redis.scard('{}:{}:{}:count'.format(bot.get_me().id, message.chat.id, message.from_user.id)))
                if int(max_added) == int(uadded):
                    txt = 'کاربر گرامی $mention$\n'
                    txt += 'شما با افزودن $max$ کاربر به گروه مجاز به ارسال پیام شدید.'
                    txt = txt.replace(
                        '$mention$',
                        '[{0}](tg://user?id={1})'.format(message.from_user.first_name, message.from_user.id)
                    )
                    txt = txt.replace(
                        '$max$',
                        '{}'.format(redis.hget(bot.get_me().id, '{}:count'.format(message.chat.id)) or 3)
                    )
                    bot.send_message(
                        chat_id=message.chat.id,
                        text=txt,
                        parse_mode='markdown'
                    )


@bot.message_handler(content_types=['audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice',
                                    'location', 'contact', 'left_chat_member', 'new_chat_title',
                                    'new_chat_photo', 'delete_chat_photo', 'group_chat_created', 'pinned_message',
                                    'supergroup_chat_created', 'channel_chat_created', 'migrate_to_chat_id',
                                    'migrate_from_chat_id'])
def _check(message):
    Timer(30, check_charge, args=[message]).start()
    if redis.get('expire:{}'.format(message.chat.id)) == 'enable':
        del_msg(message)


if __name__ == '__main__':
    try:
        print('Bot Starting...')
        bot.polling(True)
    except Exception as error:
        print(error)
        try:
            bot.send_message(manager, '{}'.format(error))
        except:
            pass
