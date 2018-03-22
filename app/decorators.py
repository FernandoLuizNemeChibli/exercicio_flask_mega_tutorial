from threading import Thread

def async(function):
	def wrapper(*args,**kwargs):
		thread_object = Thread(
			target=function,
			args=args,
			kwargs=kwargs
		)
		thread_object.start()
	return wrapper
