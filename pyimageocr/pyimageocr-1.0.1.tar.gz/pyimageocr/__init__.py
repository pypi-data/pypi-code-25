import cv2
import matplotlib.pyplot as plt
import os
class OCR:
    """
    OCR  class
    """
    __mode = ""
    __codename = "pyimageocr"
    __ver = 1.0
    __image = []
    __height, __width, __channels = 0, 0, 0
    rowSegment = []
    colSegment = []
    def __init__(self, mode = "en", accurecy = 60):
        self.__mode = mode
        self.__accurecy = accurecy
    def getImageFormFile(self, filename):
        try:
            img = cv2.imread(filename)
            self.__image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.__height, self.__width, self.__channels = img.shape
            return self.__image
        except Exception:
            print("File Read Error... (Line 24)")
    def thresoldImage(self):
        try:
            sum = 0
            for i in range(0, self.__height):
                for j in range(0, self.__width):
                    sum = sum+ self.__image[i, j]
            thresh = sum/(self.__width*self.__height)
            self.__image = cv2.threshold(self.__image, thresh, 255, cv2.THRESH_BINARY)[1]
        except Exception:
            print("Unknown Execption at line 34")
    def imageShow(self):
        try:
            cv2.namedWindow('image', cv2.WINDOW_NORMAL)
            cv2.imshow('image', self.__image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception:
            print("System can't detect any compatible version of OpenCV")

    def compressInt(self, number):
        remove  = []
        for i in range(0, len(number)-1):
            if abs(number[i] - number[i+1]) < 3:
                remove.append(number[i+1])
        for i in range(0, len(remove)):
            number.remove(remove[i])
                
        return number
    def getNoOfFile(self, path):
        path, dirs, files = os.walk(path).__next__()
        return len(files)
        
    def save(self, image, path):
        num = str(self.getNoOfFile(path)+1)
        cv2.imwrite("__pycache__/tmp.jpg",image)
        main = cv2.imread("__pycache__/tmp.jpg")
        main = cv2.resize(main, (64, 64))
        cv2.imwrite(path+"/"+num+".jpg",main)

    def pattern_match(self, image):
        cv2.imwrite("__pycache__/tmp.jpg",image)
        main = cv2.imread("__pycache__/tmp.jpg")
        main = cv2.resize(main, (64, 64))
        cv2.imwrite("__pycache__/tmp.jpg",main)
        main = cv2.imread("__pycache__/tmp.jpg")
        main = cv2.cvtColor(main, cv2.COLOR_BGR2GRAY)
        for i in range(ord('A'), ord('Z')+1):
            for j in range(1, self.getNoOfFile("img/"+chr(i))+1):
                if os.path.exists("img/"+chr(i)+"/"+str(j)+".jpg"):
                    img = cv2.imread("img/"+chr(i)+"/"+str(j)+".jpg")
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    match = main == img
                    per = sum(sum(match))*100/4096
                    if per > self.__accurecy:
                        return [chr(i), per]
        return None

    def getRows(self):
        frequency, space = [], []
        line = 0
        segment = []
        start , end =0,0
        for i in range(0, self.__height):
            tmp = []
            row_freq = 0
            for j in range(0, self.__width):
                if(self.__image[i, j] == 0):
                    row_freq += 1
            frequency.append(row_freq)
            space.append(self.__height-i)
            
            if line == 0 and row_freq > 5:
                start = i - 5         #crop with margin ex i-5
                line = 1
            elif line == 1 and row_freq < 5:
                line = 0
                end=i + 5             #crop with margin ex i+5
                tmp.append(start)
                tmp.append(end)
                segment.append(tmp[:])
                
        plt.barh(space, frequency, align='center', alpha=0.5)
        plt.show()
        return (segment)
        
    def getWord(self, image):
        
        height, width = image.shape
        frequency, space = [], []
        line = 0
        segment = []
        start , end =0,0
        for i in range(0, width):
            tmp = []
            row_freq = 0
            for j in range(0, height):
                if(image[j, i] == 0):
                    row_freq += 1
            frequency.append(row_freq)
            space.append(i)
            
            if line == 0 and row_freq > 3:
                start = i - 3             #crop with margin ex -3
                line = 1
            elif line == 1 and row_freq < 3:
                line = 0
                end=i + 3         #crop with margin ex i +3
                tmp.append(start)
                tmp.append(end)
                segment.append(tmp[:])
        
        for i in range(len(segment)):
            charecter = self.pattern_match(image[0:height, segment[i][0]:segment[i][1]])
            if charecter == None:
                cv2.namedWindow('What is This Text ?', cv2.WINDOW_NORMAL)
                cv2.imshow('What is This Text ?', image[0:height, segment[i][0]:segment[i][1]])
                tmpChar = chr(cv2.waitKey())
                cv2.destroyAllWindows()
                if tmpChar != ".":
                    self.save(image[0:height, segment[i][0]:segment[i][1]], "img/"+tmpChar)
            else:
                print(charecter)
        return
    def getimageHistogram(self):
        self.rowSegment = self.getRows()
        for i in range(len(self.rowSegment)):
            self.getWord(self.__image[self.rowSegment[i][0]:self.rowSegment[i][1], 0:self.__width]);