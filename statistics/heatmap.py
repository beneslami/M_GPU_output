import matplotlib.pyplot as plt
import seaborn as sn
if __name__ == '__main__':
	data1 = [
		[0.000, 0.046, 0.418, 0.535],
		[0.053, 0.000, 0.279, 0.667],
		[0.007, 0.164, 0.000, 0.827],
		[0.098, 0.108, 0.793, 0.000]
	]

	data2 = [
		[0.000, 0.047, 0.417, 0.536],
		[0.052, 0.000, 0.279, 0.669],
		[0.008, 0.165, 0.000, 0.827],
		[0.100, 0.108, 0.792, 0.000]
	]

	fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(20, 20))
	fig.subplots_adjust(wspace=0.01)
	sn.heatmap(data1, cmap="hot", ax=ax1, cbar=True, linewidth=.3, annot=True)
	sn.heatmap(data2, cmap="hot", ax=ax2, cbar=True, linewidth=.3, annot=True)
	ax1.set_title("AccelSim Traffic Pattern") # AccelSim link usage (Byte/Cycle)      AccelSim Traffic Pattern
	ax2.set_title("BookSim Traffic Pattern") # BookSim link usage (Byte/Cycle)       BookSim Traffic Pattern
	ax2.yaxis.tick_right()

	fig.subplots_adjust(wspace=0.1)
	plt.show()