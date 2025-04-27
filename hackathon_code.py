# pygame start
"""
this module is the program code that runs the fire predictor.
one unique thing about the code is that it's made in pygame and not a library that suits app development,
so it's made like a game. this means that the screen is updated frame-by-frame and is coded as such. 
more on that near the bottom of the program

to follow the line of logic, start at line 330 and go down
main flow of logic:
1. make buttons which the user can enter text into
2. When calculate button is pressed, pass on textbox inputs to calculate_risk() function
3. Normalize user inputs
4. Apply weights to inputs and add them all up
5. display as a percentage and provide graphics followed with margin of error.
"""
import pygame, time
pygame.init()


def main(): # mainloop, all it does it gets user input and calculates
    get_input()



class Button:

    """
    Button class - used for making ediatble text boxes
    User needs to input the x-y position of box, and dimensions
    __init__ also sets up the color, whether box is active, and the text

    """
    buttons_list = []
    def __init__(self,x,y,length,width):
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.color = (60,80,20) # these last 4 are not needed to be initialized by user
        self.typing_active = False
        self.holding_button = False
        self.text = ""

        # automatically add object to the list so that methods can be carried out each object easily
        Button.buttons_list.append(self)
        

    def show_rect(self):
        button = pygame.Rect(self.x, self.y,self.length,self.width)
        # pygame updates every frame, so pressing and holding on button
        # causes it to switch back and forth between T/F for typing_active
        if not (self.check_touching() and pygame.mouse.get_pressed()[0]):
            self.holding_button = False
        
        if self.check_touching() and pygame.mouse.get_pressed()[0]: # if mouse is hovering over box and mousedown
            if not self.holding_button:
                if self.typing_active:
                    self.typing_active = False
                else:
                    self.typing_active = True

                    for obj in Button.buttons_list: # if a box is selected, make all other boxes unselected
                        if obj is not self:
                            obj.typing_active = False

                self.holding_button = True

        if pygame.mouse.get_pressed()[0] and not self.check_touching():
            self.typing_active = False # this variable ensures that the user lets go of the button




        if self.typing_active: # if box is active, make it brighter
            self.color = (160,180,120)
        else:
            self.color = (60,80,20)


        pygame.draw.rect(win,self.color,button) 
        self.typing()
    
    def typing(self):
        # this function allows the user to type numbers into text boxes
        if self.typing_active: # only detect inputs from user if the textbox is active
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]: # if enter key pressed, deactivate box
                self.typing_active = False

            for event in pygame.event.get():

                if event.type == pygame.KEYDOWN: # if any key is pressed (other than enter)

                    if event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1] # remove last char
                    elif event.unicode.isdigit() or event.key == pygame.K_PERIOD: # allow only for numbers or decimal point
                            self.text += event.unicode # add the char that pygame detected


        show_text(self.x+(self.length/2),self.y+(self.width/2),40,(0,0,0),self.text) # show text in middle of box



    def check_touching(self):
        """
        this method returns if the mouse is hovering over a button
        """
        # setup variables  for the if condition
        obj1x = self.x
        obj1y = self.y
        obj1xdist = self.length
        obj1ydist = self.width

        # get mouse coords
        obj2x = get_mouse_coords()[0]
        obj2y = get_mouse_coords()[1]
        obj2xdist = 2
        obj2ydist = 2


        # check if mouse is hovering over box
        if obj1x+obj1xdist > obj2x and obj2x+obj2xdist > obj1x and obj1y < obj2y+obj2ydist and obj2y < obj1y+obj1ydist:
            return True
        else:
            return False


def show_text(x,y,size,color,text):
    """
    this function allows for text to be shown. it's turned into a function because
    pygame has too many steps for making text, so we automated the process

    inputs: x pos, y pos, size of text (ex: 12 pt font), color (r,g,b), and the text itself (str)
    """
    font = pygame.font.SysFont("Times", size)

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))

    win.blit(text_surface, text_rect)


def get_input():
    """
    this function is the main function that handles the entire program (not to be confused with main())


    temp = What is the average high temperature in the region? 
    humidity = 70-What is the average humidity in the region? Enter as a percent. 
    terrain = How steep is the terrain in the region? Enter as a grade percentage. 
    fuel = On a scale of 0-10, how much dry/dead plant matter covers the ground in your region? 
    wind = What is the average high wind speed (in MPH) in the region? 
    rain =  130- How many inches of rain does the region get yearly? 

    
    this function
    """
    
    show_descriptions()
    
    for x in Button.buttons_list: # use the list initialized in Button class to apply method to all objects of the class
        x.show_rect()


    

    calculate_button()
    if calc_pressed and not empty_value(): # if the calculate button has been pressed and none of the textboxes are empty
        # turn textbox inputs into a list
        enviro_data = [temp_b.text,80-float(hum_b.text),ter_b.text,fuel_b.text,wind_b.text,130-float(rain_b.text)]
        calculate_risk(enviro_data)
        

