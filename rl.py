import numpy as np

import random



class pegEnv():

	def __init__(self):

		self.state = (0,0,0,0,0,0,0)		

		self.valTab = (1,2,3,4,5,6,7,8,9,10,10,10,10)

	

	def step(self, action):

		return self._take_action(action)



	def _take_action(self, action):

		reward = self.reward(self.state, action)

		self.state = self.updateState(action)

		#done = (state[6] == 1 or state[6] == 2 or state[6] == 4 or state[6] == 8)

		done = (self.state[6] <= 0)

		return self.state, reward, done



	def reset(self):

		temp = [0,0,0,0,0,0,0]

		for i in range(5):

			temp[i] = random.randint(0, 12)

		temp[5] = random.randint(0, 30)

		temp[6] = random.randint(1, 15)

		self.state = tuple(temp)

		return self.state

		

	def reward(self, state, action):

		reward = 0

		if state[action] == state[4]:

			reward += 2



		if state[5] + self.valTab[state[action]] == 15:

			reward += 2



		if state[5] + self.valTab[state[action]] == 31:

			reward += 2



		return reward



	def updateState(self, action):

		temp = list(self.state)

		temp[6] -= 2 ** action

		self.state = tuple(temp)

		return self.state



	def sample_action(self):

		return random.randint(0, 3)



	def isValidAction(self, action):

		if action == 3 and ((self.state[6] >> 3) % 2 == 0):

			return False

		if action == 2 and ((self.state[6] >> 2) % 2 == 0):

			return False

		if action == 1 and ((self.state[6] >> 1) % 2 == 0):

			return False

		if action == 0 and (self.state[6] % 2 == 0):

			return False

		return True



def main():

	random.seed()

	env = pegEnv()

	Q = train_agent(env)

	np.save("q.csv", Q)



def train_agent(env):

	Q = np.zeros((13,13,13,13,13,31, 16, 4))

	alpha = 0.5

	epsilon = 0.1



	lick = 0

	lol = 0

	for index, x in np.ndenumerate(Q):

		lick += 1

		if (lick % 100000 == 0):

			print(lol)

			lol += 1

		temp1 = list(index)

		temp1.pop(7)

		if (temp1[6] == 0):

			continue





		for i in range(1, 10):

			state = env.reset()

			state = tuple(temp1)

			#print('state: ', state)



			epochs, penalites, reward, = 0,0,0

			done = False

			while not done:

				#make sure action is valid

				if random.uniform(0, 1) < epsilon:

					action = env.sample_action()

				else:

					action = np.argmax(Q[state])



				while not env.isValidAction(action):

					if action == 3:

						action = 0

					else:

						action += 1

					

				#print(action)

			

				next_state, reward, done = env.step(action)



				temp = list(state)

				temp.append(action)

				temp = tuple(temp)



				old_value = Q[temp]

				#print('nextState: ', next_state)

				next_max = np.max(Q[next_state])



				new_value = (1 - alpha) * old_value + alpha * (reward + next_max)

				Q[temp] = new_value



				state = next_state



	print("Training finished.\n")

	return Q



if __name__ == "__main__":

	main()
