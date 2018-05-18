#################################soar/widgets.py#################################
# soar3.0
#  / widgets.py
# (C) 2006-2008 Michael Haimes
#
# Protected by the GPL
#
#
# ...
# Go ahead, try and sue me
################################################################################

####################################Imports#####################################
from tkinter import *

import form.parallel as parallel
import form.common as common
import form.main
import math
import os
import sys
import time
################################################################################

class DrawingFrame(Frame):
  def __init__(self, parent, width_px, height_px, x_min, x_max, y_min, y_max):
    Frame.__init__(self, parent)
    self.width_px, self.height_px = width_px, height_px
    self.x_min, self.x_max = x_min, x_max
    self.y_min, self.y_max = y_min, y_max
    self.x_scale = self.width_px / (self.x_max - self.x_min)
    self.y_scale = self.height_px / (self.y_max - self.y_min)

    self.canvas = Canvas(self, width=self.width_px, height=self.height_px, background = "white")
    self.canvas.pack()
    
    self.next_id = 0
    self.drawing_tasks = parallel.TaskThread()
    self.drawing_tasks.start()

  def __del__(self):
    self.stop_tasks()

  def stop_tasks(self):
    try:
      self.drawing_tasks.stop()
      self.drawing_tasks.clear()
    except:
      pass
    

  def wrap_and_add_task(self, task):
    def tryTask():
      try:
        task()
      except:
        self.stop_tasks()
#    self.drawing_tasks.add_task(lambda: common.tk_enqueue(task))  
    self.drawing_tasks.add_task(lambda: common.tk_enqueue(tryTask))  

  def px_to_cx(self, x):
    return self.x_scale * (x - self.x_min)

  def py_to_cy(self, y):
    return self.height_px - self.y_scale*(y - self.y_min)

  def tagpair(self):
    returnid, nexttag = self.next_id, "t:"+repr(self.next_id)
    self.next_id += 1
    return returnid, nexttag

  def delete(self, item):
    self.wrap_and_add_task(lambda: self.canvas.delete("t:"+repr(item)))

  def clear(self):
    def tryClear():
      try:
        self.canvas.delete("all")
      except:
        self.stop_tasks()
