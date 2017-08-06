########################################################################
#
# TSP (Travelling Salesman Problem), interactive simulation, uses
# direct sampling and simulated annealing to find (or approach...)
# solution
#
# Peter U., July/August 2017
#
# Version 1.0
#
########################################################################
#
# Import packages:
import random
import math
import pygame
from pygame.locals import *
import timeit
import time
import datetime
import matplotlib.pyplot as plt

########################################################################
# Global settings:
SIZE = 600           # size of display window for single instance
STATUS_HEIGHT = 80   # height of status bar in display window
STATUS_HEIGHT2 = 30  # height of status bar within instance subwindows
STATUS_HEIGHT3 = 45  # height of status bar at the bottom (Github info)
DELIM_WIDTH = 5      # width of delimiter between direct and sim. ann. output
CITY_RADIUS = 5      # radius of circle representing city
FONTSIZE = 20        # font size for control section buttons
VERBOSE = False      # level of chattiness
SAVEPLOT = True      # save plot of tour length vs iteration (True) or only display it (False)
SLEEP = 0            # delay (in seconds) after plotting new configuration
N = 20               # initial number of cities
SEED = None          # random seed
VERSION = "1.0"      # version


########################################################################
# define colors for graphics output:
COLORS = {"WHITE": (255, 255, 255), "RED": (255, 0, 0), "GREEN": (0, 255, 0),
          "BLUE": (0, 0, 255), "BLACK": (0, 0, 0), "YELLOW": (255, 255, 0),
          "LIGHT_BLUE": (0, 125, 227), "GREY1": (120, 120, 120),
          "GREY2": (224, 224, 224), "LIGHTBLUE": (102, 178, 255),
          "LIGHTRED": (255, 153, 153), "LIGHTYELLOW": (255, 255, 153),
          "PINK": (255, 51, 255), "DARKBLUE": (0, 0, 153),
          "LAVENDER": (204, 153, 255), "LIGHTGREEN": (153, 255, 204),
          "BROWN": (102, 51, 0), "OLIVE": (153, 153, 0), "DARKGREY": (105, 105, 105)}


########################################################################
# Helper functions:
def distance(x, y):
    # get Euclidean distance between two points (cities) in 2D space
    return math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)

def tour_length(cities, N):
    # get total tour length for current sequence of cities
    assert len(cities) == N, "WTF?? " + str(len(cities)) + " vs " + str(N)
    return sum(distance(cities[k + 1], cities[k]) for k in range(N - 1)) + distance(cities[0], cities[N - 1])

def draw_text(surface, font, text, position, color):
    # draw user-defined text in pygame graphics surface
    lable = font.render(text, 1, color)
    surface.blit(lable, position)

def generate_cities(N):
    # generate positions for N cities randomly in range .025 <= x <= .975
    # and .025 <= y <= .975 (leave margins at all sides for aesthetics
    # reasons)
    random.seed(SEED)
    cities = [(.025 + random.uniform(0.0, 0.95), .025 + random.uniform(0.0, 0.95)) for i in range(N)]
    random.seed()
    return cities[:]

def change_N(N):
    # change number of cities, so various variables have to be reset
    iters, siters, diters = 0, 0, 0
    d_energy_min, s_energy_min = float('inf'), 10000.
    beta, n_accept = 1.0, 0
    dcities = generate_cities(N)
    scities = dcities[:]
    if VERBOSE: print "Simulating", N, "cities."
    return N, dcities, scities, iters, siters, diters, d_energy_min, s_energy_min, beta, n_accept, timeit.default_timer(), {"direct": {"iters": [], "lengths": []}, "simann": {"iters": [], "lengths": []}}

def get_filename(N, iters):
    # generate file (without extension),
    # contains number of cities, iteration number and timestamp
    filename = "Images/TSP_comparism_N" + str(N) + "_iters" + str(iters) + "_" +  \
               datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return filename

def save_image(surface, N, iters):
    # save current graphics surface as image (PNG format); filename
    filename = get_filename(N, iters) + "_map.png"
    pygame.image.save(surface, filename)
    return filename

