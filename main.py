import numpy as np
import cv2
import telebot
import os
import db
import emoji
from config import token
from time import time

bot = telebot.TeleBot(token)
img_name_array = []
#user_time = {'user_id': 'alloved_time', ...}
user_time = {}
time_limit = 5

def colorized(img_name):
    prototxt = './model/colorization_deploy_v2.prototxt'
    model = './model/colorization_release_v2.caffemodel'
    points = './model/pts_in_hull.npy'
    image = './input_images/' + img_name + '.jpg'

    net = cv2.dnn.readNetFromCaffe(prototxt, model)
    pts = np.load(points)

    class8 = net.getLayerId('class8_ab')
    conv8 = net.getLayerId('conv8_313_rh')
    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype('float32')]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype='float32')] #2.606

    image = cv2.imread(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    scaled = image.astype('float32') / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_RGB2LAB)
    resized = cv2.resize(lab, (224, 224)) #224
    L = cv2.split(resized)[0] - 50

    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
    ab = cv2.resize(ab, (image.shape[1], image.shape[0]))

    L = cv2.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2RGB)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype('uint8')

    cv2.imwrite('./input_images/' + img_name + '.jpg', cv2.cvtColor(colorized, cv2.COLOR_RGB2BGR))
    return 0

# not work
def remove_used_photo(img_name):
    global img_name_array
    img_name_array.append(img_name)
    try:
        for img_name in img_name_array:
            print(img_name)
            os.remove('./input_images/' + img_name + '.jpg')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    @bot.message_handler(commands=['start'])
    def start_message(message):
        try:
            check_user = db.check_user(message.from_user.id)
            if check_user:
                # НЕ В ПЕРВЫЙ РАЗ
                bot.send_message(message.chat.id,
                                 text=f'{emoji.FLAG_RUSSIA}Уже всё давно настроено.\n'
                                      f'Отправьте мне свое черно-белое фото, и я его раскрашу'
                                      f'{emoji.RAINBOW}\n\n'
                                      f'{emoji.FLAG_UNITED_STATES}Everything works.\n'
                                      f'Send me your black and white photo, and we will color it'
                                      f'{emoji.RAINBOW}')
            else:
                # В ПЕРВЫЙ РАЗ
                bot.send_message(message.chat.id,
                                 text=f'{emoji.FLAG_RUSSIA}Отправьте мне свое черно-белое фото, и я его раскрашу'
                                      f'{emoji.RAINBOW}\n\n'
                                      f'{emoji.FLAG_UNITED_STATES}Send me your black and white photo, and we will color it'
                                      f'{emoji.RAINBOW}')
                db.add_user(message.from_user.id, message.from_user.username)
        except Exception as e:
            print(repr(e))

    @bot.message_handler(content_types=['photo'])
    def handle_docs_photo(message):
        if message.chat.id not in user_time or user_time[message.chat.id] < time():
            user_time[message.chat.id] = time() + time_limit
            try:
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                print(message)
                img_name = message.photo[0].file_id
                print(img_name)
                src = './input_images/' + img_name + '.jpg'
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)
            except Exception as e:
                print(e)
            bot.send_message(message.chat.id,
                             text=f'{emoji.FLAG_RUSSIA}Мы приступили к обработке, ожидайте...{emoji.ROBOT}\n\n'
                                  f'{emoji.FLAG_UNITED_STATES}We have started processing, please wait...{emoji.ROBOT}')
            colorized(img_name)
            colorized_photo = open('./input_images/' + img_name + '.jpg', 'rb')
            bot.send_photo(message.chat.id, colorized_photo)
            # remove_used_photo(img_name)
        else:
            bot.send_message(message.chat.id,
                             text=f'{emoji.FLAG_RUSSIA}Нельзя отправлять фото чаще 1 раза в {time_limit} секунд{emoji.WARNING}\n\n'
                                  f"{emoji.FLAG_UNITED_STATES}You can't send photos more than once every {time_limit} seconds{emoji.WARNING}")


    bot.polling()
