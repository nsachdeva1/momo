# Basic slash command that simply returns the input
class Slash():

  def __init__(self, message):
    self.msg = message

  def getMessage(self):
      return self.msg