def make_plot(plot_data, N, iters):
    # generate plot of minimal tour length vs iteration number for both
    # direct sampling and simulated annealing; plot has log-log-scale;
    # plot is saved to file with filename containing N, iteration and
    # timestamp
    filename = get_filename(N, iters) + "_plot.png"
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xscale("log")
    ax.set_yscale("log")
    xmax = max(plot_data["direct"]["iters"][-1], plot_data["simann"]["iters"][-1])
    x1 = plot_data["direct"]["iters"]
    y1 = plot_data["direct"]["lengths"]
    x2 = plot_data["simann"]["iters"]
    y2 = plot_data["simann"]["lengths"]
    if x1[-1] < x2[-1]:
        x1.append(x2[-1])
        y1.append(y1[-1])
    elif x1[-1] > x2[-1]:
        x2.append(x1[-1])
        y2.append(y2[-1])
    plt.plot(x1, y1, color="red", lw=2, label="direct sampling")
    plt.plot(x2, y2, color="blue", lw=2, label="simulated annealing")
    plt.legend(loc=3, fontsize=16)
    plt.xlabel("iteration", fontsize=16)
    plt.ylabel("minimal tour length", fontsize=16)
    plt.title("Tour length vs iteration", fontsize=20)
    if SAVEPLOT:
        plt.savefig(filename)
    plt.show()
    return filename

    
########################################################################
# Initialisation:
start_timer = timeit.default_timer()
pygame.init()
helv20 = pygame.font.SysFont("Helvetica", 20)
helv24 = pygame.font.SysFont("Helvetica", 24)
# start clock:
fpsClock = pygame.time.Clock()
# set display surface for pygame:
SWIDTH = 2 * SIZE + DELIM_WIDTH
SHEIGHT = SIZE + STATUS_HEIGHT + STATUS_HEIGHT2 + STATUS_HEIGHT3
print SWIDTH, SHEIGHT
surface = pygame.display.set_mode((SWIDTH, SHEIGHT))
surface.set_alpha(None)
pygame.display.set_caption("TSP: direct sampling vs simulated annealing, v" + VERSION)
dcities = generate_cities(N)  # cities for direct sampling
scities = dcities[:]          # cities for simulated annealing



