import pymunk
import neat
import pygame
from pymunk.vec2d import Vec2d
import random
import math

# Global Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
AGENT_RADIUS = 10
POLE_LENGTH = 50
SHOW_VISUAL = True  # Toggle this for visual representation

pygame.init()
if SHOW_VISUAL:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

space = pymunk.Space()
space.gravity = (0.0, 900.0)
space.damping = 0.8  # Damping

def draw_boxes_and_ground():
    for i in range(1, 3):
        pygame.draw.line(screen, (0, 0, 0), (i*SCREEN_WIDTH//3, 0), (i*SCREEN_WIDTH//3, SCREEN_HEIGHT), 2)
    for i in range(1, 3):
        pygame.draw.line(screen, (0, 0, 0), (0, i*SCREEN_HEIGHT//3), (SCREEN_WIDTH, i*SCREEN_HEIGHT//3), 2)

def draw_fitness(fitness, i, j):
    font = pygame.font.SysFont(None, 25)
    text = font.render(f"Fitness: {round(fitness, 2)}", True, (0,0,0))
    screen.blit(text, (i * SCREEN_WIDTH/3 + 10, j * SCREEN_HEIGHT/3 + 5))

def create_agent_and_pole(i, j):
    initial_x = i * SCREEN_WIDTH/3 + SCREEN_WIDTH/6
    initial_y = j * SCREEN_HEIGHT/3 + SCREEN_HEIGHT/6 - AGENT_RADIUS - 5
    
    # Create agent body
    body = pymunk.Body(10, pymunk.moment_for_circle(10, 0, AGENT_RADIUS, (0,0)))
    body.position = initial_x, initial_y
    shape = pymunk.Circle(body, AGENT_RADIUS)
    space.add(body, shape)
    
    # Adjusting pole position so that its top is attached to the agent
    pole_body = pymunk.Body(1, pymunk.moment_for_segment(10, (0, 0), (0, -POLE_LENGTH), 5))  # Adjusted moment
    pole_body.position = initial_x, initial_y - AGENT_RADIUS
    pole_body.angle = random.uniform(-0.1, 0.1)  
    pole_shape = pymunk.Segment(pole_body, (0, 0), (0, -POLE_LENGTH), 5)
    pole_shape.elasticity = 0.0
    space.add(pole_body, pole_shape)
    
    # Create joint between agent and pole
    pivot = pymunk.PivotJoint(body, pole_body, (0, -AGENT_RADIUS), (0, 0))
    space.add(pivot)
    
    return body, pole_body

def create_box_boundaries():
    box_boundaries = []
    for i in range(4):  # For the 4 vertical boundaries
        boundary_start = (i * SCREEN_WIDTH//3, 0)
        boundary_end = (i * SCREEN_WIDTH//3, SCREEN_HEIGHT)
        boundary = pymunk.Segment(space.static_body, boundary_start, boundary_end, 1)
        boundary.elasticity = 1
        space.add(boundary)
        box_boundaries.append(boundary)
    
    for i in range(3):  # For the 3 horizontal boundaries
        for j in range(4):  # 4 segments in each horizontal boundary
            boundary_start = (i * SCREEN_WIDTH//3, j * SCREEN_HEIGHT//3)
            boundary_end = ((i+1) * SCREEN_WIDTH//3, j * SCREEN_HEIGHT//3)
            boundary = pymunk.Segment(space.static_body, boundary_start, boundary_end, 1)
            boundary.elasticity = 1
            space.add(boundary)
            box_boundaries.append(boundary)
    
    return box_boundaries

def draw_agent_and_pole(agent, pole):
    # The pole's top end should be the agent's position minus the agent's radius
    pole_start = (int(agent.position.x), int(agent.position.y - AGENT_RADIUS))

    # Calculate pole's bottom end based on its angle
    pole_end = (int(pole_start[0] + math.sin(pole.angle) * POLE_LENGTH), int(pole_start[1] - math.cos(pole.angle) * POLE_LENGTH))
    
    pygame.draw.circle(screen, (255, 0, 0), (int(agent.position.x), int(agent.position.y)), AGENT_RADIUS)
    pygame.draw.line(screen, (0, 255, 0), pole_start, pole_end, 5)

def eval_genomes(genomes, config):
    # Create box boundaries first
    create_box_boundaries()
    nets = []
    agents = []
    poles = []

    for _, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
    
    for i in range(3):
        for j in range(3):
            agent, pole = create_agent_and_pole(i, j)
            agents.append(agent)
            poles.append(pole)

    start_time = pygame.time.get_ticks()

    while (pygame.time.get_ticks() - start_time) < 5000:  # 5 seconds
        if SHOW_VISUAL:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            screen.fill((255,255,255))
            draw_boxes_and_ground()

        for x, agent in enumerate(agents):
            output = nets[x].activate((poles[x].angle, poles[x].angular_velocity, agent.velocity.x))
            
            if output[0] > 0.5:
                agent.apply_impulse_at_local_point(Vec2d(20, 0))
            elif output[0] < -0.5:
                agent.apply_impulse_at_local_point(Vec2d(-20, 0))

            genomes[x][1].fitness += 0.1

            if abs(poles[x].angle) > 1.5:
                genomes[x][1].fitness -= 10

            # Check if pole's angle exceeds limit to detach from AI
            if abs(poles[x].angle) > math.radians(45):  # Adjust the value as needed
                for constraint in space.constraints:
                    if isinstance(constraint, pymunk.PivotJoint) and (constraint.a == agent or constraint.b == agent):
                        space.remove(constraint)

            if SHOW_VISUAL:
                draw_agent_and_pole(agent, poles[x])
                i, j = x // 3, x % 3
                draw_fitness(genomes[x][1].fitness, i, j)

        for _ in range(10):
            space.step(1/600.0)

        if SHOW_VISUAL:
            pygame.display.flip()
            clock.tick(60)

# Run the simulation
config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'config-feedforward')
p = neat.Population(config)
p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)
winner = p.run(eval_genomes)