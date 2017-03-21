from setuptools import find_packages, setup

import todone


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='todone',
      version=todone.__version__,
      description='Todo list manager and agenda',
      long_description=readme(),
      url='https://github.com/safnuk/todone',
      author='Brad Safnuk',
      author_email='safnuk@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'todone = todone.application:main',
          ]
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "Development Status :: 1 - Planning",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      install_requires=[
          'peewee',
          'python-dateutil',
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)
