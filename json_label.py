from matplotlib.pyplot import *
#from fuzzylab import *
#from fuzzy_algocompare import *
#from bilateral_filter import *
#import rospy                      # rospy
import numpy as np                # numpy
import cv2                        # OpenCV2
import matplotlib.pyplot as plt
import scipy.ndimage
import math
import timeit
from numpy import int16
from numpy import uint8
import json
import tkinter as tk
from PIL import ImageTk, Image, ImageDraw, ImageFont
import easygui
import tkinter.font as tkfont
import os
import copy


outputjson = []
coords = None
lane_number = 0
coordinates = None


def confirm_input(image):
	cv2.imshow('Final', image)
	result = easygui.ynbox("Are you sure about the current input?", "Confirmation")
	cv2.destroyAllWindows()
	return result

def handle_answer():
	global lane_number
	try:
		lane_number = int(entry.get())
		window.destroy()
	except ValueError:
		entry.delete(0, tk.END)
		entry.insert(tk.END, "Invalid input. Enter again")

def on_click(event, x, y, flags, param):
	global coords
	if event == cv2.EVENT_LBUTTONDOWN:
		coords = (x, y)
		print("The pixel you clicked is ",coords)
		print("Please press Enter to confirm.")

def on_click_continuous(event, x, y, flags, param):
	global coordinates
	if event == cv2.EVENT_LBUTTONDOWN:
		coordinates.append((x,y))

def get_continuous_coordinates(image):
	global coordinates
	coordinates = []

	cv2.imshow("Click on the image to record coordinates (Press Enter to finish)", image)
	cv2.setMouseCallback("Click on the image to record coordinates (Press Enter to finish)", on_click_continuous)

	while True:
		key = cv2.waitKey(0) & 0xFF

		if key == 13:  # Check if Enter key is pressed
			break

	cv2.destroyAllWindows()
	return coordinates

def decide_all_points(xlist, inputlist):
	ylist = [160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 700, 710]
	#print("Input x = ", xlist)
	for i in range(len(inputlist)):
		yn = find_closest(inputlist[i][1])
		index = ylist.index(yn)
		xlist[index] = inputlist[i][0]
	#print("Updated xlist = ", xlist)
	for j in range(56):
		#print('j = ',j)
		element = xlist[j]
		#print(element)
		elementy = ylist[j]
		#print(elementy)
		if element == 0:
			cnt = j
			#print("The nth is 0", cnt)
			while xlist[cnt+1] ==0:
				cnt += 1
			#print("The nth is not zero", cnt+1)
			nextnonzero_y = ylist[cnt+1]
			nextnonzero_x = xlist[cnt+1]
			#print("next x = ", nextnonzero_x)
			#print("next y = ", nextnonzero_y)
			previous_x = xlist[j-1]
			previous_y = ylist[j-1]
			#print("previous x = ", previous_x)
			#print("previous y = ", previous_y)
			fittedx = round(previous_x-10/(nextnonzero_y-previous_y)*(previous_x-nextnonzero_x))
			xlist[j] = fittedx
	#print("Fitted x = ", xlist)



	return xlist


def save_clicked_number(number):
	# Do something with the clicked number
	global lane_number
	lane_number = number
	print("Clicked number:", number)
	window.destroy()

def find_closest(input):
	y_coordinates = [160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 700, 710]
	lowest = 2000
	coord = 160
	for nb in y_coordinates:
		dif = np.abs(nb-input)
		if dif<lowest:
			lowest = dif
			coord = nb
		else:
			break

	return coord


json_file = 'DR7_label_revise.json' #Edit when change file
y_coordinates = [160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 700, 710]

if os.path.exists(json_file):
	outputjson = []
	with open(json_file, 'r') as file:
		for line in file:
			outputjson.append(json.loads(line))
	frame_nb = len(outputjson)
	#print(outputjson)
	print(frame_nb)
	bottoms = []
	#print(line.type())
	newline = json.loads(line)
	#print("read line - ", line)
	lastframe = newline["lanes"][:]
	#print(lastframe)
	for previous_lane in lastframe:
		while previous_lane[-1] <0:
			previous_lane.pop()
		added = (previous_lane[-1], y_coordinates[len(previous_lane)-1])
		bottoms.append(added)
	#print("read part - ", outputjson)

