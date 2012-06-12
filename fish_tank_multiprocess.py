'''
Created on Jun 7, 2012

@author: thomasdunne
'''
"""

    Object:
            Tank:
                Vars:
                    Array of Fish:
                    Single Water:
                    Shared Array of Faces: (REM: shared, therefore use RLocks)
                        -- Lauch a new thread to try to keep this array as up to date as possible
                Methods:
                    Update Array of Fish:
                    Update Background:
                    Draw:
            Fish:
                Vars:
                    Position:
                    Previous Position:
                    Direction:
                    Original Image: (to avoid repetative scaling induced blur)
                    Drawable Image:
                    Drawable Position:
                Methods:
                    Update: (REM: last position = position, and direction)
                    Draw:
            
            Water:
                Vars:
                    Background objs
                Methods:
                    Update:
                    Draw:

"""

from SimpleCV import Display, Image, HaarCascade, Kinect, pg
import time, threading
from multiprocessing import Process

lock = threading.RLock()


class FaceListUpdater(threading.Thread):
    def __init__(self, parent):
        self.parent = parent
        threading.Thread.__init__(self)
    
    def run(self):
        while self.parent.running == True:
            with lock:
                self.parent.camera_image = self.parent.camera.getImage().flipHorizontal()
                self.parent.face_array = self.parent.camera_image.findHaarFeatures(HaarCascade('face2.xml'))
            print "*************Thread Func***********"
            print "* cam =", self.parent.camera
            print "* cam_img =", self.parent.camera_image
            print "* arr =", self.parent.face_array
            print "***********************************"
            
def prun(parent):
    while parent.running == True:
        with lock:
            parent.camera_image = parent.camera.getImage().flipHorizontal()
            parent.face_array = parent.camera_image.findHaarFeatures(HaarCascade('face2.xml'))
        print "*************Thread Func***********"
        print "* cam =", parent.camera
        print "* cam_img =", parent.camera_image
        print "* arr =", parent.face_array
        print "***********************************"

class Tank():
    def __init__(self, cam):
        self.running = True
        self.camera = cam
        self.camera_image = None
        self.fish_array = []
        self.face_array = []
#        self.face_updater = FaceListUpdater(self)
        self.face_updater = Process(target=prun, args=(self,))
        self.face_updater.start()
#        self._test_run(self)
        print "**************Main Func************"
        print "* cam =", self.camera
        print "* cam_img =", self.camera_image
        print "* arr =", self.face_array
        print "***********************************"
        self.water = Water(self) 

    def __del__(self):
        print "*** DELETING ***"
        self.running = False
        self.face_updater.join()

    def _test_run(self, parent):
        print "calling camera methods..."
        with lock:
            parent.camera_image = parent.camera.getImage().flipHorizontal()
            parent.face_array = parent.camera_image.resize(w=320).findHaarFeatures(HaarCascade('face2.xml'))
            print "updating camera", parent.camera_image

    def update(self):
        #self._test_run(self)
        self.update_fish()
        self.update_background()

    def update_fish(self):
        for fish in self.fish_array:
            fish.update()
    
    def update_background(self):
        if self.water is not None:
            self.water.update()

    def draw(self, canvas):
        if self.water is not None:
            self.water.draw(canvas)
        print "background should be drawn now"
        
        for fish in self.fish_array:
            fish.draw(canvas)

class Fish():
    def __init__(self, image_url):
        self.position = (0, 0)
        self.last_position = (0, 0)
        self.draw_position = (0, 0)
        self.direction = "left"
        self.orig_image = Image(image_url)
        self.draw_image = None

    def update(self):
        self.update_dir()
        self.draw_image = self.draw_image.resize()

        if self.direction == "left":
            self.draw_position = self.position
        
        elif self.dirction == "right":
            # TODO: setup offsets here for image when facing another direction
            self.draw_position = (self.position[0] + 0, self.position[1] + 0)
            pass

    def update_dir(self):
        hor_change = self.position[0] - self.last_position[0]
        # if the difference is more than 10 pixels
        if abs(hor_change) > 10:
            # TODO: can optimise this slightly by checking if == left && horchange is positive
            # (so doesnt flip it every time over 10 pixels in the same direction)
            if self.direction == "left":
                self.direction = "right"
                self.draw_image = self.orig_image.flipHorizontal().copy()
            elif self.direction == "right":
                self.direction = "left"
                self.draw_image = self.orig_image.copy()
            self.last_position = self.position

    def draw(self, canvas):
        self.draw_image.save(canvas)

class Water():
    def __init__(self, parent):
        self.position = (0, 0)
        self.draw_images = []
        self.parent = parent

    def assign(self, image):
        print "Assigned", type(image), "to Water"
        self.draw_images.append(image)

    def update(self):
        """
        print "calling camera methods..."
        print "*************Thread Func***********"
        print "* cam =", cam
        print "* cam_img =", img[0]
        print "* arr =", array[0]
        print "***********************************"
        """
        pass

    def draw(self, canvas):
        with lock:
            self.parent.camera_image.save(canvas)
        for image in self.draw_images:
            print image
            if image is not None:
                with lock:
                    image.save(canvas)

if __name__ == '__main__':

    #disp = Display(flags = pg.FULLSCREEN)
    disp = Display()
    cam = Kinect()
    time.sleep(0.05) 

    fishtank = Tank(cam)
    print "Everything should be initalised..."
    
    while not disp.isDone():
        print "Looping..."
        if disp.mouseLeft:
            fishtank.running = False
            break
        fishtank.update()
        fishtank.draw(disp)
        #time.sleep(0.05)
        #time.sleep(1)


