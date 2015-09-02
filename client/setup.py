import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


setup(name='rpio-client',
      version='1.0',
      description='Client for rpio-server',
      long_description=README,
      classifiers=[
          "License :: OSI Approved :: BSD License",
          "Operating System :: POSIX",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: System :: Networking",
      ],
      author='Alexander Zelenyak aka ZZZ',
      author_email='zzz.sochi@gmail.com',
      url='https://github.com/zzzsochi/rpio-server/client',
      keywords=['gpio', 'rpi', 'raspberry', 'raspberrypi', 'go'],
      py_modules=['rpio_client'],
      )
