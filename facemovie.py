'''
Created on 27 mars 2012

@author: jll
'''
import cv
import os
import Guy
from FaceParams import FaceParams

class FaceMovie(object):
    '''
    Main class of the whole application. 
    Contains the core image processing functions.
    Supports the communication layer with the end user interface.
    '''
    def __init__(self, in_folder, out_folder, param_folder):
        '''
        Constructor
        '''
        self.source= in_folder # Source folder for pictures
        self.out = out_folder # Folder to save outputs
        self.params_source = param_folder # Folder in which xml files can be found
        
        self.guys = [] # List of pictures in source folder
        
        # Setting up some default parameters for Face Detection
        self.face_params = FaceParams(self.params_source)
        
        # PLacement of face wanted in the image in the end 
        # Generic is center face = (1/2, 1/4)
        self.x_ratio = 1.0/2
        self.y_ratio = 1.0/4
        
        # Needed minimum size of output image
        self.dim_x = 0
        self.dim_y = 0
        
    def list_guys(self):
        """
        Aims at populating the guys list, using the source folder as an input. 
        Guys list shall be sorted by file name alphabetical order
        """
        try:
            os.path.exists(self.source)
            os.path.isdir(self.source) # checking if folder exists
        except : # find precise exception
            print "ERROR : Source folder not found ! Exiting. . ." 
            sys.exit(0)
            
        # just listing directory. Lets be more secure later
        files = os.listdir(self.source)
        
        # loading images, create Guys and store it into guys
        for token in files :
            image = cv.LoadImage(os.path.join(self.source, token))
            guy_name = os.path.splitext(token)[0]
            a_guy = Guy.Guy(image, guy_name)
         
            # populating guys
            self.guys.append(a_guy)

    def search_faces(self):
        """
        Searches for all faces in the guys we have
        Results to be stored directly in guys
        """
        for a_guy in self.guys:
            a_guy.search_face(self.face_params)
            if a_guy.has_face(): # face(s) have been found
                print "%d faces found for %s" % (a_guy.num_faces(), a_guy.name)
    
    def find_out_dims(self):
        """
        Aims at calculating which size of output image is needed to display 
        outputs, knowing x and y desired ratios, and detected faces centers
        """
        
        for a_guy in self.guys:
            if a_guy.has_face():
                # Working on x                
                x1 = (a_guy.x_center  / self.x_ratio) 
                x2 = 1
                #x2 = ((a_guy.in_x - a_guy.x_center) / (1 - self.x_ratio))
                x_fin = int(max(x1, x2)) + 1 # for borders
                if x_fin > self.dim_x:
                    self.dim_x = x_fin
                    
                # Working on y
                y1 = (a_guy.y_center / self.y_ratio) 
                y2 = ((a_guy.in_y - a_guy.y_center) / (1 - self.y_ratio))
                y_fin = int(max(y1, y2)) + 1 # for borders
                if y_fin > self.dim_y:
                    self.dim_y = y_fin
                
    # Informative functions
    def number_guys(self):
        """
        Simply returns the number of guys in the current to-be movie
        """    
        return len(self.guys)
    
    def show_faces(self, time=1000, debug=True):
        """
        Show all faces that have been found for the guys.
        The time for which each image will be diplayed can be chosen.
        Several modes can be chosen to adapt the result.
        """
        for a_guy in self.guys:
            a_guy.out_display(self.face_params, time, debug=debug)

    def save_faces(self, out_folder, format="png", debug=True):
        """
        Save all faces into out_folder, in the given format
        Debug is used to draw rectangles around found faces
        """
        for a_guy in self.guys:
                a_guy.save_result(self.face_params, 
                                  out_folder, 
                                  format, 
                                  debug)    
                          
    def save_movie(self, out_folder, debug=True):
        """
        Creates a movie with all faces found in the inputs.
        Guy is skipped if no face is found.
        
        TODO : No codec involved !
        Resize should be done somewhere else !
        """
        filename = os.path.join(out_folder, "output.avi")
        fourcc = 0#-1
        fps = 10 # should be less
        frameSize = (self.guys[0].in_x, self.guys[0].in_y) 
        my_video = cv.CreateVideoWriter(filename, 
                                      fourcc, 
                                      fps, 
                                      frameSize,
                                      1) 
        frame = cv.CreateImage(frameSize, 
                               cv.IPL_DEPTH_8U, 
                               3)
        for a_guy in self.guys: 
            if a_guy.has_face():
                a_guy.create_output(self.face_params, debug)
                cv.Resize(a_guy.out_im, frame)
                cv.WriteFrame(my_video, frame)   

if __name__ == "__main__":
    # quick and dirty tests
    root_fo = "C:\Users\jll\perso\FaceMovie"
    in_fo = os.path.join(root_fo, "input\Axel_tsts")
    #in_fo = os.path.join(root_fo, "input\Axel")
    out_fo = os.path.join(root_fo, "output")
    par_fo = os.path.join(root_fo, "haarcascades")
    
    my_movie = FaceMovie(in_fo, out_fo, par_fo)
    my_movie.list_guys()
    my_movie.search_faces()
    # I want to know the size of the output frame, knowing initial conditions
    my_movie.find_out_dims()

    x_center = int(my_movie.dim_x * my_movie.x_ratio)
    y_center = int(my_movie.dim_y * my_movie.y_ratio)
    for a_guy in my_movie.guys:
        a_guy.create_debug_output()
        #a_guy.create_video_output(my_movie.dim_x, my_movie.dim_y, x_center, y_center)
        a_guy.out_display(000)
    
    #my_movie.show_faces(2000)
    #my_movie.save_faces("output", debug=True)
    #my_movie.save_movie("output", debug=True)
    
    print "Done !"
    