"""
class tfish():
    def __init__(self, image):
        self.image = scv.Image(image)
        self.orig_image_left = scv.Image(image)
        self.orig_image_right = scv.Image(image)#.flipHorizontal()
        self.direction = "left"
        self.pos = (0, 0)
        self.lastpos = (-1, -1)
        self.print_pos = self.pos

    def update(self, newx, newy):
        # the new point is more left than old point
        # therefore we must be swimming left
        if self.pos[0] <= self.lastpos[0]:
            # if we're swimming right
            if self.direction == "right":
                # change fish to swim left
                self.direction = "left"
            # fish should no swim left
        # if should be swimming right
        else:
            # but we are actually swimming left
            if self.direction == "left":
                # flip image to swim right
                self.direction = "right"
            # now we should be swimming right

        if self.direction == "right":
            self.image = self.orig_image_right.resize(h=int(newy*1.25)).copy()#(int(newx * 1.75), int(newy)).copy()
            #self.print_pos = (self.pos[0] + 10 - 50, int(self.pos[1] - 10))
        else:
            self.image = self.orig_image_left.resize(h=int(newy*1.25)).copy()#(int(newx * 1.75), int(newy)).copy()
        self.print_pos = (self.pos[0] + 10, int(self.pos[1] - 10))

        #print "fish is now swimming", self.direction, "from", self.lastpos, "to", self.pos
            

if __name__ == '__main__':

    cam = scv.Kinect()
    disp = scv.Display(flags=scv.pg.FULLSCREEN)
    
    hc = scv.HaarCascade("face2.xml")
    hmouth = scv.HaarCascade("mouth.xml")

    image_mask = scv.Image("fish/alpha_mask_fish.png")
    water_image = scv.Image("fish/water.png")
    water_images = [scv.Image(wa) for wa in ["fish/water1.png", "fish/water2.png", "fish/water3.png"]]
    image_urls = ["fish/fish1.png", "fish/fish2.png", "fish/fish3.png"]
    fish = []
    for url in image_urls:
        fish.append(tfish(url))

    start_time = time.time()        
    water_index = 0
    water_time = 0

    while not disp.isDone():
        ""
            depth = cam.getDepth()
            
            if disp.mouseLeft:
                break
            depth.save(disp)
        ""
            
        image = cam.getImage().flipHorizontal()#.scale(320,240)
        faces = image.findHaarFeatures(hc) # load in trained face file

        #image = image.blit(water_image, pos=(0, 0), alpha=0.5)
            
        water_time += 1
        if water_time == 10:
            water_index += 1
            water_time = 0
            
        if water_index >= len(water_images):
            water_index = 0

        image = image.blit(water_images[water_index], pos=(0, 0), alpha=0.75)
            
        if faces:
            faces.sortArea()
            for index in range(len(faces)):
                face = faces[index]

                facex = face.x - (face.width() / 2)
                facey = face.y - (face.height() / 2)

                voff = face.height() * 0.25
                half = (face.width()/2, face.height()/2)
                image.drawRectangle(face.x-half[0], face.y-half[1]-voff, face.width(), face.height()+voff, colour, thickness, 255)

                index = index % len(fish)

                fish[index].lastpos = fish[index].pos
                fish[index].pos = (int(face.x-half[0]), int(face.y-half[1]-voff))

                fish[index].update(face.width(), face.height()+voff)

                size = fish[index].image.size()            

                #image.blit(fish[index].image, alphaMask=image_mask.scale(fish[index].image.size()[0], fish[index].image.size()[1]).toGray(), pos=fish[index].print_pos)
                    
                if fish[index].direction == "left":
                    image = image.blit(fish[index].image, pos=fish[index].print_pos, alphaMask=image_mask.scale(size[0], size[1]))
                else:
                    image = image.blit(fish[index].image, pos=fish[index].print_pos, alphaMask=image_mask.scale(size[0], size[1]))#).flipHorizontal())

                myFace = face.crop()
                myFace = myFace.crop(0, myFace.height/2, myFace.width, myFace.height/2)
                mouths = myFace.findHaarFeatures(hmouth)
                if mouths:
                    mouths.sortArea()
                    for ind in [-1]:#range(len(mouths)):
                        mouth = mouths[ind]

                        mouthx = facex + mouth.x - (mouth.width() / 2)
                        mouthy = facey + myFace.height + mouth.y - (mouth.height() / 2)

                        image.drawRectangle(mouthx, mouthy, mouth.width(), mouth.height(), scv.Color.BLUE, thickness, -1)
                        image.drawText(str(ind), facex+mouth.x, facey+mouth.y, scv.Color.BLUE, 20)
                            
                        #myFace.drawRectangle(mouth.x-mouth.width()/2, mouth.y-mouth.height()/2, mouth.width(), mouth.height(), scv.Color.BLUE, thickness, -1)
                    #myFace.save(disp)
                else:
                    image.drawText("No mouths detected :O", 20, 20, scv.Color.RED, 20)

        image.save(disp) #display the image
        #time.sleep(0.01) # Let the program sleep for 1 millisecond so the comp

        #findHaarFeatures(self, cascade,scale factor, min neighbors, use canny)
        #img.upload(dest, api key, api secret, verbose)
        #img.smooth(algorithm name, aperature, sigma, spatial sigma, grayscale)
        #img.drawCircle(ctr, rad, color, thickness)

print "Exiting... Freed Kinect Ownership"
"""

