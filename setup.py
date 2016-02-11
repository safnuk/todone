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
      setup_requires=['pytest-runner',],
      test_require=['pytest',],
      include_package_data=True,
      zip_safe=False)
