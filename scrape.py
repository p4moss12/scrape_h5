import sys
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import io
import numpy as np
from PIL import Image
import h5py
import time


def main(args):
    SCROLL_PAUSE_TIME = 0.1
    try:
        query = args[1]  # arg from command line
        count = int(args[-1])
    except IndexError:
        print('No query specified, please try again...')
        return
    except ValueError:
        print('Incorrect parameters(count)')
        return

    print('Retrieving images...')

    # Selenium
    driver = webdriver.Chrome(executable_path='C:/ChromeDriver/chromedriver.exe')  # create driver
    im_links = []
    im_elems = []
    im_made = 0

    driver.get(f'https://unsplash.com/s/photos/{query}')  # opens search page
    html_elem = driver.find_element_by_tag_name('html')  # get html element

    while len(im_links) < count:
        # extend im_elems with new found elements
        im_elems = driver.find_elements_by_css_selector('img[srcset]')[:count]
        for elem in im_elems[::-1]:  # add links from the back of the list
            if len(im_links) >= count:
                break
            try:
                if not elem.get_attribute('srcset') in im_links:  # check if link is already in list
                    im_links.append(elem.get_attribute('srcset'))  # append link

                    # get image as array
                    data = elem.screenshot_as_png
                    img = Image.open(io.BytesIO(data))
                    numpy_array = np.asarray(img)
                    write_to_hdf(numpy_array,im_made)
                    im_made += 1

            except StaleElementReferenceException:
                pass

        # time.sleep(SCROLL_PAUSE_TIME)
        html_elem.send_keys(Keys.PAGE_DOWN)

    # for count, image in enumerate(im_links):
    #     res = requests.get(image)  # get response object
    #     res.raise_for_status()  # raises exception if fails to download
    #
    #     imfile = open(f'Images/im{count}.jpeg', 'wb')  # open image file for writing, write in binary to keep encoding
    #     for chunk in res.iter_content(100000):  # write in chunks
    #         imfile.write(chunk)
    #     imfile.close()

    print('Done :)')


def write_to_hdf(array, num):
    # Create HDF file
    f = h5py.File('new_file.h5', 'a')

    # IF IMAGE GROUP DOESN'T EXIST, CREATE IT
    if not f.__contains__('Images'):
        img_grp = f.create_group('Images')
    else:
        img_grp = f['Images']

    # CREATING DATA SET
    img_data = img_grp.create_dataset(f'img{num}', array.shape, data=array)

    # SET THE IMAGE ATTRIBUTES
    img_data.attrs['CLASS'] = np.string_('IMAGE')
    img_data.attrs['IMAGE_VERSION'] = np.string_('1.2')
    img_data.attrs['IMAGE_SUBCLASS'] = np.string_('IMAGE_TRUECOLOR')
    img_data.attrs['INTERLACE_MODE'] = np.string_('INTERLACE_PIXEL')
    img_data.attrs['IMAGE_MINMAXRANGE'] = np.array([0, 255], dtype=np.uint8)


if __name__ == '__main__':
    main(sys.argv)
