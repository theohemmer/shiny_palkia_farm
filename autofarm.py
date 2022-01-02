#!/bin/python3

import cv2
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import nxbt

# top 954 15
# middle 931 463
# bottom 974 940

#|N         NAME            X      Y      R   G   B |
#|0 - example            : 1920   1080   255 255 255|
#|--------------------------------------------------|
#|1 - online             : 521    806    233 0   0  | search top screen brighter than middle and low
#|0 - quit               : 528    517    255 245 18 | search middle screen brighter than top and low
#|1 - online             : 521    806    233 0   0  | search top screen brighter than middle and low
#|2 - link               : 911    650    255 255 136| search bottom screen brighter than top and low
#|3 - developed by       : 1041   414    255 255 255| search r > 200 g > 200 b > 200
#|4 - title screen       : 827    318    255 237 13 | search r > 200 g > 200 b < 100
#|5 - in game            : 570    108    255 255 255| search r > 200 g > 200 b > 200
#|6 - diag before fight  : 1271   977    255 255 255| search r > 200 g > 200 b > 200
#|6 - diag in fight      : 1271   977    255 255 255| search r > 200 g > 200 b > 200
#|7 - fight button       : 1731   647    254 77  55 | search r > 230 g < 100 b < 100
#|8 - palkia color       : 1314   539    240 151 207|

point_x = 0
point_y = 0

def sendMail(img_name, subject, body):
    with open(img_name, 'rb') as f:
        img_data = f.read()
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = 'xxarchitekxx@gmail.com'
    msg['To'] = 'theo.hemmer@epitech.eu'

    text = MIMEText(body)
    msg.attach(text)
    image = MIMEImage(img_data, name="ShinyDetector.png")
    msg.attach(image)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("", "")
    s.sendmail('xxarchitekxx@gmail.com', "theo.hemmer@epitech.eu", msg.as_string())
    s.quit()

def show_coord(event, x, y, flags, param):
    global point_y
    global point_x
    if event == 1:
        print("x: ", x, " y: ", y)
        point_x = x
        point_y = y

lastaction = 0

def sendHome(nx, ctrl_idx):
    global lastaction
    lastaction = 1
    macro = """
    HOME 0.2s
    1.5s
    """
    nx.macro(ctrl_idx, macro)

def sendA(nx, ctrl_idx):
    global lastaction
    lastaction = 2
    macro = """
    A 0.2s
    1.5s
    """
    nx.macro(ctrl_idx, macro)

def sendX(nx, ctrl_idx):
    global lastaction
    lastaction = 3
    macro = """
    X 0.2s
    1.5s
    """
    nx.macro(ctrl_idx, macro)

def sendUP(nx, ctrl_idx):
    global lastaction
    lastaction = 4
    macro = """
    DPAD_UP 0.2s
    1.5s
    """
    nx.macro(ctrl_idx, macro)

def unstuck(nx, ctrl_idx, frame, reset):
    global lastaction
    if reset == True:
        lastaction = 0
        return
    if lastaction == 1:
        sendHome(nx, ctrl_idx)
    if lastaction == 2:
        sendA(nx, ctrl_idx)
    if lastaction == 3:
        sendX(nx, ctrl_idx)
    if lastaction == 4:
        sendUP(nx, ctrl_idx)
    if lastaction == 5:
        time = datetime.now().strftime("%d%m%Y_%H%M%S")
        time = time + ".jpg"
        cv2.imwrite(time, frame)
        sendMail(time, "Personnel - The Shiny farmer is stuck", "Look in the attachement")
    lastaction = 5

def check_pixel(r, g, b, r1, g1, b1):
    if r + 10 >= r1 or r - 10 <= r1:
        if g + 10 >= g1 or g - 10 <= g1:
            if b + 10 >= b1 or b - 10 <= b1:
                return True
    return False

def to_720(coord):
    return int(coord * (2/3))