def calculate_risk(factors):
    """
    this is the main function that handles all the equations
    """
    global weights_list
    # maximum values, each value is a reasonable maximum that the user can input
    # ex: reasonable max temp is 100, reasonable max humidity is 80, etc
    max_list = [100,80,20,10,50,130]
    # weights work in the same way in that each one corresponds to its environmental factor
    weights_list = [0.25,0.20,0.08,0.23,0.13,0.11] # must add to 100%, or 1
    # ex: temp is 0.25, meaning temperature contributes to 25% of what causes a wildfire


    normalized_values = normalize(factors, max_list) # turn user inputs into values between 0-1

    final_values = add_weights(normalized_values,weights_list) # apply weights to values (normalized value * weight)
    total_risk = sum(final_values) # add up the normalized*weight values for each input
    # after testing the model, we found that it overshoots for values under ~45% fire risk
    if total_risk < 0.45: 
        total_risk = total_risk /  (20*(0.5-total_risk)) # bring value closer to 0 the closer it is to 0
    
    show_text(900,200,100,(170,150,180),(str(round(total_risk*1000)/10)+"%")) # display these percentages
    show_text(900,285,30,(100,250,180),"Annual fire risk")


    # these if-elif blocks display the fire meter graphic depending on the percent
    if total_risk <= 0.2:
        win.blit(risk_10, (650,250))

    elif total_risk <= 0.4:
        win.blit(risk_30, (650,250))

    elif total_risk <= 0.6:
        win.blit(risk_50, (650,250))

    elif total_risk <= 0.8:
        win.blit(risk_70, (650,250))

    else:
        win.blit(risk_90, (650,250))


    confidence_interval() # calc confidence interval


def empty_value():
    """
    this function is used a few times by other parts of the program
    it's mostly used to check if all the textboxes have some input, since they start as empty
    if thereis at least 1 empty box, then it can't calculate fire risk
    """
    empty_value = False
    for x in Button.buttons_list: # iterate through list of objects
        if x.text == "":
            empty_value = True
    return empty_value


def normalize(data, maximums):
    """
    this function normalizes user inputs into values between 0 and 1
    after this, weights are applied

    function has parameters of data (user input list) and maximums (list of reasonable maximums for user inputs)
    """
    new_data = []

    for x in range(len(data)):
        new_data.append(float(data[x]) / maximums[x]) # part = percent * whole --> user input = normalized value * reasonable maximum
    return new_data # gives back list of normalized values


def add_weights(data,weights):
    """
    some environmental factors have a bigger influence on a wildfire than others
    ex: temperature is more important the terrain ruggedness, so it has a higher weight

    needs arguments of data (list of normalized user inputs) and weights (list of weights for each factor)
    """
    new_data = []

    for x in range(len(data)):
        new_data.append(data[x]*weights[x]) # apply weight by doing: normalized value * weight
    return new_data


def show_descriptions():
    """
    all this function does is give short descriptions to the left of each textbox
    it uses the show_text function to make the process of adding text easier
    """

#x,y,size,color,text
    show_text(125,115,25,(240,240,240),"Avg high temp (F)")
    show_text(125,215,25,(240,240,240),"Avg humidity (%)")
    show_text(150,315,25,(240,240,240),"Avg terrain grade (%)")
    show_text(210,415,25,(240,240,240),"Amount of dry vegetation (0-10)")
    show_text(190,515,25,(240,240,240),"Avg high wind speed (MPH)")
    show_text(165,615,25,(240,240,240),"Annual rainfall (inches)")


