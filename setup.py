from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='todone',
      version='0.01',
      description='Todo list manager and agenda',
      long_description=readme(),
      url='https://bitbucket.org/safnuk/todone',
      author='Brad Safnuk',
      author_email='safnuk@gmail.com',
      license='MIT',
      packages=['todone'],
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'todone = todone.application:main',
          ]
      },
      classifiers = [
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Development Status :: 1 - Planning",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      install_requires = [
          'peewee',
          'python-dateutil',
      ],
      zip_safe=False)