#    self.drawing_tasks.clear_tasks(lambda: self.canvas.delete("all"))
    self.drawing_tasks.clear_tasks(tryClear)

  def drawPoint(self, x, y, color = "blue"):
    cx, cy = int(self.px_to_cx(x)), int(self.py_to_cy(y))
    returnid, nexttag = self.tagpair()
    def make():
      self.canvas.create_rectangle(cx-1, cy-1, cx+1, cy+1, fill = color, outline = color, tag = nexttag)
    self.wrap_and_add_task(make)
    return returnid

  def draw_text(self, x, y, text, color = "blue"):
    returnid, nexttag = self.tagpair()
    cx, cy = int(self.px_to_cx(x)), int(self.py_to_cy(y))
    def make():
      self.canvas.create_text(cx,cy,
                              text = text,
                              fill = color,
                              tag = nexttag)
    self.wrap_and_add_task(make)
    return returnid

  def drawRect(self, coordinate1, coordinate2, color = "black"):
    (x1,y1) = coordinate1
    (x2,y2) = coordinate2
    returnid, nexttag = self.tagpair()
    cx1, cy1 = int(self.px_to_cx(x1)), int(self.py_to_cy(y1))
    cx2, cy2 = int(self.px_to_cx(x2)), int(self.py_to_cy(y2))
    def make():
      self.canvas.create_rectangle(cx1, cy1, cx2, cy2,
                                   fill = color, tag = nexttag)
    self.wrap_and_add_task(make)
    return returnid

  def drawLine(self, lineParams, color = "black"):
    (a,b,c) = lineParams
    if abs(b) < 0.001:
      startX = int(self.px_to_cx(-c/a))
      endX = int(self.px_to_cx(-c/a))
      startY = int(self.py_to_cy(self.y_min))
      endY = int(self.py_to_cy(self.y_max))
    else:
      startX = int(self.px_to_cx(self.x_min))
      startY = int(self.py_to_cy(- (a * self.x_min + c) / b))
      endX = int(self.px_to_cx(self.x_max))
      endY = int(self.py_to_cy(- (a * self.x_max + c) / b))
    returnid, nexttag = self.tagpair()
    def make():
      self.canvas.create_line(startX, startY, endX, endY,
                              fill = color, tag = nexttag)
    self.wrap_and_add_task(make)
    return returnid

  def draw_line_seg(self, x1, y1, x2, y2, color = "black", width = 2):
    returnid, nexttag = self.tagpair()
    cx1, cy1 = int(self.px_to_cx(x1)), int(self.py_to_cy(y1))
    cx2, cy2 = int(self.px_to_cx(x2)), int(self.py_to_cy(y2))
    def make():
      self.canvas.create_line(cx1, cy1,
                              cx2, cy2,
                              fill = color, width = width,
                              tag = nexttag)
    self.wrap_and_add_task(make)
    return returnid

  def drawUnscaledLineSeg(self, x1, y1, xproj, yproj, color = "black", width = 1):
    returnid, nexttag = self.tagpair()
    cx1, cy1 = int(self.px_to_cx(x1)), int(self.py_to_cy(y1))
    def make():
      self.canvas.create_line(cx1, cy1,
                              cx1+xproj, cy1-yproj,
                              fill = color,
                              width = width, tag = nexttag)
    self.wrap_and_add_task(make)
    return returnid

  def drawUnscaledRect(self, x1, y1, xproj, yproj, color = "black"):
    returnid, nexttag = self.tagpair()
    cx1, cy1 = int(self.px_to_cx(x1)), int(self.py_to_cy(y1))
    def make():
      self.canvas.create_rectangle(cx1-xproj, cy1+yproj,
                                   cx1+xproj, cy1-yproj,
                                   fill = color, tag = nexttag)
    self.wrap_and_add_task(make)
    return returnid

  def draw_robot(self, x, y, noseX, noseY,color = "blue", size = 8):
    windowX, windowY = int(self.px_to_cx(x)), int(self.py_to_cy(y))
    windowNX, windowNY = int(self.px_to_cx(noseX)), int(self.py_to_cy(noseY))
    hsize = int(size)/2   # For once, we want the int division!
    returnida, nexttaga = self.tagpair()
    returnidb, nexttagb = self.tagpair()
    def make():
      self.canvas.create_rectangle(windowX-hsize, windowY-hsize,
                                   windowX+hsize, windowY+hsize,
                                   fill = color, outline = color,
                                   tag = nexttaga)
      self.canvas.create_line(windowX, windowY,
                              windowNX, windowNY,
                              fill=color, width=2, arrow="last",
                              tag = nexttagb)
    self.wrap_and_add_task(make)
    return (returnida, returnidb)

  def recolorRectangle(self, itemnumber, color):
    self.canvas.itemconfig(itemnumber, fill = color, outline = color)

  def recolorLine(self, itemnumber, color):
    self.canvas.itemconfig(itemnumber, fill = color)

  def draw_robotWithNose(self, x, y, theta, color = "blue", size = 6):
    rawx = math.cos(theta)
    rawy = math.sin(theta)
    hx, hy = 0.15, 0.0
    noseX = x+rawx*hx-rawy*hy
    noseY = y+rawy*hx+rawx*hy
    return self.draw_robot(x, y, noseX, noseY, color = color, size = size)

  def postscript(self, filename):
    self.canvas.update()
    self.canvas.postscript(file = filename)

  def pdf(self, filename):
    time.sleep(1.0)
    self.postscript(filename+".ps")
    ret = os.system("ps2pdf "+filename+".ps "+filename+".pdf")
    converted = (ret == 0)
    if not converted:
      ret = os.system("convert "+filename+".ps "+filename+".pdf")
      converted = (ret == 0)
    if converted:
      sys.stdout.write("Done writing file "+filename+".pdf\n")
      #os.system("rm "+filename+".ps")
    else:
      sys.stderr.write("Error converting file from postscript: "+
                       filename+".ps")

class DrawingWindow(Toplevel):
  def __init__(self, w_p, h_p, x_min, x_max, y_min, y_max, title):
    Toplevel.__init__(self)
    self.wm_title(title)
    
    self.drawingframe = DrawingFrame(self, w_p, h_p, x_min, x_max, y_min, y_max)
    self.drawingframe.pack()

    self.delete = self.drawingframe.delete
    self.clear = self.drawingframe.clear
    self.close = self.destroy

    self.drawPoint = self.drawingframe.drawPoint
    self.draw_text = self.drawingframe.draw_text
    self.drawRect = self.drawingframe.drawRect
    self.drawLine = self.drawingframe.drawLine
    self.draw_line_seg = self.drawingframe.draw_line_seg
    self.drawUnscaledLineSeg = self.drawingframe.drawUnscaledLineSeg
    self.drawUnscaledRect = self.drawingframe.drawUnscaledRect
    self.draw_robot = self.drawingframe.draw_robot
    self.draw_robotWithNose = self.drawingframe.draw_robotWithNose
    self.pdf = self.drawingframe.pdf
    self.recolorRectangle = self.drawingframe.recolorRectangle
    self.recolorLine = self.drawingframe.recolorLine
