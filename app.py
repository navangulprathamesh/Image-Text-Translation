#store form data in dictionary format and display to user:
from flask import Flask,request,render_template,send_from_directory,send_file,redirect,url_for
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
#import pytesseract
import cv2
import numpy as np
#from pytesseract import Output
import boto3
import img2pdf
import os
import re
import io
import glob
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from pdf2image import convert_from_path
from google_trans_new import google_translator 
#from docx import Document


UPLOAD_FOLDER = 'final/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/',methods=['POST','GET'])
def input():
    return render_template('index.html')

@app.route('/data',methods=['POST','GET'])
def data():
    if request.method == 'POST':
        imagefile =request.files['file']
        lang = request.form['language']
        lang1=request.form['language']
        if lang1 == 'Hindi':
            lang = 'hi'
        elif lang1 == 'Punjabi':
            lang = 'pa'
        elif lang1 == 'Marathi':
            lang = 'mr'
        elif lang1 == "Empty":
            return "select Language"
            pass
        image_path = "./file_upload/" + imagefile.filename
        imagefile.save(image_path)
        global L1
        L1=list(os.path.splitext(image_path))
        image1=np.zeros((800,1000,3), np.uint8)
        if L1[1]== L1[1]== '.png' or L1[1]== '.jpg' or L1[1]== '.jpeg':
            image = cv2.imread(image_path)
            image=cv2.resize(image,(1000,800))
            cv2.imwrite("self.png",image)
            with open(image_path, 'rb') as document:
                imageBytes = bytearray(document.read())
            text = boto3.client('textract')
            response = text.detect_document_text(Document={'Bytes': imageBytes})
            locations=[]
            words=[]
            for i in response["Blocks"]:
                if i["BlockType"] == "LINE":
                    words.append('{}'.format(i["Text"]))
                    locations.append([i["Geometry"]["BoundingBox"]["Width"],i["Geometry"]["BoundingBox"]["Height"],i["Geometry"]["BoundingBox"]["Left"],i["Geometry"]["BoundingBox"]["Top"]])

            text="  ".join(words)
            
            text=list(map(str,text.split("  ")))
            trans=[]
            '''
            translate = boto3.client(service_name='translate', region_name='us-east-2', use_ssl=True)
            for i in text:
                result = translate.translate_text(Text=i, SourceLanguageCode="en", TargetLanguageCode=lang)
                trans.append(result.get("TranslatedText"))
            print(" ".join(trans))
            '''

            translator = google_translator()
           
            for j in text:
                trans.append(translator.translate(j,lang_tgt=lang))

            
            
            list2=[]
            for i in locations:
                (x, y, w, h) = (i[2], i[3], i[0],  i[1])
                image = cv2.rectangle(image, (int(x*1000), int(y*800)), (int((x+w)*1000), int((y+h)*800)), (255, 255, 255), -1)
                image1 = cv2.rectangle(image1, (int(x*1000), int(y*800)), (int((x+w)*1000), int((y+h)*800)), (255, 255, 255), -1)
                list2.append([int(x*1000), int(y*800)])

            #print(list2)
            #cv2.imshow('Img',image1) 
            cv2.imwrite("text1.jpg",image)
            cv2.imwrite("text2.jpg",image1)
            image=cv2.imread("text1.jpg")
            image1=cv2.imread("text2.jpg",0)
            dst = cv2.inpaint(image, image1, 2, cv2.INPAINT_TELEA)
            cv2.imwrite("text3.jpg",dst)
            final = Image.open("text3.jpg")

            #Language to be translated
            if lang == 'mr' :
                font = ImageFont.truetype("Marathi.ttf", 18)
                #print(font)
            elif lang == 'pa' :
                font = ImageFont.truetype("Karmic_Sanj_Black.ttf", 16)
            elif lang == 'hi' :
                font = ImageFont.truetype("Akshar Unicode.ttf", 19)
            
            draw = ImageDraw.Draw(final)
            
            #cv2.imshow('Inpainting result', dst)

            for i in range(len(trans)):
                 draw.text( (list2[i][0],list2[i][1]), trans[i], fill=(0,0,0),font=font)
            final.save("final/final2.jpg")
            os.system("C:/Users/navan/Desktop/DL/Handwrittenrecog/final/final2.jpg")
            print("Done")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            return render_template('abc.html')

        
        elif L1[1]== '.pdf':
            images = convert_from_path(image_path, 500,poppler_path=r'C:\Users\navan\Desktop\DL\Handwrittenrecog\poppler-0.68.0\bin')
            for i in range(len(images)):
                print("Page "+str(i+1)+" processing.....")
                
                
                images[i].save('pdf/output.jpg')
                image=cv2.imread("pdf/output.jpg")
                image=cv2.resize(image,(1000,800))
                with open("pdf/output.jpg", 'rb') as document:
                    imageBytes = bytearray(document.read())
                text = boto3.client('textract')
                response = text.detect_document_text(Document={'Bytes': imageBytes})
                locations=[]
                words=[]
                for j in response["Blocks"]:
                    if j["BlockType"] == "LINE":
                        words.append('{}'.format(j["Text"]))
                        locations.append([j["Geometry"]["BoundingBox"]["Width"],j["Geometry"]["BoundingBox"]["Height"],j["Geometry"]["BoundingBox"]["Left"],j["Geometry"]["BoundingBox"]["Top"]])

                text="  ".join(words)
                
                text=list(map(str,text.split("  ")))
                trans=[]

                translator = google_translator()

                for j in text:
                    trans.append(translator.translate(j,lang_tgt=lang))

                
                
                list2=[]
                for j in locations:
                    (x, y, w, h) = (j[2], j[3], j[0],  j[1])
                    image = cv2.rectangle(image, (int(x*1000), int(y*800)), (int((x+w)*1000), int((y+h)*800)), (255, 255, 255), -1)
                    image1 = cv2.rectangle(image1, (int(x*1000), int(y*800)), (int((x+w)*1000), int((y+h)*800)), (255, 255, 255), -1)
                    list2.append([int(x*1000), int(y*800)])
                
              
                cv2.imwrite("pdf/text1.jpg",image)
                cv2.imwrite("pdf/text2.jpg",image1)
                image=cv2.imread("pdf/text1.jpg")
                image1=cv2.imread("pdf/text2.jpg",0)
                dst = cv2.inpaint(image, image1, 2, cv2.INPAINT_TELEA)
                cv2.imwrite("pdf/text3.jpg",dst)
                final = Image.open("pdf/text3.jpg")
                #Language to be translated
                if lang == 'mr' :
                    font = ImageFont.truetype("Marathi.ttf", 18)
                    #print(font)
                elif lang == 'pa' :
                    font = ImageFont.truetype("Karmic_Sanj_Black.ttf", 16)
                elif lang == 'hi' :
                    font = ImageFont.truetype("Akshar Unicode.ttf", 19)
                
                draw = ImageDraw.Draw(final)

                for j in range(len(trans)):
                    draw.text( (list2[j][0],list2[j][1]), trans[j], fill=(0,0,0),font=font)
                final.save("pdf/Final"+str(i)+".jpg")
                os.remove("pdf/text1.jpg")
                os.remove("pdf/text2.jpg")
                os.remove("pdf/text3.jpg")
                os.remove("pdf/output.jpg")
                print("Image "+str(i+1)+" Inpainted successfully.\n")
            with open("final/Final.pdf","wb") as f:
                f.write(img2pdf.convert(glob.glob("pdf/*.jpg")))
            os.system("C:/Users/navan/Desktop/DL/Handwrittenrecog/final/Final.pdf")
            for file in os.scandir("pdf/"):
                os.remove(file.path)
            print("Final PDF Generated Successfully.")

            return render_template('abc.html')
       
#if L1[1]== L1[1]== '.png' or L1[1]== '.jpg' or L1[1]== '.jpeg':
@app.route('/image/',methods=['POST','GET'])
def hello():
    if L1[1]== '.png' or L1[1]== '.jpg' or L1[1]== '.jpeg':
        path = "final2.jpg"
        return send_from_directory(app.config['UPLOAD_FOLDER'],filename=path, as_attachment=True,cache_timeout=0)
        
    elif L1[1]== '.pdf':
        path = "Final.pdf"
        return send_from_directory(app.config['UPLOAD_FOLDER'],filename=path, as_attachment=True,cache_timeout=0)
    #return send_file(path,as_attachment=True)
             
if __name__ =='__main__':
    app.run(debug=True)    

