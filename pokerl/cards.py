class Card:
	"""  """

	@property
	def rank(self) -> int:
		"""  """

		return (self.value & 0xf) or 13 # Make ace highest rank
	
	@property
	def suit(self) -> int:
		"""  """

		return self.value >> 4
	
	def __init__(self, value: int):
		"""  """

		assert value >> 4 in range(4)
		assert value & 0xf < 0xf

		self.value = value
	
	def __repr__(self) -> str:
		"""  """
		
		return chr(0x1f0a1 + self.value)