def calculate_button():
    """
    this function creates the calculate button
    """

    global calc_pressed, holding_calc
    if not calc_pressed: # this if-else adds a boarder around the button which becomes brighter if calculation is active
        boarder_calc = pygame.Rect(775,40,270,85)
        pygame.draw.rect(win,(130*0.3,230*0.3,100*0.3),boarder_calc)
    else:
        boarder_calc = pygame.Rect(775,40,270,85)
        pygame.draw.rect(win,(130*0.7,230*0.7,100*0.7),boarder_calc)

    # make the actual rectangle for the button with the text of it that says "calculate"
    calc = pygame.Rect(785,50,250,65)
    pygame.draw.rect(win,(230,230,100),calc)
    show_text(785+(250/2), 50+(65/2), 30,(20,10,10),"CALCULATE")

    obj1x = 785
    obj1y = 50
    obj1xdist = 250
    obj1ydist = 65

    obj2x = get_mouse_coords()[0]
    obj2y = get_mouse_coords()[1]
    obj2xdist = 2
    obj2ydist = 2
    # below compound inequality is similar to the check_touching() method in the Button class, it checks if mouse is touching box
    touching = obj1x+obj1xdist > obj2x and obj2x+obj2xdist > obj1x and obj1y < obj2y+obj2ydist and obj2y < obj1y+obj1ydist

    if not touching or not pygame.mouse.get_pressed()[0]: # if box is clicked
        holding_calc = False # make sure that if mouse is held down, the calc_pressed doesn't keep switching between T/F


    if touching and pygame.mouse.get_pressed()[0] and not empty_value() and not holding_calc:
        calc_pressed = not calc_pressed # sets holding calc to true so that the if condition doesn't run again until the mouse is unpressed
        holding_calc = True


def confidence_interval():
    """
    code for finding confidence interval meaning the margin of error that the final risk percentage could have
    we did NOT come up with this formula ourselves, we got it from ChatGPT and we customized it to fit our criteria
    """
    assumed_var = [2,5,1,1,2,5] # amount of variability error we expect, ex assumed_var[0] 
                                # is 2, meaning that we expect temp to vary by 2 degrees
    total_error_squared = 0
    for x in range(6):
        # sum of ((each value in weights list squared) times (each value in variability list squared))
        total_error_squared += (weights_list[x]**2 * assumed_var[x]**2)
    # square root that result
    error_margin = (total_error_squared)**0.5
    error_margin *= 1.96 # 95% confidence interval - z score of 1.96 standard deviations
    show_text(900,600,30,(250,180,230),f"Error margin of {round(error_margin,2)}%") # display that confidence interval
        

def get_mouse_coords(): # return tuple w mouse x and y
    """
    this function simply gets the mouse coordinates and returns them as x and y
    we made this function because we don't want to memorize the syntax :P
    """
    mouse_pos = pygame.mouse.get_pos()

    return mouse_pos


#this segment sets the screen ratio to 1280x720, but screen size can be adjusted to make it fit for smaller screen while having the same ratio
screen_size = 1
SCWID = 1280*screen_size
SCHEI = 720*screen_size

# sets framerate, can be anything really because there are no animations
SLEEP = 0.05

global calc_pressed, holding_calc
calc_pressed = False
holding_calc = False
win = pygame.display.set_mode((SCWID,SCHEI)) # setup window/screen

run = True # this variable is used in below while loop, it decides when to stop the program


# create objects for each textbox
temp_b = Button(400,100,100,50)
hum_b = Button(400,200,100,50)
ter_b = Button(400,300,100,50)
fuel_b = Button(400,400,100,50)
wind_b = Button(400,500,100,50)
rain_b = Button(400,600,100,50)


# these next 25-ish lines load and setup the meter images (the semicircle with an arrow)

#this part sets up what size the meter should be (both the ratio and how the ratio should be scaled)
meter_scale = 5
meter_length = 100*meter_scale
meter_width = 70*meter_scale

# load arrow pointing to first (leftmost - green) section and scale it
risk_10 = pygame.image.load("assets/meter/frame_1.png")
risk_10 = pygame.transform.scale(risk_10,(meter_length,meter_width))

# load arrow pointing to second section and scale it
risk_30 = pygame.image.load("assets/meter/frame_2.png")
risk_30 = pygame.transform.scale(risk_30,(meter_length,meter_width))

# load arrow pointing to second section and scale it
risk_50 = pygame.image.load("assets/meter/frame_3.png")
risk_50 = pygame.transform.scale(risk_50,(meter_length,meter_width))

# load arrow pointing to second section and scale it
risk_70 = pygame.image.load("assets/meter/frame_4.png")
risk_70 = pygame.transform.scale(risk_70,(meter_length,meter_width))

# load arrow pointing to second section and scale it
risk_90 = pygame.image.load("assets/meter/frame_5.png")
risk_90 = pygame.transform.scale(risk_90,(meter_length,meter_width))


"""
this is the loop that runs the entire program (this is a continuation of the docstring at top of program)
pygame runs frame-by-frame, and this while loop does that. every frame, the main() function executes with all the other above functions
"""
while run:
    win.fill((20,35,25))
    time.sleep(SLEEP)
    

    main()
    #run = False


    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # if X button is pressed, set run to False and exit while loop
        
            run = False
    #sometimes the program may not close even after pressing the X button, that is usually because a text box is still selected
    # deselect a textbox by pressing enter or clicking away from it, then try closing it again

pygame.quit() # end program
