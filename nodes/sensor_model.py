import math
import prob_utilities as prob_util
import scipy.stats

"""
Key assumptions:
	- Everyone needs to agree on Theta in robot's pose
	- Pose X_t is in grid coordinates
	- Will have access to a nearest neighbor funtion that returns the nearest (euclidean dist) occupied grid space given a grid space.
		- get_dist_to_nearest_occupied((x, y)) 
			- this function should also take a parameter that defines the local area around (x, y) to search 
	- Grid cells are either occuppied, free, or unknown (it is very important that unknown grid cells are marked as such)
	- Assume rangefinder shares x,y location of robot pose 
"""

class SensorModelSimple(object):

	def __init__(self, stddev = 2.5, beam_width = .04):
		self.stddev = stddev
		self.beam_width = beam_width

	'''
	update
		params:
		  - z_t: sensor readings (Laser_Scan())
		  - pose (x_t): robot pose
		  - m: map
		return: importance weight
		note: importance weight is a belief in the current sensor reading given the pose and the map
	'''
	def update(self, z_t, pose, m):
		#TODO: probably don't want to use all range scans
		result = 1.0
		cur_angle = z_t.angle_min 				#store current angle in radians
		inc_angle = z_t.angle_increment 		#angle increment between scans in radians
		range_max = z_t.range_max
		for i in xrange(0, len(z_t.ranges)):
			#get the expected distance to obstacle
			expected_distance = m.rayTrace((pose.x, pose.y), cur_angle + pose.theta)
			result *= self.getProbReadingGivenDistance(z_t.ranges[i], expected_distance, range_max)
			cur_angle += inc_angle
		return result

	def getProbReadingGivenDistance(self, sensor_distance = 0, expected_distance = 0, max_distance = 0):
		#alpha is 1.0 divided by the area of the normal curve that is to the right of 0.0
		#Basically, it is the renormalization constant.
		alpha = 1.0/(1.0 - prob_util.getCND(0.0, expected_distance, self.stddev))
	    beta = 1.0 - prob_util.getCND(max_distance, true_distance, stddev) #probability of max range
    	if (sensor_distance >= max_distance):
     	    return beta
		return alpha * prob_util.getProbND(sensor_distance, expected_distance, self.stddev)

	def update_map(self, z_t, pose, m):
		cur_angle = z_t.angle_min 				#store current angle in radians
		inc_angle = z_t.angle_increment 		#angle increment between scans in radians
		range_max = z_t.range_max

		
		for r in z_t.ranges:
			#Discard any infinite readings
			if r != "inf":
				# For each reading, mark cell being sensed and all cells in an arc around it as occupied
				init_angle = cur_angle + pose.theta - self.beam_width/2.0
				end angle = cur_angle + pose.theta + self.beam_width/2.0
				step = math.atan2(m.step, r) #This ensures that the width of each step is never greater than the grid size
				while init_angle <= end_angle:
					point_x = r * math.cos(init_angle) + pose.x
					point_y = r * math.sin(init_angle) + pose.y
					#Clear all points up to the sensed point, then set the sensed point to occupied
					m.clearTo((pose.x, pose.y), (point_x, point_y))
					m[point_x][point_y] = True
					init_angle += step

			cur_angle += inc_angle
		return m