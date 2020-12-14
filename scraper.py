from lxml import html
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
from selenium import webdriver
from seleniumrequests import Chrome
from os import path
import time
import urllib
import os
import os.path
import json
import requests
import csv
import io
import random
import string

# Rename the foder and location to whatever you want
SAVE_FOLDER = ".\\Saved-Images"
CSV = '.\\DeviantImages.csv'

def main():

    # Creates a folder if one doesn't already exist
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)


    gallery_url= input("Enter the URL of the gallery you want to scrape: ")
    num_images = int(input("How many images do you want to download? \n"))


    browser = webdriver.Chrome()
    browser.get(gallery_url)
    
    list_of_deviations = browser_scroll(browser)
    #set_of_deviations = set(list_of_deviations)

    print("Number of deviations found on url: " + str(int(len(list_of_deviations)/2)) + '\n')


    # Saving the image name, url, and thread of comments into a csv
    filename = CSV
    with open(filename, 'w', newline='', encoding='UTF-8') as csvfile:
        cw = csv.writer(csvfile)
        cw.writerow(['Image Name', 'Image URL', '', 'Comment Thread'])

        i = 0
        for deviation in list_of_deviations:
            if i % 2 == 0 and i <= num_images*2-1:
                deviation_url = deviation.get('href')
                print("Link: " + str(deviation_url) + '\n')

                image_url, image_name, Comments = download_image_and_comments(deviation_url)

                
                if image_url is not None:
                    #com = io.open('.\\Comments-log.txt', 'r', encoding="utf-8", errors='replace')
                    #comments = com.read()
                    #comments = comments.encode('utf-8')
                    cw.writerow([image_name, image_url, '', str(Comments)])
                    #com.close()
                else:
                    i-=1
            
            i+=1



def browser_scroll(browser):
    final_list = []

    browser_url = browser.current_url

    # Access url, turn it into an html object that can be traversed
    page = requests.get(browser_url)
    gallery_tree = html.fromstring(page.content)

    list_of_deviations = gallery_tree.xpath('//a[@data-hook="deviation_link"]')
    final_list += list_of_deviations

    for i in range(30):
        #scroll down the page, load more images
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        browser_url = browser.current_url

        # Access url, turn it into an html object that can be traversed
        page = requests.get(browser_url)
        gallery_tree = html.fromstring(page.content)

        list_of_deviations = gallery_tree.xpath('//a[@data-hook="deviation_link"]')
        final_list += list_of_deviations

    return final_list
    



def download_image_and_comments(profile):

    print("searching...")

    my_url = profile
    page = requests.get(my_url)


    tree = html.fromstring(page.content)

    # THis will create a list containing number of comments
    num_Comments = tree.xpath('//div[@data-hook="comments_count"]//text()')
    #print("Num_Comments list: " + str(num_Comments) + '\n')
    for count in num_Comments:
        if count.isnumeric():
            num_Comments = int(count)
            break


    # DOESNT WORK
    #print("Number of comments: " + str(num_Comments))


    # This will capture every comment into a list
    Comments1 = tree.xpath('//div[@data-hook="comment_body"]//text()')
    Comments2 = tree.xpath('//p/text()')

    Comments = Comments1 + Comments2


    #num_Comments = len(Comments)
    print("Number of comments: " + str(num_Comments) + '\n')
    print("Number of comments extracted: " + str(len(Comments))+ '\n' )
    #print("Comments: \n" + str(Comments) + '\n')


    # This will capture image url and name
    Image = tree.xpath('//div[@data-hook="art_stage"]//img')
    #print("Image path type: " + str(type(Image)))
    #print("Image path object: " + str(Image))

    # This conditional checks if the expected image is an actual image
    if isinstance(num_Comments, int) and len(Image) > 0 and num_Comments > 14:
        image = Image[0]
        image_url = image.get('src')
        image_name = image.get('alt')
        image_name = image_name.replace(' ', '-')
        image_name = image_name.replace('>', '-')
        image_name = image_name.replace('<', '-')
        image_name = image_name.replace('?', '')
        image_name = image_name.replace('/', '-')
        image_name = image_name.replace('\\', '-')
        image_name = image_name.replace('|', '-')
        image_name = image_name.replace('.', '-')
        image_name = image_name.replace(';', '-')
        image_name = image_name.replace(',', '-')
        image_name = image_name.replace(':', '-')
        image_name = image_name.replace('=', '')

        # This adds a random string of letters at the end so there's no duplicate names
        letters = string.ascii_letters
        letters = ''.join(random.choice(letters) for i in range(4))

        image_name = image_name + letters + '.jpg'

        print("Image Name: \n" + str(image_name) + '\n')
        print("Image URL: \n" + str(image_url) + '\n\n\n')

        # Here we save the image to a local file
        image_location = "D:\Research\DeviantArtScraper\Saved-Images\\" + image_name

        # MAke sure the file doesn't already exist
        if not path.exists(image_location):  
            r = requests.get(image_url)
            with open(image_location, 'wb') as f:
                f.write(r.content)

            return image_url, image_name, Comments


        '''
        wr = io.open(".\\Comments-log.txt", "w", encoding="utf-8", errors='replace')
        wr.write(str(Comments) + '\n')
        '''

        

    # If expected image is a gif or video, we'll return null
    print("Something unexpected happened. Either image is a video/gif, comments are turned off, or image has already been downloaded.\n\n")
    return None, None, None

    


if __name__ == '__main__':
    main()