import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pyvista as pv
import numpy as np
import PIL.Image as Image
import io

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Send me a photo!')


def sphere(update: Update, context: CallbackContext) -> None:
    photos = update.message.photo
    best_photo = None
    for photo in photos:
        if best_photo is None or best_photo['width'] * best_photo['height'] < photo['width'] * photo['height']:
            best_photo = photo
    logger.info(f'Photo from {update.message.from_user.full_name} aka @{update.message.from_user.username} '
                f'({best_photo["height"]}x{best_photo["width"]})')
    image_bytes = best_photo.get_file().download_as_bytearray()
    image = Image.open(io.BytesIO(image_bytes)).transpose(Image.FLIP_LEFT_RIGHT)
    image.save('orig.png')
    tex = pv.read_texture('orig.png')
    sphere_surf = pv.Sphere()
    sphere_surf.texture_map_to_sphere(inplace=True)
    sphere_surf.plot(texture=tex,
                     screenshot='sphere.png',
                     interactive=False,
                     off_screen=True,
                     background=(0, 0, 0, 0),
                     cpos=[(0, 2, 0), (0, 1, 0), (0, 0, -1)],
                     show_axes=False,
                     lighting=False,
                     window_size=(640, 640))
    update.message.reply_photo(photo=open('sphere.png', 'rb'))



def main():
    with open('.bot-token', 'r') as f:
        bot_token = f.readline().strip()

    updater = Updater(bot_token, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.photo, sphere))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