def main():
    global point_y
    global point_x
    cv2.namedWindow("preview")
    cv2.setMouseCallback("preview", show_coord)

    nx = nxbt.Nxbt()

    ctrl_idx = nx.create_controller(nxbt.PRO_CONTROLLER)
    nx.wait_for_connection(ctrl_idx)

    state = False

    sendHome(nx, ctrl_idx)

    vc = cv2.VideoCapture(0, cv2.CAP_ANY)
    vc.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    vc.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    print(vc.get(cv2.CAP_PROP_BACKEND))

    if vc.isOpened(): # try to get the first frame
        rval, frame = vc.read()
    else:
        rval = False

    check_state = 0
    prev_state = -1
    actual_frame = 0
    total_frame = 0
    number_of_try = 0

    while rval:
        actual_frame += 1
        if check_state != prev_state:
            if check_state == 0:
                number_of_try += 1
                print("Try #", number_of_try)
            prev_state = check_state
            actual_frame = 0
        cv2.imshow("preview", frame)
        if state == False:
            rval, frame = vc.read()
        key = cv2.waitKey(20)
        if actual_frame == 2000 and check_state != 12:
            unstuck(nx, ctrl_idx, frame, False)
        if actual_frame == 4000 and check_state != 12:
            unstuck(nx, ctrl_idx, frame, False)
        if actual_frame == 6000 and check_state != 12:
            unstuck(0, 0, frame, True)
            sendHome(nx, ctrl_idx)
            sendA(nx, ctrl_idx)
            sendA(nx, ctrl_idx)
            sendHome(nx, ctrl_idx)
            total_frame = 0
            check_state = 0
        cv2.circle(frame, (point_x, point_y), 5, (255,0,0), 5)
        (b, g, r) = frame[point_y, point_x]
        #print("Point - ({}, {}) R: {}, G: {}, B: {}".format(point_x, point_y, r, g, b))
        if key == 27: # exit on ESC
            break
        if key == 13:
            unstuck(0, 0, frame, True)
            sendHome(nx, ctrl_idx)
            sendA(nx, ctrl_idx)
            sendA(nx, ctrl_idx)
            sendHome(nx, ctrl_idx)
            check_state = 0
            total_frame = 0
        if check_state == 0:
            (b, g, r) = frame[to_720(806), to_720(521)]
            if r >= 220 and g <= 50 and b <= 50:
                sendX(nx, ctrl_idx)
                check_state = 1
            cv2.putText(frame, "Waiting for home screen", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 1:
            (b, g, r) = frame[to_720(189), to_720(727)]
            if r <= 100 and g <= 100 and b <= 100:
                sendA(nx, ctrl_idx)
                check_state = 2
            cv2.putText(frame, "Waiting for exit confirmation", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 2:
            (b, g, r) = frame[to_720(806), to_720(521)]
            if r >= 220 and g <= 50 and b <= 50:
                sendA(nx, ctrl_idx)
                check_state = 3
            cv2.putText(frame, "Waiting for home screen", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 3:
            (b, g, r) = frame[to_720(650), to_720(911)]
            if r >= 220 and g >= 220 and b <= 220:
                sendA(nx, ctrl_idx)
                check_state = 4
            cv2.putText(frame, "Waiting for player choise", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 4:
            (b, g, r) = frame[to_720(416), to_720(960)]
            (b1, g1, r1) = frame[to_720(15), to_720(954)]
            if r >= 200 and g >= 200 and b >= 200:
                if b1 <= 10 and g1 <= 10 and b1 <= 10:
                    sendA(nx, ctrl_idx)
                    check_state = 5
            cv2.putText(frame, "Waiting for developed by", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 5:
            (b, g, r) = frame[to_720(318), to_720(827)]
            if r >= 200 and g >= 200 and b <= 100:
                sendA(nx, ctrl_idx)
                check_state = 6
            cv2.putText(frame, "Waiting for title screen", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 6:
            (b, g, r) = frame[to_720(108), to_720(570)]
            if r >= 200 and g >= 200 and b >= 200:
                sendUP(nx, ctrl_idx)
                check_state = 7
            cv2.putText(frame, "Waiting for in game", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 7:
            (b, g, r) = frame[to_720(977), to_720(1271)]
            if r >= 200 and g >= 200 and b >= 200:
                sendA(nx, ctrl_idx)
                sendA(nx, ctrl_idx)
                check_state = 8
            cv2.putText(frame, "Waiting for palkia diag", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 8:
            (b, g, r) = frame[to_720(977), to_720(1271)]
            if r != 255 and g != 255 and b != 255:
                check_state = 9
            cv2.putText(frame, "Waiting for fight start", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 9:
            (b, g, r) = frame[to_720(977), to_720(1271)]
            if r >= 200 and g >= 200 and b >= 200:
                check_state = 10
            cv2.putText(frame, "Waiting for palkia diag", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 10:
            total_frame += 1
            (b, g, r) = frame[to_720(647), to_720(1731)]
            (b1, g1, r1) = frame[62, 1072] #coord where taken in 720p
            (b2, g2, r2) = frame[622, 215] #coord where taken in 720p
            (b3, g3, r3) = frame[511, 1158] #coord where taken in 720p
            (b4, g4, r4) = frame[590, 1139] #coord where taken in 720p
            (b5, g5, r5) = frame[670, 1135] #coord where taken in 720p
            if r >= 230 and g <= 100 and b <= 100 \
            and r1 >= 220 and g1 >= 220 and b1 >= 220 \
            and r2 >= 220 and g2 >= 220 and b2 >= 220 \
            and r3 <= 100 and g3 >= 180 and b3 <= 100 \
            and r4 >= 200 and g4 >= 150 and b4 <= 100 \
            and r5 <= 170 and g5 <= 170 and b5 >= 220:
                check_state = 11
            cv2.putText(frame, "Waiting for fight button", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
        if check_state == 11:
            cv2.putText(frame, "In fight after: {} frames".format(total_frame), (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,0,255), 5)
            print("Number of frames: {}".format(total_frame))
            time = datetime.now().strftime("%d%m%Y_%H%M%S")
            time = time + ".jpg"
            cv2.imwrite(time, frame)
            if total_frame >= 160:
                sendMail(time, "Personnel - A shiny as maybe been found", "Look in the attachement")
                check_state = 12
            else:
                sendHome(nx, ctrl_idx)
                check_state = 0
                total_frame = 0
        if check_state == 12:
            cv2.putText(frame, "Shiny!", (0,100), cv2.FONT_HERSHEY_PLAIN, 5, (0,255,0), 5)
    vc.release()
    cv2.destroyWindow("preview")

if __name__ == "__main__":
    main()