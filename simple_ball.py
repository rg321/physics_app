from kivy.app import App
from kivy.properties import *
from kivy.graphics import *
from kivy.uix.widget import Widget
from transitions import Machine
from kivy.core.window import Window
from kivy.clock import Clock
from functools import partial
from time import time
from helper_functions import unit_vector
from vector import Vector
from kivy.graphics.instructions import *


DELTA = (0.055, 0.055)
INTERVAL = 1.0 / 100.0 # larger D means more calls to function
G_FACTOR = -2

states = ['lying_on_ground', 'in_air', 'back_to_ground']
transitions = [
    {   
        'trigger': 'kick',
        'source': 'lying_on_ground',
        'dest': 'in_air',
        'before': 'store_ball_position',
        'after': 'move_the_ball'
        # 'after': 'move_the_ball',
        # 'conditions': ['is_ball_touched']
    },
    { 
        'trigger': 'collide',
        'source': 'in_air',
        'dest': 'back_to_ground', 
    }
]

class ProjectileGame(Widget):
		ground = ObjectProperty(None)
		ball = ObjectProperty(None)
		platform = ObjectProperty(None)
		arrow = ObjectProperty(None)
		line_instruction = Instruction()
		line_instruction_group = InstructionGroup()

		def save_pos_if_ball_touched(self, *args):
			pos = args[1].pos
			if self.ball.collide_point(*pos):
				self.ball.touch_pos = pos
				print 'ball touched at pos ', args[1].pos

		def show_arrow_if_ball_was_touched(self, *touch):
			ball_touched_at = self.ball.touch_pos
			if ball_touched_at:
				self.draw_arrow(ball_touched_at, touch, self.ball.centre)

		def draw_arrow(self, ball_touched_at, touch, ball_centre):
			present_touch = touch[1].pos
			# print 'touch', touch
			print 'ball_touched_at, present_touch', ball_touched_at, present_touch
			touch_vector = Vector(*present_touch) - Vector(*ball_touched_at)
			print 'touch_vector', touch_vector
			touch_vector_inversed = touch_vector.inverse()
			# touch_vector_inversed = touch_vector
			arrow_length_vector = unit_vector(touch_vector_inversed.norm(), touch_vector_inversed.argument())
			# self.ball.velocity_unit_vector = unit_vector(1, touch_vector_inversed.argument())
			self.ball.velocity_unit_vector = arrow_length_vector
			arrow_ending_vector = arrow_length_vector + ball_centre
			# with self.arrow.canvas:
			print 'drawing arrow', ball_centre, arrow_ending_vector.values
			# print 'touch', touch.ud
			# touch[0].arrow._points = (ball_centre, arrow_ending_vector.values)
			line_points = (ball_centre, arrow_ending_vector.values)
			self.line_instruction = Line(points=line_points, group='arrows')
			# self.line_instruction_group.add(self.line_instruction)
			self.arrow.canvas.clear()
			self.arrow.canvas.add(self.line_instruction)

		def remove_arrow_and_kick_if_ball_was_touched(self, ground, platform, *touch):
			self.ball.touch_pos = ()
			# del(touch[1].ud['arrow'])
			# print str(line_instruction_group)
			# print self.arrow.canvas.children
			# print [x.group for x in self.line_instruction_group.children]
			self.arrow.canvas.clear()
			self.ball.kick(ground, platform, touch)
			# print 'childeren', [x.group for x in self.line_instruction_group.children]
			# print str(self.line_instruction_group)


class Ground(Widget):
	def __init__(self, **kwargs):
		super(Ground, self).__init__(**kwargs)
		self.pos = (0, 0)
		self.size = (Window.width, 20)

class Platform(Widget):
	def __init__(self, **kwargs):
		super(Platform, self).__init__(**kwargs)
		self.pos = (Window.width * (2.3 / 3.0), 20)
		self.size = (20, 20)

class Arrow(Widget):
	def __init__(self, **kwargs):
		super(Arrow, self).__init__(**kwargs)
		self._points = ()

	@property
	def points(self):
		return self._points
		

class Ball(Widget):
	def __init__(self, **kwargs):
		super(Ball, self).__init__(**kwargs)
		self.pos = (50, 50)
		self.size = (50, 50)
		self.machine = Machine(model=self, states=states, transitions=transitions, initial='lying_on_ground')
		self.touched_at = None

	@property
	def centre(self):
		half_size = tuple(x/2.0 for x in self.size)
		return tuple(sum(y) for y in zip(self.pos, half_size))
		
	# def on_touch_down(self, touch):
	# 	self.kicked()
	# 	print '{}'.format('touched down')




	def store_ball_position(self, ground, platform, *args):
		print 'kicked at ', args
		self.start_time = time()

	def is_ball_touched(self, ground, platform, *args):
		print 'CLICKED at ', ground, platform, args[1].pos
		pos = args[1].pos
		# print type(touch)
		return self.collide_point(*pos)

		
	def move_the_ball(self, ground, platform, *args, **event):
		print 'ball moving'
		print 'ball ', self.pos, self.size
		print 'ground ' ,ground.pos, ground.size
		Clock.schedule_interval(partial(self.move_ball_if_possible, ground, platform), INTERVAL)

		# while not self.pos[1] < ground.size[1]:

	def move_ball_if_possible(self, ground, platform, *args):
		print self.pos, ground.size
		print "-----velocity_unit_vector", self.velocity_unit_vector
		delta = tuple(x[0] * x[1] for x in zip(self.velocity_unit_vector, DELTA))
		print "--------delta", delta
		self.pos = tuple(sum(x) for x in zip(self.pos, delta, self.gravity()))
		# print 'collision param', self.collide_widget(ground)
		return not (self.collide_widget(ground) or self.collide_widget(platform))

	def gravity(self):
		return (0, G_FACTOR * (time() - self.start_time))


class PhysicsApp(App):
    def build(self):
        return ProjectileGame()

if __name__ == "__main__":
    app = PhysicsApp().run()
    