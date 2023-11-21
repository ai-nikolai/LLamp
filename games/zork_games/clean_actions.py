def clean_word(word):
	"""removes > and new space"""
	out_word = ""

	for letter in word:
		if letter.isalnum():
			out_word += letter

	return out_word



if __name__=="__main__":
	unique_actions = set()
	unique_words = set()
	FILE_PATH = "zork/gold_path.txt"
	with open(FILE_PATH, "r") as file:
		for line in file.readlines():
			unique_words |= set([word for word in line.split(" ")])

	# print(unique_words)

	for word in unique_words:
		if word.startswith(">"):
			unique_actions |= set([clean_word(word)])

	print(unique_actions)
	# print(unique_words - unique_actions)
