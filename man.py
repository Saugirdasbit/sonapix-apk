from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.filechooser import FileChooserIconView
import cv2
import numpy as np
from kivy.graphics.texture import Texture

# Fono pašalinimas naudojant OpenCV (GrabCut algoritmą)
def remove_background(image_path):
    image = cv2.imread(image_path)
    mask = np.zeros(image.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = (10, 10, image.shape[1] - 10, image.shape[0] - 10)
    cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    image = image * mask2[:, :, np.newaxis]
    return image

# Objektų šalinimas naudojant OpenCV (Inpaint metodą)
def remove_objects(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]
    image = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)
    return image

# Portreto gerinimas (detalizacijos ir kontrasto stiprinimas)
def enhance_portrait(image_path):
    image = cv2.imread(image_path)
    image = cv2.detailEnhance(image, sigma_s=10, sigma_r=0.15)
    return image

# Juodai baltų nuotraukų spalvinimas su OpenCV spalvų paletėmis
def colorize_bw(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    color_image = cv2.applyColorMap(image, cv2.COLORMAP_JET)
    return color_image

class SonaPixApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        self.filechooser = FileChooserIconView()
        self.filechooser.bind(on_selection=self.load_image)
        self.layout.add_widget(self.filechooser)

        self.image_display = KivyImage()
        self.layout.add_widget(self.image_display)

        self.remove_bg_button = Button(text='Pašalinti foną')
        self.remove_bg_button.bind(on_press=self.remove_bg)
        self.layout.add_widget(self.remove_bg_button)

        self.remove_obj_button = Button(text='Šalinti objektus')
        self.remove_obj_button.bind(on_press=self.remove_obj)
        self.layout.add_widget(self.remove_obj_button)

        self.enhance_button = Button(text='Pagerinti portretą')
        self.enhance_button.bind(on_press=self.enhance)
        self.layout.add_widget(self.enhance_button)

        self.colorize_button = Button(text='Spalvinti BW nuotrauką')
        self.colorize_button.bind(on_press=self.colorize)
        self.layout.add_widget(self.colorize_button)

        return self.layout

    def load_image(self, filechooser, selection):
        if selection:
            self.image_path = selection[0]
            self.update_image(self.image_path)

    def update_image(self, image_path):
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        buf = cv2.flip(image, 0).tobytes()
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.image_display.texture = texture

    def remove_bg(self, instance):
        if hasattr(self, 'image_path'):
            image = remove_background(self.image_path)
            cv2.imwrite("bg_removed.png", image)
            self.update_image("bg_removed.png")

    def remove_obj(self, instance):
        if hasattr(self, 'image_path'):
            image = remove_objects(self.image_path)
            cv2.imwrite("obj_removed.png", image)
            self.update_image("obj_removed.png")

    def enhance(self, instance):
        if hasattr(self, 'image_path'):
            image = enhance_portrait(self.image_path)
            cv2.imwrite("enhanced.png", image)
            self.update_image("enhanced.png")

    def colorize(self, instance):
        if hasattr(self, 'image_path'):
            image = colorize_bw(self.image_path)
            cv2.imwrite("colorized.png", image)
            self.update_image("colorized.png")

if __name__ == '__main__':
    SonaPixApp().run()