else:
	outputjson = []
	frame_nb = 0
	bottoms = [(1,710)]


folder = "cropped_dataset/new_D_R_7_figure/frame-"  #Edit when change file

while frame_nb <= 1597: #Edit when change file
	#window = tk.Tk()
	#frame_nb = i+1
	print("Frame number = ", frame_nb)
	filename = folder + str(frame_nb) + ".jpg"
	print("File name = ", filename)
	image = Image.open(filename)
	draw = ImageDraw.Draw(image)
	text = "Frame number " + str(frame_nb) + ". Please input the line number. "
	font = ImageFont.load_default()
	#font.Font(size = 20, weight = "bold")

	text_color = (255, 255, 255)  # White color
	text_width, text_height = draw.textsize(text, font)
	text_x = (image.width - text_width) // 2  # Centered horizontally
	text_y = 10  # 10 pixels below the top edge

	# Draw a rectangle as the background for the text
	rectangle_coords = [(0, 0), (image.width, text_height + 20)]
	draw.rectangle(rectangle_coords, fill=(0, 0, 0))  # Black color

	# Draw the text on the image
	draw.text((text_x, text_y), text, font=font, fill=text_color)

	
	window = tk.Tk()

	photo = ImageTk.PhotoImage(image)
	label = tk.Label(window, image=photo)
	label.pack()

	#entry = tk.Entry(window)
	#entry.pack()
	button_frame = tk.Frame(window)
	button_frame.pack()

	button_font = tkfont.Font(size = 30, weight = "bold")

	for k in range(1,6):
		button = tk.Button(button_frame, text=str(k), width = 5, height = 3, command = lambda  p=k: save_clicked_number(p))
		button.pack(side=tk.LEFT)

	#button = tk.Button(window, text = "Submit", command = handle_answer)
	#button.pack()

	window.mainloop()
	print("Number of lane lines:", lane_number)

	img = cv2.imread(filename)
	
	#cv2.line(img, (0, 160), (img.shape[1], 160), (0, 0, 255), 1)
	#cv2.line(img, (0, 280), (img.shape[1], 280), (0, 0, 255), 1)
	#cv2.line(img, (0, 300), (img.shape[1], 300), (0, 0, 255), 1)
	#cv2.line(img, (0, 320), (img.shape[1], 320), (0, 0, 255), 1)
	#cv2.line(img, (0, 710), (img.shape[1], 710), (0, 0, 255), 1)
	for elements in y_coordinates:
		if elements%20 ==0 or elements == 710:
			cv2.line(img, (0, elements), (img.shape[1], elements), (0, 255, 0), 1)
	lanes_coords = []
	font = cv2.FONT_HERSHEY_SIMPLEX
	font_scale = 1
	color = (255, 255, 255)  # White color
	thickness = 2
	line_type = cv2.LINE_AA
	for multiples in bottoms:
		cv2.circle(img, multiples, radius = 2, color = (255,0,0), thickness = 2)
	for j in range(lane_number):
		text = "Please click the closest point of lane # " + str(j+1) + ". Then press Enter."
		text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
		text_x = int((img.shape[1] - text_size[0]) / 2)  # Centered horizontally
		text_y = text_size[1] + 10  # 10 pixels below the top edge
		cv2.rectangle(img, (0, 0), (img.shape[1], text_size[1] + 20), (0, 0, 0), cv2.FILLED)
		cv2.putText(img, text, (text_x, text_y), font, font_scale, color, thickness, line_type)
		
		this_lane = [0]*56
		print("Please click the closest point of lane #", j+1)
		cv2.namedWindow("Image")
		cv2.setMouseCallback("Image", on_click)
		cv2.imshow("Image", img)
		cv2.waitKey(0)
		closex = coords[0]
		closey = find_closest(coords[1])
		print("Closest point: ", (closex,closey))

		text = "Please click the farthest point of lane # " + str(j+1) + ". Then press Enter."
		cv2.rectangle(img, (0, 0), (img.shape[1], text_size[1] + 20), (0, 0, 0), cv2.FILLED)
		cv2.putText(img, text, (text_x, text_y), font, font_scale, color, thickness, line_type)

		print("Please click the farthest point of lane #", j+1)
		cv2.namedWindow("Image")
		cv2.setMouseCallback("Image", on_click)
		cv2.imshow("Image", img)
		cv2.waitKey(0)
		farx = coords[0]
		fary = find_closest(coords[1])
		print("Farthest point", (farx, fary))
		cv2.destroyAllWindows()

		nexty = closey
		nextx = closex
		#print("nextx = ", nextx)
		#print("nexty = ", nexty)

		while (nexty <= 710) and (nextx >= 0) and (nextx <= img.shape[1]):
			closex = nextx
			closey = nexty
			nexty = nexty + 10
			nextx = nextx + (closex-farx)/(closey-fary)*10
			#print("nextx = ", nextx)
			#print("nexty = ", nexty)
			

			
		closex = int(closex)
		closey = int(closey)
		#print("Final closex = ", closex)
		#print("Final closey = ", closey)


		for elem in range(56):
			if y_coordinates[elem] < fary:
				this_lane[elem] = -2
			elif y_coordinates[elem] == fary:
				this_lane[elem] = farx
			elif y_coordinates[elem] == closey:
				this_lane[elem] = closex
			elif y_coordinates[elem] > closey:
				this_lane[elem] = -2
		cv2.line(img, (closex,closey), (farx, fary), (0,0,255), 2)
		text = "Please click several points along line #" + str(j+1) + ". Then press Enter."
		cv2.rectangle(img, (0, 0), (img.shape[1], text_size[1] + 20), (0, 0, 0), cv2.FILLED)
		cv2.putText(img, text, (text_x, text_y), font, font_scale, color, thickness, line_type)
		print("Plase click a number of points along the lane line")
		#cv2.namedWindow("Image")
		#cv2.setMouseCallback("Image", on_click)
		#cv2.imshow("Image", img)
		#cv2.waitKey(0)
		#cv2.destroyAllWindows()

		clicked_coordinates = get_continuous_coordinates(img)
		print("Clicked coordinates:")
		for n, (x, y) in enumerate(clicked_coordinates):
			print(f"Point {n+1}: ({x}, {y})")
			cv2.circle(img, (x,y), radius = 1, color = (255,255,0), thickness = 2)
		print(clicked_coordinates)
		#cv2.imshow("Image", img)
		#cv2.waitKey(0)
		this_lane = decide_all_points(this_lane, clicked_coordinates)
		lanes_coords.append(this_lane)


		print("This lane = ", this_lane)


	print("All lanes = ", lanes_coords)
	#cv2.destroyAllWindows()
	newinputimage = cv2.imread(filename)
	for lines in lanes_coords:
		for m in range(len(y_coordinates)):
			x = lines[m]
			y = y_coordinates[m]
			cv2.circle(newinputimage, (x,y), radius = 1, color = (255,255,0), thickness = 2)
	#cv2.imshow("Final result", newinputimage)
	cv2.destroyAllWindows()
	if not confirm_input(newinputimage):
		continue
	dictionary = {}
	dictionary['lanes'] = lanes_coords
	dictionary['h_samples'] = y_coordinates
	dictionary['raw_file'] = "frame-" + str(frame_nb) + ".jpg"
	outputjson.append(dictionary)
	#print("output part - ", outputjson)
	with open(json_file, 'w') as fp:
		fp.write('\n'.join(json.dumps(i) for i in outputjson))
	frame_nb += 1
	print("Confirm, input result to dictionary")
	bottoms = []
	saved_coords = copy.deepcopy(lanes_coords)
	for thislanes in saved_coords:
		while thislanes[-1] <0:
			thislanes.pop()
		added = (thislanes[-1], y_coordinates[len(thislanes)-1])
		bottoms.append(added)
	#print(lanes_coords)
	#print(saved_coords)
	print(bottoms)

