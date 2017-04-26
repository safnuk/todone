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
      license='Apache-2.0',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'todone = todone.application:main',
              'todone-server = todone.server:main',
          ]
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: OS Independent",
      ],
      install_requires=[
          'peewee',
          'python-dateutil',
          'websockets'
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)