######################################################################
# Button class for control section, PyGame doesn't have ready-to-use
# buttons or similar:
class Button():

    def __init__(self, width, height, text, color, tcolor):
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.tcolor = tcolor

    def SetText(self, text):
        self.text = text

    def PlaceButton(self, surface, x, y):
        self.x = x
        self.y = y
        surface = self.DrawButton(surface, x, y)
        surface = self.ButtonText(surface, x, y)

    def DrawButton(self, surface, x, y):
        pygame.draw.rect(surface, self.color, (x, y, self.width, self.height), 0)
        return surface

    def ButtonText(self, surface, x, y):
        font_size = int(self.width // len(self.text))
        font = pygame.font.SysFont("Arial", FONTSIZE)
        text = font.render(self.text, 1, self.tcolor)
        surface.blit(text, ((x + self.width/2) - text.get_width()/2, (y + self.height/2) - text.get_height()/2))
        return surface

    def IsPressed(self, mouse):
        return mouse[0] > self.x and \
               mouse[1] > self.y and \
               mouse[0] <= self.x + self.width and \
               mouse[1] < self.y + self.height

########################################################################
# simulation step for direct sampling, just randomly shuffle cities,
# i.e. previous configuration has to impact whatsoever on next configuration:
def direct_sampling(cities):
    random.shuffle(cities)
    return cities
    

########################################################################
# simulation step for simulated annealing:
#
# The main part of the code for this function was provided by Werner Krauth
# and his team from Ecole Normale Superieure as part of the course
# "Statistical Mechanics - Algorithms and Computations" which was hosted
# on the Coursera Platform (https://www.coursera.org/course/smac)
# For an explanation of the simulated annealing method see
# https://en.wikipedia.org/wiki/Simulated_annealing
# Basically, in each iteration a "neighbouring" route is chosen and:
# - if it has lower energy than the current route (i.e. is shorter): it is
#   always accepted
# - if it has higher energy than the current route (i.e. is longer): it is
#   accepted with some probability p which depends on the difference in energies
#   and a "temperature" which slowly decreases during the simulation. The
#   parameter beta is basically the inverse temperature
#
def simulated_annealing(N, cities, beta, n_accept, best_energy):
    energy = tour_length(cities, N)
    new_route = False
    if n_accept >= 100 * math.log(N):
        beta *= 1.005
        n_accept = 0
    p = random.uniform(0.0, 1.0)
    if p < 0.2:
        # cut sequence somewhere in first half, swap first and second part,
        # cut again at new point in first half and reverse first part
        i = random.randint(0, N / 2)
        cities = cities[i:] + cities[:i]
        i = random.randint(0, N / 2)
        a = cities[:i]
        a.reverse()
        new_cities = a + cities[i:]
    elif p < 0.6:
        # move randomly chosen city to a randomly chosen new position in sequence
        new_cities = cities[:]
        i = random.randint(1, N - 1)
        a = new_cities.pop(i)
        j = random.randint(1, N - 2)
        new_cities.insert(j, a)
    else:
        # swap two randomly chosen cities
        new_cities = cities[:]
        i = random.randint(1, N - 1)
        j = random.randint(1, N - 1)
        new_cities[i] = cities[j]
        new_cities[j] = cities[i]
    new_energy = tour_length(new_cities, N)
    if random.uniform(0.0, 1.0) < math.exp(- beta * (new_energy - energy)):
        # accept new route with probability depending on difference in
        # tour length (new - current) and parameter beta
        n_accept += 1
        energy = new_energy
        cities = new_cities[:]
        if energy < best_energy:
           best_energy = energy
           best_tour = cities[:]    
           new_route = True
    return cities, beta, n_accept, best_energy, new_route

   
########################################################################
# Main loop:
def mainloop(surface, N, dcities, scities, start_timer):
    # main loop, checks user actions, does simulation step, does graphics
    # output if necessary
    d_energy_min = float('inf')
    s_energy_min = 10000
    running = True
    iters, siters, diters = 0, 0, 0
    start = timeit.default_timer()
    speed = 0
    # parameters for simulated annealing:
    beta = 1.0        # inverse temperature
    n_accept = 0
    # ploting data:
    plot_data = {"direct": {"iters": [], "lengths": []}, "simann": {"iters": [], "lengths": []}}

    # define buttons for user control:
    button_ncity_10 = Button(50, 30, "10", COLORS["LIGHTBLUE"], COLORS["BLACK"])
    button_ncity_20 = Button(50, 30, "20", COLORS["LIGHTBLUE"], COLORS["BLACK"])
    button_ncity_50 = Button(50, 30, "50", COLORS["LIGHTBLUE"], COLORS["BLACK"])
    button_ncity_100 = Button(50, 30, "100", COLORS["LIGHTBLUE"], COLORS["BLACK"])
    button_ncity_200 = Button(50, 30, "200", COLORS["LIGHTBLUE"], COLORS["BLACK"])
    button_ncity_500 = Button(50, 30, "500", COLORS["LIGHTBLUE"], COLORS["BLACK"])
    button_quit = Button(60, 30, "Quit", COLORS["RED"], COLORS["BLACK"])
    button_pause = Button(60, 30, "Pause", COLORS["LIGHTBLUE"], COLORS["BLACK"])
    button_continue = Button(60, 30, "Cont.", COLORS["GREEN"], COLORS["BLACK"])
    button_save = Button(60, 30, "Save", COLORS["LAVENDER"], COLORS["BLACK"])
    button_plot = Button(60, 30, "Plot", COLORS["LAVENDER"], COLORS["BLACK"])

    # loop until user event:
    while True:

        # Event handler:
        for event in pygame.event.get():
            # pygame event handler
            if event.type == QUIT:
                # graphics window is closed
                pygame.quit()
                return
            elif event.type == KEYDOWN:
                # key is pressed
                if event.key in [K_ESCAPE, K_q]:
                    # 'q' or ESC will quit program
                    pygame.quit()
                    return
                elif event.key == K_c:
                    # 'c' continues simulation
                    running = True
                elif event.key == K_p:
                    # 'p' pauses simulation
                    running = False
            elif event.type == MOUSEBUTTONDOWN:
                # mouse button is pressed
                if button_ncity_10.IsPressed(pygame.mouse.get_pos()):
                    # N = 10 selected
                    N, dcities, scities, iters, siters, diters, d_energy_min, s_energy_min, beta, n_accept, start, plot_data = change_N(10)
                elif button_ncity_20.IsPressed(pygame.mouse.get_pos()):
                    # N = 20 selected
                    N, dcities, scities, iters, siters, diters, d_energy_min, s_energy_min, beta, n_accept, start, plot_data = change_N(20)
                elif button_ncity_50.IsPressed(pygame.mouse.get_pos()):
                    # N = 50 selected
                    N, dcities, scities, iters, siters, diters, d_energy_min, s_energy_min, beta, n_accept, start, plot_data = change_N(50)
                elif button_ncity_100.IsPressed(pygame.mouse.get_pos()):
                    # N = 100 selected
                    N, dcities, scities, iters, siters, diters, d_energy_min, s_energy_min, beta, n_accept, start, plot_data = change_N(100)
                elif button_ncity_200.IsPressed(pygame.mouse.get_pos()):
                    # N = 200 selected
                    N, dcities, scities, iters, siters, diters, d_energy_min, s_energy_min, beta, n_accept, start, plot_data = change_N(200)
                elif button_ncity_500.IsPressed(pygame.mouse.get_pos()):
                    # N = 500 selected
                    N, dcities, scities, iters, siters, diters, d_energy_min, s_energy_min, beta, n_accept, start, plot_data = change_N(500)
                elif button_quit.IsPressed(pygame.mouse.get_pos()):
                    # 'Quit' selected
                    if VERBOSE: print "Quitting..."
                    pygame.quit()
                    return
                elif button_continue.IsPressed(pygame.mouse.get_pos()):
                    # 'Continue' selected, simulation continues
                    if VERBOSE: print "Continuing..."
                    running = True
                elif button_pause.IsPressed(pygame.mouse.get_pos()):
                    # 'Pause' selected, simulation is halted
                    if VERBOSE: print "Simulation paused."
                    running = False
                elif button_save.IsPressed(pygame.mouse.get_pos()):
                    # 'Save' selected, image will be saved
                    filename = save_image(surface, N, iters)
                    if VERBOSE: print "Image saved, filename:", filename
                elif button_plot.IsPressed(pygame.mouse.get_pos()):
                    # 'Plot' selected, generate plot of tour length vs iteration
                    filename = make_plot(plot_data, N, iters)
                    if VERBOSE: print "Plot generated, filename:", filename
                                                
        if not running:
            # if simulation is paused, skip rest of mainloop
            continue
        if VERBOSE and iters % 10000 == 0:
            print "N/iters/beta/s_energy_min =", N, iters, beta, round(s_energy_min, 3)
        iters += 1  # iteration counter
        
        change = False
        # generate new route by direct sampling:
        new_dcities = direct_sampling(dcities[:])
        d_energy = tour_length(new_dcities, N)
        if d_energy < d_energy_min:
            d_energy_min = d_energy
            if VERBOSE:
                print "Tour length direct sampling:", d_energy_min, "at iteration", iters
            dcities = new_dcities[:]
            diters = iters
            change = True
            plot_data["direct"]["iters"].append(iters)
            plot_data["direct"]["lengths"].append(d_energy_min)
        # generate new route by simulated annealing:
        new_scities, beta, n_accept, s_energy_min, new_route = simulated_annealing(N, scities[:], beta, n_accept, s_energy_min)
        if new_route:
            if VERBOSE:
                print "Tour length simulated annealing:", s_energy_min, "at iteration", iters
            scities = new_scities[:]
            siters = iters
            change = True
            plot_data["simann"]["iters"].append(iters)
            plot_data["simann"]["lengths"].append(s_energy_min)


        if iters % 1000 == 0:
            # every 1k iterations we will plot current configuration even if
            # it hasn't changed
            change = True
            
        if change:

            # calculate simulation speed:
            delta_iter = 100000 // N
            show_speed = iters % delta_iter == 0
            if show_speed:
                T = timeit.default_timer() - start
                start = timeit.default_timer()
                speed = delta_iter / T
            # only generate graphics output if new route is present for
            # direct sampling and/or simulated annealing or if iteration
            # count is divisible by 1000
            #
            # buttons and text elements:
            surface.fill(COLORS["WHITE"])
            surface.fill(COLORS["LIGHTYELLOW"], (0, 0, 2 * SIZE + DELIM_WIDTH, STATUS_HEIGHT))
            surface.fill(COLORS["DARKBLUE"], (SIZE, STATUS_HEIGHT, DELIM_WIDTH, SIZE + STATUS_HEIGHT2))
            surface.fill(COLORS["DARKBLUE"], (0, STATUS_HEIGHT, DELIM_WIDTH, SIZE + STATUS_HEIGHT2))
            surface.fill(COLORS["DARKBLUE"], (2 * SIZE, STATUS_HEIGHT, DELIM_WIDTH, SIZE + STATUS_HEIGHT2))
            surface.fill(COLORS["DARKBLUE"], (0, SIZE + STATUS_HEIGHT + STATUS_HEIGHT2, 2 * SIZE + DELIM_WIDTH, DELIM_WIDTH))
            surface.fill(COLORS["DARKBLUE"], (0, STATUS_HEIGHT, 2 * SIZE + DELIM_WIDTH, DELIM_WIDTH))
            draw_text(surface, helv24, "https://github.com/RandyWaterhouse/TSP_simulated_annealing", (SIZE // 2, SIZE + STATUS_HEIGHT + STATUS_HEIGHT2 + DELIM_WIDTH + 5), COLORS["DARKGREY"])
            draw_text(surface, helv24, "No of cities:", (110, 10), COLORS["BLACK"])
            draw_text(surface, helv24, str(N), (250, 10), COLORS["BLUE"])
            button_ncity_10.PlaceButton(surface, 10, 40)
            button_ncity_20.PlaceButton(surface, 70, 40)
            button_ncity_50.PlaceButton(surface, 130, 40)
            button_ncity_100.PlaceButton(surface, 190, 40)
            button_ncity_200.PlaceButton(surface, 250, 40)
            button_ncity_500.PlaceButton(surface, 310, 40)
            pygame.draw.line(surface, COLORS["GREY1"], (380, 0), (380, STATUS_HEIGHT), 3)
            draw_text(surface, helv24, "Iterations:", (400, 10), COLORS["BLACK"])
            draw_text(surface, helv24, str(iters // 1000) + " k", (400, 40), COLORS["BLUE"])
            pygame.draw.line(surface, COLORS["GREY1"], (520, 0), (520, STATUS_HEIGHT), 3)
            draw_text(surface, helv24, "Tour Length Ratio:", (540, 10), COLORS["BLACK"])
            draw_text(surface, helv24, str(round(d_energy_min / s_energy_min, 3)), (540, 40), COLORS["BLUE"])
            pygame.draw.line(surface, COLORS["GREY1"], (750, 0), (750, STATUS_HEIGHT), 3)
            draw_text(surface, helv24, "Speed (iters/sec):", (770, 10), COLORS["BLACK"])
            draw_text(surface, helv24, str(int(round(speed, 0))), (770, 40), COLORS["BLUE"])
            pygame.draw.line(surface, COLORS["GREY1"], (2 * SIZE + DELIM_WIDTH - 230, 0), (2 * SIZE + DELIM_WIDTH - 230, STATUS_HEIGHT), 3)
            button_quit.PlaceButton(surface, 2 * SIZE + DELIM_WIDTH - 210, 10)
            button_pause.PlaceButton(surface, 2 * SIZE + DELIM_WIDTH - 210, 45)
            button_continue.PlaceButton(surface, 2 * SIZE + DELIM_WIDTH - 140, 45)
            button_save.PlaceButton(surface, 2 * SIZE + DELIM_WIDTH - 70, 10)
            button_plot.PlaceButton(surface, 2 * SIZE + DELIM_WIDTH - 70, 45)

            # draw cities and roads:
            #
            # direct sampling:
            for i in range(N):
                x1, y1 = dcities[i]
                x2, y2 = dcities[(i+1)%N]
                xi1 = int(SIZE * x1)
                xi2 = int(SIZE * x2)
                yi1 = STATUS_HEIGHT + STATUS_HEIGHT2+ int(SIZE * y1)
                yi2 = STATUS_HEIGHT + STATUS_HEIGHT2 + int(SIZE * y2)
                pygame.draw.line(surface, COLORS["DARKGREY"], [xi1, yi1], [xi2, yi2], 3)
            for x, y in dcities:
                xi = int(SIZE * x)
                yi = STATUS_HEIGHT + STATUS_HEIGHT2 + int(SIZE * y)
                pygame.draw.circle(surface, COLORS["BLUE"], [xi, yi], CITY_RADIUS)
            draw_text(surface, helv24, "Iterations:", (30, STATUS_HEIGHT + 10), COLORS["BLACK"])
            draw_text(surface, helv24, str(diters), (150, STATUS_HEIGHT + 10), COLORS["BLUE"])
            draw_text(surface, helv24, "Min. Tour Length:", (260, STATUS_HEIGHT + 10), COLORS["BLACK"])
            draw_text(surface, helv24, str(round(d_energy_min, 3)), (460, STATUS_HEIGHT + 10), COLORS["BLUE"])
            # simulated annealing:
            for i in range(N):
                x1, y1 = scities[i]
                x2, y2 = scities[(i+1)%N]
                xi1 = SIZE + DELIM_WIDTH + int(SIZE * x1)
                xi2 = SIZE + DELIM_WIDTH + int(SIZE * x2)
                yi1 = STATUS_HEIGHT + STATUS_HEIGHT2 + int(SIZE * y1)
                yi2 = STATUS_HEIGHT + STATUS_HEIGHT2 + int(SIZE * y2)
                pygame.draw.line(surface, COLORS["DARKGREY"], [xi1, yi1], [xi2, yi2], 3)
            for x, y in dcities:
                xi = SIZE + DELIM_WIDTH + int(SIZE * x)
                yi = STATUS_HEIGHT + STATUS_HEIGHT2 + int(SIZE * y)
                pygame.draw.circle(surface, COLORS["BLUE"], [xi, yi], CITY_RADIUS)
            draw_text(surface, helv24, "Iterations:", (SIZE + DELIM_WIDTH + 30, STATUS_HEIGHT + 10), COLORS["BLACK"])
            draw_text(surface, helv24, str(siters), (SIZE + DELIM_WIDTH + 150, STATUS_HEIGHT + 10), COLORS["BLUE"])
            draw_text(surface, helv24, "Min. Tour Length:", (SIZE + DELIM_WIDTH + 260, STATUS_HEIGHT + 10), COLORS["BLACK"])
            draw_text(surface, helv24, str(round(s_energy_min, 3)), (SIZE + DELIM_WIDTH + 460, STATUS_HEIGHT + 10), COLORS["BLUE"])

            # update graphics output:
            pygame.display.flip()
            # wait a moment (SLEEP may be zero):
            time.sleep(SLEEP)
        

# calling "mainloop" will start simulation:
mainloop(surface, N, dcities, scities, start_timer)

