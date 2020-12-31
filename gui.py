import os
import uuid

from PIL import Image
from dearpygui import core as dpg, simple as sdpg

import img2pdf as i2p

_SUPP_IMG = ['jpg', 'jpeg', 'webp', 'gif', 'png']


class I2PFileData:
    def __init__(self, data):
        self.f_dir: str = data[0]
        self.f_name: str = data[1]
        self.path: str = os.path.join(self.f_dir, self.f_name)
        self.uuid: str = str(uuid.uuid4().hex)

        self.ext: str = os.path.splitext(self.f_name)[1][1:]
        self.valid: bool = self.ext in _SUPP_IMG or self.ext == 'pdf'
        self.images = []
        if self.valid:
            if self.ext == 'pdf':
                self.images = i2p.parse_images(self.path)
            else:
                self.images.append(Image.open(self.path))

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.__repr__()


class I2PPageData:
    def __init__(self, file, file_index=0):
        self.file: I2PFileData = file
        self.file_index: int = file_index

    def __repr__(self):
        return '{} # {}'.format(self.file.f_name, self.file_index)

    def __str__(self):
        return self.__repr__()


class Img2PDFApp:
    def __init__(self):
        self.files = []
        self.pages = []
        self.last_preview_image = None

    def __render(self, sender, data):
        dpg.configure_item('##files', items=self.files)
        dpg.configure_item('##pages', items=self.pages)

        if dpg.is_key_released(dpg.mvKey_Escape):
            self.__handle_quit()

    def __handle_quit(self, sender=None, data=None):
        dpg.stop_dearpygui()

    def __file_add(self, sender, data):
        dpg.open_file_dialog(callback=self.__file_add_cb)

    def __file_add_cb(self, sender, data):
        f_path = os.path.join(data[0], data[1])
        f_data = None
        if os.path.exists(f_path) and os.path.isfile(f_path) and data[1] != '.':
            f_data = I2PFileData(data)
        else:
            dpg.set_value(':Status', 'Not a valid file')
            return

        if f_data.valid:
            self.files.append(f_data)
        else:
            del f_data
            dpg.set_value(':Status', 'Not a valid file')

    def __file_add_all_pages(self, sender, data):
        if len(self.files) <= 0:
            return

        selected_id = dpg.get_value('##files')
        file = self.files[selected_id]
        for i in range(len(file.images)):
            self.pages.append(I2PPageData(file, i))

        self.__update_preview()

    def __file_add_page(self, sender, data):
        if len(self.files) <= 0:
            return

        selected_id = dpg.get_value('##files')
        selected_page = dpg.get_value('##add_page_num')
        file = self.files[selected_id]
        if 0 <= selected_id < len(file.images):
            self.pages.append(I2PPageData(file, int(selected_page)))

        dpg.set_value('##pages', len(self.pages)-1)
        self.__update_preview()

    def __file_remove(self, sender, data):
        if len(self.files) <= 0:
            return

        selected_id = dpg.get_value('##files')
        file = self.files[selected_id]
        self.pages = [x for x in self.pages if x.file != file]
        self.files.pop(selected_id)

        self.__update_preview()

    def __page_remove(self, sender, data):
        if len(self.pages) <= 0:
            return

        selected_id = dpg.get_value('##pages')
        self.pages.pop(selected_id)

        dpg.set_value('##pages', selected_id - 1 if selected_id > 0 else 0)

        self.__update_preview()

    def __page_duplicate(self, sender, data):
        if len(self.pages) <= 0:
            return

        selected_id = dpg.get_value('##pages')

        self.pages.insert(selected_id, self.pages[selected_id])
        dpg.set_value('##pages', selected_id + 1)

    def __page_move_up(self, sender, data):
        if len(self.pages) <= 0:
            return

        selected_id = dpg.get_value('##pages')
        if selected_id <= 0:
            return
        t_prev = self.pages[selected_id - 1]
        this = self.pages[selected_id]

        self.pages[selected_id - 1] = this
        self.pages[selected_id] = t_prev

        dpg.set_value('##pages', selected_id - 1)

    def __page_move_down(self, sender, data):
        if len(self.pages) <= 0:
            return

        selected_id = dpg.get_value('##pages')
        if selected_id >= len(self.pages) - 1:
            return
        t_next = self.pages[selected_id + 1]
        this = self.pages[selected_id]

        self.pages[selected_id + 1] = this
        self.pages[selected_id] = t_next

        dpg.set_value('##pages', selected_id + 1)

    def __save_file(self, sender=None, data=None):
        if len(self.pages) <= 0:
            dpg.set_value(':Status', 'No page to save')
            return
        dpg.open_file_dialog(callback=self.__save_file_cb)

    def __save_file_cb(self, sender=None, data=None):
        if data[1] == '.':
            dpg.set_value(':Status', 'Not a valid file')
            dpg.show_logger()
            return

        f_name = os.path.join(data[0], data[1])
        pages = [x.file.images[x.file_index] for x in self.pages]
        i2p.gen_pdf(pages, f_name)

    def __close_app(self, sender=None, data=None):
        self.__handle_quit()

    def __update_preview(self, sender=None, data=None):
        if len(self.pages) <= 0:
            dpg.clear_drawing('page_preview')
            dpg.set_value(':Page number', '-1')
            dpg.set_value(':File', '-1')
            return
        selected_id = dpg.get_value('##pages')
        page = self.pages[selected_id]
        file = page.file
        n_file = os.path.join('gui_assets/', '{}_{}.jpg'.format(file.uuid, page.file_index))
        if not os.path.exists(n_file) and not os.path.isfile(n_file):
            file.images[page.file_index].save(n_file)
        dpg.draw_image('page_preview', n_file, [0, 0], [300, 300])
        dpg.set_value(':Page number', str(page.file_index))
        dpg.set_value(':File', str(file))

        # Not necessarily related, just leaving it here tho since this func
        #  gets called when vital changes occur anyways
        dpg.set_value(':Status', '')

    def show(self):
        if not os.path.exists('gui_assets') or not os.path.isdir('gui_assets'):
            os.mkdir('gui_assets')

        for f in os.listdir('gui_assets'):
            fn = os.path.join('gui_assets', f)
            os.unlink(fn)

        with sdpg.window('Img2PDF GUI'):
            dpg.add_text('Files')
            dpg.add_group('file_list')
            dpg.add_listbox('##files', items=self.files, num_items=5)
            dpg.end()

            dpg.add_same_line()

            dpg.add_group('file_btn')
            dpg.add_button('Add file', callback=self.__file_add, width=120)
            dpg.add_button('Remove selected', callback=self.__file_remove, width=120)
            dpg.add_button('Add all Pages', callback=self.__file_add_all_pages, width=120)
            dpg.add_input_text('##add_page_num', decimal=True, width=57, hint='page #')
            dpg.add_same_line()
            dpg.add_button('Add', callback=self.__file_add_page, width=55)
            dpg.end()

            dpg.add_spacing(count=2)
            dpg.add_separator()
            dpg.add_spacing(count=2)

            dpg.add_text('Pages')
            dpg.add_group('page_list')
            dpg.add_listbox('##pages', items=self.files, num_items=5, callback=self.__update_preview)
            dpg.end()

            dpg.add_same_line()

            dpg.add_group('page_btn')
            dpg.add_button('Move up', callback=self.__page_move_up, width=120)
            dpg.add_button('Move down', callback=self.__page_move_down, width=120)
            dpg.add_button('Duplicate', callback=self.__page_duplicate, width=120)
            dpg.add_button('Remove', callback=self.__page_remove, width=120)
            dpg.end()

            dpg.add_spacing(count=2)
            dpg.add_separator()
            dpg.add_spacing(count=2)

            dpg.add_text('Preview')
            dpg.add_group('preview')
            dpg.add_drawing('page_preview', width=300, height=300)
            dpg.end()

            dpg.add_same_line()

            dpg.add_group('preview_data')
            dpg.add_label_text(':Page number', default_value='-1', color=[255,2585,255])
            dpg.add_label_text(':File', default_value='-1', color=[255,2585,255])
            dpg.end()

            dpg.add_spacing(count=2)
            dpg.add_separator()
            dpg.add_spacing(count=2)

            dpg.add_group('footer_buttons', horizontal=True)
            dpg.add_label_text(':Status', default_value='')
            dpg.add_button('Save', callback=self.__save_file)
            dpg.add_button('Close', callback=self.__close_app)
            dpg.end()

            dpg.set_render_callback(self.__render)
            dpg.set_main_window_size(600, 680)
            dpg.set_main_window_pos(650, 100)
        # dpg.set_theme('Grey')
        dpg.start_dearpygui(primary_window='Img2PDF GUI')


if __name__ == '__main__':
    app = Img2PDFApp()
    app.show()
